import copy
import pickle
import random
import time as time
import numpy as np
import os as os
import pandas as pd

import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

import qmla.construct_models as construct_models
import qmla.model_for_comparison
import qmla.logging
import qmla.redis_settings as rds
import redis

pickle.HIGHEST_PROTOCOL = 4
plt.switch_backend('agg')


__all__ = [
    'remote_bayes_factor_calculation'
]


def remote_bayes_factor_calculation(
    model_a_id,
    model_b_id,
    branch_id=None,
    num_times_to_use='all',
    bf_data_folder=None,
    times_record='BayesFactorsTimes.txt',
    check_db=False,
    bayes_threshold=1,
    host_name='localhost',
    port_number=6379,
    qid=0,
    log_file='rq_output.log'
):
    r"""
    Standalone function to compute Bayes factors.

    Used in conjunction with redis databases so this calculation can be
    performed without any knowledge other than model IDs.
    Data is unpickled from a redis databse, containing
    `learned_model` information, i.e. final parameters etc.
    Given `model_id`s correspond to model names in the database, which are combined
    with the final learned parameters to reconstruct model classes of
    complete learned models.
    Each model had been trained on a given set of experimental parmaeters (times).
    The reconstructed model classes are updated according to the experimental parameters
    of the opponent model, such that both models have underwent the same experiments.
    From these we extract log likelihoods to compute the Bayes factor, BF(A,B).
    Models have a unique pair_id, simply (min(A,B), max(A,B)).
    For BF(A,B) >> 1, A is deemed the winner; BF(A,B)<<1 deems B the winner.
    The result is then stored redis databases:
        - bayes_factors_db: BF(A,B)
        - bayes_factors_winners_db: id of winning model
        - active_branches_bayes: when complete, increase the count of
          complete pairs' BF on the given branch.

    :param int model_a_id: unique id for model A
    :param int model_b_id: unique id for model B
    :param int branch_id: unique id of branch the pair (A,B) are on
    :param str or int num_times_to_use: how many times, used during the training of
        models A,B, to use during the BF calculation. Default 'all'; if
        otherwise, Nt, keeps the most recent Nt experiment times of A,B.
    :param str bf_data_folder: folder path to store information such as times
        used during calculation, and plots of posterior marginals.
    :param str times_record: filename to store times used during calculation.
    :param bool check_db: look in redis databases to check if this pair's BF
        has already been computed; return pre-computed BF if so.
    :param float bayes_threshold: value to determine whether either model is superior
        enough to "win" the comparison. If 1 < BF < threshold, neither win.
    :param str host_name: name of host server on which redis database exists.
    :param int port_number: this QMLA instance's unique port number,
        on which redis database exists.
    :param int qid: QMLA id, unique to a single instance within a run.
        Used to identify the redis database corresponding to this instance.
    :param str log_file: Path of the log file.
    """

    def log_print(to_print_list):
        qmla.logging.print_to_log(
            to_print_list=to_print_list,
            log_file=log_file,
            log_identifier='BF ({}/{})'.format(model_a_id, model_b_id)
        )
    log_print(["BF Start on branch", branch_id])
    log_print(["num experiments to use for BF=", num_times_to_use])
    time_start = time.time()

    # Access databases
    redis_databases = rds.get_redis_databases_by_qmla_id(
        host_name, port_number, qid)
    qmla_core_info_database = redis_databases['qmla_core_info_database']
    learned_models_info_db = redis_databases['learned_models_info_db']
    learned_models_ids = redis_databases['learned_models_ids']
    bayes_factors_db = redis_databases['bayes_factors_db']
    bayes_factors_winners_db = redis_databases['bayes_factors_winners_db']
    active_branches_learning_models = redis_databases['active_branches_learning_models']
    active_branches_bayes = redis_databases['active_branches_bayes']
    active_interbranch_bayes = redis_databases['active_interbranch_bayes']

    # Retrieve data from databases
    qmla_core_info_dict = pickle.loads(
        redis_databases['qmla_core_info_database']['qmla_settings'])
    true_mod_name = qmla_core_info_dict['true_name']
    log_print(["True name:", true_mod_name])

    # Whether to build plots
    save_plots_of_posteriors = False
    plot_true_mod_post_bayes_factor_dynamics = False

    # Get model instances
    model_a = qmla.model_for_comparison.ModelInstanceForComparison(
        model_id=model_a_id,
        qid=qid,
        log_file=log_file,
        host_name=host_name,
        port_number=port_number,
    )
    model_b = qmla.model_for_comparison.ModelInstanceForComparison(
        model_id=model_b_id,
        qid=qid,
        log_file=log_file,
        host_name=host_name,
        port_number=port_number,
    )

    # Take a copy of each updater before updates (for plotting later)
    updater_a_copy = copy.deepcopy(model_a.qinfer_updater)
    updater_b_copy = copy.deepcopy(model_b.qinfer_updater)

    # Update the models with the times trained by the other model.
    log_l_a = model_a.update_log_likelihood(
        new_times = model_b.times_learned_over
    )
    log_l_b = model_b.update_log_likelihood(
        new_times = model_a.times_learned_over
    )
    bayes_factor = np.exp( log_l_a - log_l_b )

    diff_in_bf_times = (
        list ( set(model_a.bf_times) - set(model_b.bf_times) ) 
        + list (set(model_b.bf_times) - set(model_a.bf_times) )
    ) # should be empty if same experiments were used for A and B
    log_print(["Difference in times:", diff_in_bf_times])

    # Plot the posterior of the true model only
    if (
        save_plots_of_posteriors
        and (model_a.is_true_model or model_b.is_true_model)
    ):
        if model_a.is_true_model:
            true_model = model_a
            updater_copy = updater_a_copy
        elif model_b.is_true_model:
            true_model = model_b
            updater_copy = updater_b_copy

        try:
            plot_posterior_marginals(
                model=true_model,
                qmla_id=qid,
                initial_updater_copy=updater_copy,
                save_directory=bf_data_folder
            )
            log_print(["Plotting posterior marginal of true model succeeded."])
        except BaseException:
            log_print(["Plotting posterior marginal of true model failed."])
            pass

    # Plot dynamics on which models were compared
    if (
        plot_true_mod_post_bayes_factor_dynamics
    ):
        try:
            times_used = model_a.bf_times + model_b.bf_times
            plot_models_dynamics(
                model_a,
                model_b,
                exp_msmts=qmla_core_info_dict['experimental_measurements'],
                plot_probes_path=qmla_core_info_dict['probes_plot_file'],
                bayes_factor=bayes_factor,
                bf_times=times_used,
                qmla_id=qid,
                log_file=log_file,
                save_directory=bf_data_folder,
            )
        except BaseException:
            log_print(["Failed to plot dynamics after comparison."])
            raise
            # pass

    # Present result
    log_print([
        "BF computed: A:{}; B:{}; log10 BF={}".format(
            model_a_id,
            model_b_id,
            np.round(np.log10(bayes_factor), 2)
        )
    ])
    if bayes_factor < 1e-160:
        bayes_factor = 1e-160
    elif bayes_factor > 1e160:
        bayes_factor = 1e160

    pair_id = construct_models.unique_model_pair_identifier(
        model_a_id, model_b_id
    )

    if float(model_a_id) < float(model_b_id):
        # so that BF in database always refers to (low/high), not (high/low).
        bayes_factors_db.set(pair_id, bayes_factor)
    else:
        bayes_factors_db.set(pair_id, (1.0 / bayes_factor))

    # Record winner if BF > threshold
    if bayes_factor > bayes_threshold:
        bayes_factors_winners_db.set(pair_id, 'a')
    elif bayes_factor < (1.0 / bayes_threshold):
        bayes_factors_winners_db.set(pair_id, 'b')
    else:
        log_print(["Neither model much better."])

    # Record this result to the branch
    if branch_id is not None:
        active_branches_bayes.incr(int(branch_id), 1)
    else:
        active_interbranch_bayes.set(pair_id, True)

    log_print([
        "Finished. rq time: ", str(time.time() - time_start),
    ])

    del model_a, model_b
    return bayes_factor

