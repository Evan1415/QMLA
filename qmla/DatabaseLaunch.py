from __future__ import print_function  # so print doesn't show brackets

import numpy as np
import itertools as itr
import copy
import os as os
import sys as sys
import pandas as pd
import warnings
import hashlib

import redis
from qinfer import NormalDistribution

from qmla.QML import ModelLearningClass, reducedModel
from qmla.DataBase import * 

def launch_db(
    true_op_name,
    new_model_branches,
    new_model_ids,
    log_file,
    RootN_Qbit=[0],
    N_Qubits=1,
    gen_list=[],
    true_ops=[],
    true_params=[],
    num_particles=1000,
    qle=True,
    redimensionalise=True,
    resample_threshold=0.5,
    resampler_a=0.95,
    pgh_prefactor=1.0,
    num_probes=None,
    probe_dict=None,
    use_exp_custom=True,
    enable_sparse=True,
    debug_directory=None,
    qid=0,
    host_name='localhost',
    port_number=6379
):
    """
    Inputs:
    TODO
    RootN_Qbit: TODO
    N_Qubits: TODO
    gen_list: list of strings corresponding to model names.

    Outputs:
      - db: "running database", info on active models. Can access QML and
        operator instances for all information about models.
      - legacy_db: when a model is terminated, we maintain essential information
        in this db (for plotting, debugging etc.).
      - model_lists = list of lists containing alphabetised model names.
        When a new model is considered, it

    Usage:
        $ gen_list = ['xTy, yPz, iTxTTy] # Sample list of model names
        $ running_db, legacy_db, model_lists = DataBase.launch_db(gen_list=gen_list)

    """

    Max_N_Qubits = 13
    model_lists = {}
    for j in range(1, Max_N_Qubits):
        model_lists[j] = []

    legacy_db = pd.DataFrame({
        '<Name>': [],
        'Param_Est_Final': [],
        'Epoch_Start': [],
        'Epoch_Finish': [],
        'ModelID': [],
    })

    db = pd.DataFrame({
        '<Name>': [],
        'Status': [],  # TODO can get rid?
        'Completed': [],  # TODO what's this for?
        'branchID': [],  # TODO proper branch id's,
        # 'Param_Estimates' : sim_ops,
        # 'Estimates_Dist_Width' : [normal_dist_width for gen in generators],
        # 'Model_Class_Instance' : [],
        'Reduced_Model_Class_Instance': [],
        'Operator_Instance': [],
        'Epoch_Start': [],
        'ModelID': [],
    })

    modelID = int(0)

    gen_list = list(new_model_branches.keys())

    for model_name in gen_list:
        try_add_model = add_model(
            model_name=model_name,
            branchID=new_model_branches[model_name],
            modelID=int(new_model_ids[model_name]),
            running_database=db,
            model_lists=model_lists,
            true_op_name=true_op_name,
            true_ops=true_ops,
            true_params=true_params,
            log_file=log_file,
            epoch=0,
            probe_dict=probe_dict,
            resample_threshold=resample_threshold,
            resampler_a=resampler_a,
            pgh_prefactor=pgh_prefactor,
            num_probes=num_probes,
            num_particles=num_particles,
            redimensionalise=redimensionalise,
            use_exp_custom=use_exp_custom,
            enable_sparse=enable_sparse,
            debug_directory=debug_directory,
            # branchID=0,
            qle=qle,
            qid=qid,
            host_name=host_name,
            port_number=port_number
        )
        if try_add_model is True:
            modelID += int(1)

    return db, legacy_db, model_lists


