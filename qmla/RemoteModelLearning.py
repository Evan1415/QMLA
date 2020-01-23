from __future__ import print_function  # so print doesn't show brackets
# Libraries
import DataBase
from qinfer import NormalDistribution
import QML
import matplotlib.pyplot as plt
import matplotlib
import copy
import numpy as np
import itertools as itr
import os as os
import sys as sys
import pandas as pd
import warnings
# warnings.filterwarnings("ignore")
import time as time
import random
from psutil import virtual_memory
import json  # possibly worth a different serialization if pickle is very slow
import pickle
pickle.HIGHEST_PROTOCOL = 2

try:
    import redis
    import RedisSettings as rds
    enforce_serial = False
except BaseException:
    enforce_serial = True  # shouldn't be needed

plt.switch_backend('agg')

# Local files
# import Evo as evo
# from QML import *
# import ModelGeneration
#import BayesF
# from Distrib import MultiVariateNormalDistributionNocov


def time_seconds():
    import datetime
    now = datetime.date.today()
    hour = datetime.datetime.now().hour
    minute = datetime.datetime.now().minute
    second = datetime.datetime.now().second
    time = str(str(hour) + ':' + str(minute) + ':' + str(second))
    return time


# Single function call, given QMDInfo and a name, to learn model entirely.

def learnModelRemote(
    name,
    modelID,
    branchID,
    growth_generator,
    qmd_info=None,
    remote=False,
    host_name='localhost',
    port_number=6379,
    qid=0,
    log_file='rq_output.log'
):
    """
    This is a standalone function to perform QHL on individual
    models  without knowledge of full QMD program.
    QMD info is unpickled from a redis databse, containing
    true operator, params etc.
    Given model names are used to generate ModelLearningClass instances,
    upon which we update the posterior parameter distribution iteratively.
    Once parameters are learned, we pickle the results to dictionaries
    held on a redis database which can be accessed by other actors.

    """

    print("QHL", modelID, ":", name)
    time_start = time.time()
    # Get params from qmd_info
    rds_dbs = rds.databases_from_qmd_id(host_name, port_number, qid)
    qmd_info_db = rds_dbs['qmd_info_db']
    learned_models_info = rds_dbs['learned_models_info']
    learned_models_ids = rds_dbs['learned_models_ids']
    active_branches_learning_models = rds_dbs['active_branches_learning_models']
    any_job_failed_db = rds_dbs['any_job_failed']

    def log_print(to_print_list):
        identifier = str(
            str(time_seconds()) +
            " [RQ Learn " + str(modelID) + "]"
        )
        if not isinstance(to_print_list, list):
            to_print_list = list(to_print_list)

        print_strings = [str(s) for s in to_print_list]
        to_print = " ".join(print_strings)

        with open(log_file, 'a') as write_log_file:
            print(identifier, str(to_print), file=write_log_file,
                  flush=True
                  )

    if qmd_info is None:
        qmd_info = pickle.loads(qmd_info_db['QMDInfo'])
        probe_dict = pickle.loads(qmd_info_db['ProbeDict'])
    else:  # if in serial, qmd_info given, with probe_dict included in it.
        probe_dict = qmd_info['probe_dict']

    true_ops = qmd_info['true_oplist']
    true_params = qmd_info['true_params']
    num_particles = qmd_info['num_particles']
    num_experiments = qmd_info['num_experiments']
    base_resources = qmd_info['base_resources']
    base_num_qubits = base_resources['num_qubits']
    base_num_terms = base_resources['num_terms']

    resampler_threshold = qmd_info['resampler_thresh']
    resampler_a = qmd_info['resampler_a']
    pgh_prefactor = qmd_info['pgh_prefactor']
    debug_directory = qmd_info['debug_directory']
    qle = qmd_info['qle']
    num_probes = qmd_info['num_probes']
    sigma_threshold = qmd_info['sigma_threshold']
    gaussian = qmd_info['gaussian']
    store_particles_weights = qmd_info['store_particles_weights']
    qhl_plots = qmd_info['qhl_plots']
    results_directory = qmd_info['results_directory']
    plots_directory = qmd_info['plots_directory']
    long_id = qmd_info['long_id']
#    use_time_dep_true_params = qmd_info['use_time_dep_true_params']
#    time_dep_true_params = qmd_info['time_dep_true_params']