#########
# Utilities
#########

def log_print(
    to_print_list,
    log_file,
    log_identifier
):
    r"""Wrapper for :func:`~qmla.print_to_log`"""
    qmla.logging.print_to_log(
        to_print_list=to_print_list,
        log_file=log_file,
        log_identifier=log_identifier
    )


#########
# Plotting
#########

def plot_models_dynamics(
    model_a,
    model_b,
    exp_msmts,
    plot_probes_path,
    bayes_factor,
    bf_times,
    qmla_id,
    log_file,
    save_directory=None,
):
    times = list(sorted(exp_msmts.keys()))
    experimental_exp_vals = [
        exp_msmts[t] for t in times
    ]
    fig, ax1 = plt.subplots()

    # Plot true measurements
    ax1.scatter(
        times,
        experimental_exp_vals,
        label='Exp data',
        color='red',
        alpha=0.6,
        s=5
    )
    ax1.set_ylabel('Exp Val')
    plot_probes = pickle.load(
        open(plot_probes_path, 'rb')
    )

    for mod in [model_a, model_b]:
        final_params = mod.qinfer_updater.est_mean()
        final_ham = np.tensordot(
            final_params,
            mod.model_terms_matrices,
            axes=1
        )
        dim = int(np.log2(np.shape(final_ham)[0]))
        plot_probe = plot_probes[dim]

        mod_exp_vals = [
            mod.growth_class.expectation_value(
                ham=final_ham,
                t=t,
                state=plot_probe,
                log_file=log_file,
                log_identifier='[remote_bayes_factor: plotting]'
            )
            for t in times
        ]
        ax1.plot(
            times,
            mod_exp_vals,
            label=str("({}) {}".format(mod.model_id, mod.model_name_latex ))
        )
    try:
        # in background, show how often that time was considered
        ax2 = ax1.twinx()
        num_times = int(len(times)) - 1
        print("BF times: ", repr(bf_times))
        ax2.hist(
            bf_times,
            bins=num_times,
            # TODO put on separate plot to see when higher times compared on
            range=(min(times), max(times)),
            histtype='stepfilled',
            fill=False,
            label=str("{} times total".format(len(bf_times))),
            alpha=0.1
        )
        ax2.set_ylabel('Frequency time was during comparison')
    except BaseException:
        raise
        # pass

    bf = np.log10(bayes_factor)
    plt.title(
        "[$log_{10}$ Bayes Factor]: " + str(np.round(bf, 2))
    )
    plt.figlegend()

    plot_path = os.path.join(
        save_directory,
        'BF_{}_{}.png'.format(
            str(model_a.model_id),
            str(model_b.model_id)
        )
    )
    plt.savefig(plot_path)