def add_model(
    model_name,
    running_database,
    model_lists,
    true_op_name,
    modelID,
    log_file,
    redimensionalise=True,
    num_particles=2000,
    branchID=0,
    epoch=0,
    true_ops=[],
    true_params=[],
    use_exp_custom=True,
    enable_sparse=True,
    probe_dict=None,
    resample_threshold=0.5,
    resampler_a=0.95,
    pgh_prefactor=1.0,
    num_probes=None,
    debug_directory=None,
    qle=True,
    qid=0,
    host_name='localhost',
    port_number=6379,
    force_create_model=False,
):
    """
    Function to add a model to the existing databases.
    First checks whether the model already exists.
    If so, does not add model to databases.
      TODO: do we want to return False in this case and use as a check in QMD?

    Inputs:
      - model_name: new model name to be considered and added if new.
      - running_database: Database (output of launch_db) containing
        info on log likelihood etc.
      - model_lists: output of launch_db. A list of lists containing
        every previously considered model, categorised by dimension.

    Outputs:
      TODO: return True if added; False if previously considered?

    Effect:
      - If model hasn't been considered before,
          Adds a row to running_database containing all columns of those.
    """

    # Fix dimensions if model and true model are of different starting
    # dimension.
    modelID = int(modelID)
    alph_model_name = alph(model_name)
    model_num_qubits = get_num_qubits(model_name)

    if (
        consider_new_model(model_lists, model_name, running_database) == 'New'
        or
        force_create_model == True
    ):
        model_lists[model_num_qubits].append(alph_model_name)

        if redimensionalise:
            import ModelGeneration
            print("Redimensionalising")
            true_dim = int(np.log2(np.shape(true_ops[0])[0]))
            sim_dim = get_num_qubits(model_name)

            if sim_dim > true_dim:
                true_params = [true_params[0]]
                redimensionalised_true_op = (
                    ModelGeneration.identity_interact(subsystem=true_op_name,
                                                      num_qubits=sim_dim, return_operator=True)
                )
                true_ops = redimensionalised_true_op.constituents_operators
                sim_name = model_name

            elif true_dim > sim_dim:
                print("Before dimensionalising name. Name = ",
                      model_name, "true_dim = ", true_dim
                      )
                sim_name = (
                    ModelGeneration.dimensionalise_name_by_name(name=model_name,
                                                                true_dim=true_dim)
                )
            else:
                sim_name = model_name

        else:
            sim_name = model_name

        log_print(
            [
                "Model ", model_name,
                " not previously considered -- adding.",
                "ID:", modelID
            ],
            log_file
        )
        op = operator(name=sim_name, undimensionalised_name=model_name)
        num_rows = len(running_database)
        qml_instance = ModelLearningClass(
            name=op.name,
            num_probes=num_probes,
            # probe_dict = probe_dict,
            # sim_probe_dict = sim_probe_dict,
        )
        sim_pars = []
        num_pars = op.num_constituents
        # if num_pars ==1 : #TODO Remove this fixing the prior
        #   normal_dist = NormalDistribution(
        #     mean=true_params[0],
        #     var=0.1
        # )
        # else:
        #   normal_dist = MultiVariateNormalDistributionNocov(num_pars)

        # for j in range(op.num_constituents):
        #   sim_pars.append(normal_dist.sample()[0,0])

        # add model_db_new_row to model_db and running_database
        # Note: do NOT use pd.df.append() as this copies total DB,
        # appends and returns copy.

        reduced_qml_instance = reducedModel(
            model_name=model_name,
            sim_oplist=op.constituents_operators,
            true_oplist=true_ops,
            true_params=true_params,
            modelID=int(modelID),
            # numparticles = num_particles,
            # resample_thresh = resample_threshold,
            # resample_a = resampler_a,
            # qle = qle,
            qid=qid,
            host_name=host_name,
            port_number=port_number,
            log_file=log_file
        )

        # Add to running_database, same columns as initial gen_list

        running_db_new_row = pd.Series({
            '<Name>': model_name,
            'Status': 'Active',  # TODO
            'Completed': False,
            'branchID': int(branchID),  # TODO make argument of add_model fnc,
            # 'Param_Estimates' : sim_pars,
            # 'Estimates_Dist_Width' : normal_dist_width,
            'Reduced_Model_Class_Instance': reduced_qml_instance,
            'Operator_Instance': op,
            'Epoch_Start': 0,  # TODO fill in
            # needs to be unique for each model
            'ModelID': int(float(modelID)),
        })

        running_database.loc[num_rows] = running_db_new_row
        return True
    else:
        log_print(
            [
                "Model",
                alph_model_name,
                " previously considered."
            ],
            log_file
        )
        return False