#    log_print(['Name:', name])
#    log_print(['true ops:\n', true_ops])
#    log_print(["true params:", true_params])

    # Generate model and learn
    op = DataBase.operator(name=name)
    qml_instance = QML.ModelLearningClass(
        name=name,
        num_probes=num_probes,
        probe_dict=probe_dict,
        qid=qid,
        log_file=log_file,
        modelID=modelID
    )

    # random_sim_pars=False
    # if random_sim_pars==True:
    #     sim_pars = []
    #     num_pars = op.num_constituents
    #     if num_pars ==1 : #TODO Remove this fixing the prior
    #         normal_dist=NormalDistribution(mean=true_params[0], var=0.1)
    #     else:
    #         normal_dist = MultiVariateNormalDistributionNocov(num_pars)

    # else:

    model_priors = qmd_info['model_priors']
    if (
        model_priors is not None
        and
        DataBase.alph(name) in list(model_priors.keys())
    ):
        prior_specific_terms = model_priors[name]
    else:
        prior_specific_terms = qmd_info['prior_specific_terms']

    sim_pars = []
    constituent_terms = DataBase.get_constituent_names_from_name(name)
    for term in op.constituents_names:
        try:
            initial_prior_centre = prior_specific_terms[term][0]
            sim_pars.append(initial_prior_centre)
        except BaseException:
            # if prior not defined, start from 0 for all other params
            initial_prior_centre = 0
            sim_pars.append(initial_prior_centre)

    # add model_db_new_row to model_db and running_database
    # Note: do NOT use pd.df.append() as this copies total DB,
    # appends and returns copy.
    qml_instance.InitialiseNewModel(
        trueoplist=true_ops,
        modeltrueparams=true_params,
        simoplist=op.constituents_operators,
        simparams=[sim_pars],
        simopnames=op.constituents_names,
        numparticles=num_particles,
        growth_generator=growth_generator,
        use_exp_custom=True,
        enable_sparse=True,
        modelID=modelID,
        resample_thresh=resampler_threshold,
        resampler_a=resampler_a,
        pgh_prefactor=pgh_prefactor,
        gaussian=gaussian,
        debug_directory=debug_directory,
        qle=qle,
        host_name=host_name,
        port_number=port_number,
        qid=qid,
        log_file=log_file,
        #      use_time_dep_true_params = use_time_dep_true_params,
        #      time_dep_true_params = time_dep_true_params
    )
    log_print(
        [
            "Time to unpickle and initialise QML class: {}".format(
                time.time() - time_start
            )
        ]
    )
    log_print(["Updating model."])
    try:
        update_timer_start = time.time()
        qml_instance.UpdateModel(
            n_experiments=num_experiments,
            sigma_threshold=sigma_threshold
        )
        log_print(
            [
                "Time for update alone: {}".format(
                    time.time() - update_timer_start
                )
            ]
        )
    except NameError:
        log_print(
            [
                "QHL failed for model id {}. Setting job failure database.".format(
                    modelID)
            ]
        )
        any_job_failed_db.set('Status', 1)
    except BaseException:
        log_print(
            [
                "QHL failed for model id {}. Setting job failure database.".format(
                    modelID)
            ]
        )
        any_job_failed_db.set('Status', 1)
        # raise
        # sys.exit()

    if qhl_plots:
        log_print(["Drawing plots for QHL"])

        # with (
        #     open(
        #         str(
        #             "{}/plots/qmd_{}_qml_{}.p".format(
        #                 results_directory,
        #                 qid,
        #                 modelID
        #             )
        #         ),
        #         "wb"
        #     )
        # ) as pkl_file:
        #     pickle.dump(qml_instance, pkl_file , protocol=2)

        try:
            if len(true_ops) == 1:  # TODO buggy
                qml_instance.plotDistributionProgression(
                    save_to_file=str(
                        plots_directory
                        + 'qhl_distribution_progression_' + str(long_id) + '.png')
                )

                qml_instance.plotDistributionProgression(
                    renormalise=False,
                    save_to_file=str(
                        plots_directory
                        + 'qhl_distribution_progression_uniform_' + str(long_id) + '.png')
                )
        except BaseException:
            pass
    updated_model_info = copy.deepcopy(
        qml_instance.learned_info_dict()
    )

    del qml_instance

    compressed_info = pickle.dumps(
        updated_model_info,
        protocol=2
    )
    # TODO is there a way to use higher protocol when using python3 for faster
    # pickling? this seems to need to be decoded using encoding='latin1'....
    # not entirely clear why this encoding is used
    try:
        learned_models_info.set(
            str(modelID),
            compressed_info
        )
        log_print(
            [
                "Redis learned_models_info added to db for model:",
                str(modelID)
            ]
        )
    except BaseException:
        log_print(
            [
                "Failed to add learned_models_info for model:",
                modelID
            ]
        )
    active_branches_learning_models.incr(int(branchID), 1)
    time_end = time.time()
    log_print(["Redis SET learned_models_ids:", modelID, "; set True"])
    learned_models_ids.set(str(modelID), 1)

    if remote:
        del updated_model_info
        del compressed_info
        log_print(["Learned. rq time:", str(time_end - time_start)])
        return None
    else:
        return updated_model_info