def plot_posterior_marginals(
    model,
    initial_updater_copy,
    qmla_id,
    save_directory,
):
    r"""
    Shows parameter distribution before/after updates for BF.

    # TODO indicate which comparison this corresponds to
    # TODO plot posterior for both models in this comparison
    # TODO also plot learned posterior --
    # ie particle locations and weights that are learned, rather than
    # the normal approximation the BF assumes
    """

    num_terms = model.qinfer_model.n_modelparams

    before_updates = [
        initial_updater_copy.posterior_marginal(idx_param=i)
        for i in range(num_terms)
    ]

    after_updates = [
        model.qinfer_updater.posterior_marginal(idx_param=i)
        for i in range(num_terms)
    ]

    ncols = int(np.ceil(np.sqrt(num_terms)))
    nrows = int(np.ceil(num_terms / ncols))
    fig, axes = plt.subplots(
        figsize=(10, 7),
        nrows=nrows,
        ncols=ncols
    )

    gs = GridSpec(
        nrows=nrows,
        ncols=ncols,
    )
    row = 0
    col = 0

    for param in range(num_terms):
        ax = fig.add_subplot(gs[row, col])

        ax.plot(
            before_updates[param][0],
            before_updates[param][1],
            color='blue',
            ls='-',
            label='Before'
        )
        ax.plot(
            after_updates[param][0],
            after_updates[param][1],
            color='red',
            ls=':',
            label='After'
        )
        if row == 0 and col == ncols - 1:
            ax.legend()

        col += 1
        if col == ncols:
            col = 0
            row += 1

    save_path = os.path.join(
        save_directory,
        'bf_posteriors_qmla_{}_model_{}'.format(
            qmla_id, model.model_id
        )
    )
    plt.savefig(save_path)
