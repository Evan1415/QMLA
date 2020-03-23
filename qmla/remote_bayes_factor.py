import copy
import pickle
import random
import time as time
import numpy as np
import os as os
import pandas as pd

import matplotlib.pyplot as plt

import qmla.database_framework as database_framework
import qmla.model_instances as QML
import qmla.logging

try:
    import qmla.redis_settings as rds
    import redis
    enforce_serial = False
except BaseException:
    enforce_serial = True  # shouldn't be needed

pickle.HIGHEST_PROTOCOL = 4
plt.switch_backend('agg')


__all__ = [
    'remote_bayes_factor_calculation'
]

# Single function call to compute Bayes Factor between models given their IDs
def remote_bayes_factor_calculation(
    model_a_id,
    model_b_id,
    branch_id=None,
    interbranch=False,
    num_times_to_use='all',
    bf_data_folder=None,
    times_record='BayesFactorsTimes.txt',
    check_db=False,
    # trueModel=None,
    bayes_threshold=1,
    host_name='localhost',
    port_number=6379,
    qid=0,
    log_file='rq_output.log'
):
    """
    This is a standalone function to compute Bayes factors without knowledge
    of full QMD program. QMD info is unpickled from a redis databse, containing
    learned_model information, i.e. final parameters etc.
    Given model ids correspond to model names in the database, which are combined
    with the final learned parameters to reconstruct model classes of
    complete learned models.
    From these we extract log likelihoods to compute Bayes factors.

    """
    def log_print(to_print_list):
        qmla.logging.print_to_log(
            to_print_list = to_print_list, 
            log_file = log_file, 
            log_identifier = 'BF ({}/{})'.format(model_a_id, model_b_id)
        )
    
    time_start = time.time()
    redis_databases = rds.databases_from_qmd_id(host_name, port_number, qid)
    qmla_core_info_database = redis_databases['qmla_core_info_database']
    learned_models_info_db = redis_databases['learned_models_info_db']
    learned_models_ids = redis_databases['learned_models_ids']
    bayes_factors_db = redis_databases['bayes_factors_db']
    bayes_factors_winners_db = redis_databases['bayes_factors_winners_db']
    active_branches_learning_models = redis_databases['active_branches_learning_models']
    active_branches_bayes = redis_databases['active_branches_bayes']
    active_interbranch_bayes = redis_databases['active_interbranch_bayes']

    qmla_core_info_dict = pickle.loads(redis_databases['qmla_core_info_database']['qmla_settings'])
    use_experimental_data = qmla_core_info_dict['use_experimental_data']
    experimental_data_times = qmla_core_info_dict['experimental_measurement_times']

    linspace_times_for_bayes_factor_comparison = False
    use_opponent_learned_times = True
    true_mod_name = qmla_core_info_dict['true_name']
    save_plots_of_posteriors = True
    plot_true_mod_post_bayes_factor_dynamics = False

    if check_db:  # built in to only compute once and always return the stored value.
        if pair_id in bayes_factors_db.keys():
            bayes_factor = bayes_factors_db.get(pair_id)
            log_print(["Redis GET bayes_factors_db pair:", pair_id])
            if model_a_id < model_b_id:
                return bayes_factor
            else:
                return (1.0 / bayes_factor)
    else:

        model_a = QML.ModelInstanceForComparison(
            model_id=model_a_id,
            qid=qid,
            log_file=log_file,
            host_name=host_name,
            port_number=port_number,
        )
        model_b = QML.ModelInstanceForComparison(
            model_id=model_b_id,
            qid=qid,
            log_file=log_file,
            host_name=host_name,
            port_number=port_number,
        )

        # By default, use times the other model trained on,
        # up to t_idx given.
        # And inherit renormalization record from QML updater
        # In special cases, eg experimental data, change these defaults below.
        log_print(["Start. Branch", branch_id])
        if num_times_to_use == 'all':
            first_t_idx = 0
        else:
            first_t_idx = len(model_a.times_learned_over) - num_times_to_use

        update_times_model_a = model_b.times_learned_over[first_t_idx:]
        update_times_model_b = model_a.times_learned_over[first_t_idx:]
        set_renorm_record_to_zero = False

        with open(times_record, 'a') as write_log_file:
            np.set_printoptions(
                precision=2
            )
            print(
                "\n\nModels {}/{}".format(
                    model_a.model_id,
                    model_b.model_id
                ),
                "\n\tID_A {} [len {}]: {}".format(
                    model_a.model_id,
                    len(update_times_model_a),
                    [np.round(val, 2) for val in update_times_model_a]
                ),
                "\n\tID_B {} [len {}]: {}".format(
                    model_b.model_id,
                    len(update_times_model_b),
                    [np.round(val, 2) for val in update_times_model_b]
                ),
                file=write_log_file
            )

        updater_a_copy = copy.deepcopy(model_a.qinfer_updater)
        log_l_a = log_likelihood(
            model_a,
            update_times_model_a,
            binning=set_renorm_record_to_zero,
            log_file = log_file, 
        )
        log_l_b = log_likelihood(
            model_b,
            update_times_model_b,
            binning=set_renorm_record_to_zero,
            log_file = log_file, 
        )

        # after learning, want to see what dynamics are like after further
        # updaters
        bayes_factor = np.exp(log_l_a - log_l_b)

        if (
            save_plots_of_posteriors == True
            and
            database_framework.alph(model_a.model_name) == database_framework.alph(true_mod_name)
        ):
            try:
                print("\n\nBF UPDATE Model {}".format(model_a.model_name))
                plot_posterior_marginals(
                    model_a=model_a,
                    qid=qid,
                    updater_a_copy=updater_a_copy,
                    bf_data_folder=bf_data_folder
                )
            except BaseException:
                raise

        # TODO this is the original position of getting log likelihood + bayes factor;
        # moving above so we can plot posterior before and after BF updates.
        # log_l_a = log_likelihood(
        #     model_a,
        #     update_times_model_a,
        #     binning=set_renorm_record_to_zero
        # )
        # log_l_b = log_likelihood(
        #     model_b,
        #     update_times_model_b,
        #     binning=set_renorm_record_to_zero
        # )
        # # log_print(["Log likelihoods computed."])

        # # after learning, want to see what dynamics are like after further updaters
        # bayes_factor = np.exp(log_l_a - log_l_b)
        if (
            (
                database_framework.alph(model_a.model_name) == database_framework.alph(true_mod_name)
                or
                database_framework.alph(model_b.model_name) == database_framework.alph(true_mod_name)
            )
            and
            plot_true_mod_post_bayes_factor_dynamics == True
        ):
            try:
                plot_path = str(
                    bf_data_folder +
                    '/BF_{}__{}_{}.png'.format(
                        str(qid),
                        str(model_a.model_id),
                        str(model_b.model_id)
                    )
                )
                plot_expec_vals_of_models(
                    model_a,
                    model_b,
                    bayes_factor=bayes_factor,
                    bf_times=update_times_model_a,
                    log_file=log_file,
                    save_to_file=plot_path
                )
            except BaseException:
                raise
                # pass

        log_print(
            [
                "BF computed: A:{}; B:{}; BF:{}".format(
                    model_a_id,
                    model_b_id,
                    np.round(bayes_factor, 2)
                ),
                "\tReset remormalisation record:",
                set_renorm_record_to_zero
            ]
        )
        if bayes_factor < 1e-160:
            bayes_factor = 1e-160
        elif bayes_factor > 1e160:
            bayes_factor = 1e160

        pair_id = database_framework.unique_model_pair_identifier(
            model_a_id, model_b_id
        )
        print("Bayes Factor:", pair_id)
        if float(model_a_id) < float(model_b_id):
            # so that BF in db always refers to (low/high), not (high/low).
            bayes_factors_db.set(pair_id, bayes_factor)
        else:
            bayes_factors_db.set(pair_id, (1.0 / bayes_factor))

        if bayes_factor > bayes_threshold:
            bayes_factors_winners_db.set(pair_id, 'a')
        elif bayes_factor < (1.0 / bayes_threshold):
            bayes_factors_winners_db.set(pair_id, 'b')
        else:
            log_print(["Neither model much better."])

        if branch_id is not None:
            # only want to fill these lists when comparing models within branch
            # log_print(["Redis INCR active_branches_bayes branch:", branch_id])
            active_branches_bayes.incr(int(branch_id), 1)
        else:
            active_interbranch_bayes.set(pair_id, True)
            # log_print(["Redis SET active_interbranch_bayes pair:", pair_id,
            #     "; set:True"]
            # )
        time_end = time.time()
        log_print(
            [
                "Finished. rq time: ",
                str(time_end - time_start)
            ]
        )

        return bayes_factor

def log_print(
    to_print_list,
    log_file, 
    log_identifier
):
    qmla.logging.print_to_log(
        to_print_list = to_print_list, 
        log_file = log_file, 
        log_identifier = log_identifier
    )


def log_likelihood(
    model,
    times,
    binning=False,
    log_file=None,
):
    updater = model.qinfer_updater
    
    if binning:
        updater._renormalization_record = []
        updater.log_total_likelihood = 0
        print("BINNING")

    for i in range(len(times)):
        exp = get_exp(model, [times[i]])
        params_array = np.array([[model.true_model_params[:]]])
        # log_print(
        #     to_print_list = [
        #         "Getting datum"
        #     ], 
        #     log_file = log_file, 
        #     log_identifier = 'log_likelihood'
        # )
        datum = updater.model.simulate_experiment(
            params_array,
            exp,
            repeat=1
        )
        # log_print(
        #     to_print_list = [
        #         "Performing update"
        #     ], 
        #     log_file = log_file, 
        #     log_identifier = 'log_likelihood'
        # )
        updater.update(datum, exp)

    log_likelihood = updater.log_total_likelihood
    return log_likelihood


def get_exp(model, time):
    gen = model.qinfer_model
    exp = np.empty(
        len(time),
        dtype=gen.expparams_dtype
    )
    exp['t'] = time

    try:
        for i in range(1, len(gen.expparams_dtype)):
            col_name = 'w_' + str(i)
            exp[col_name] = model.final_learned_params[i - 1, 0]
    except BaseException:
        print("failed to get exp. \nFinal params:", model.final_learned_params)

    return exp


#########
# Functions for rescaling times to be used during Bayes factor calculation
#########

def plot_expec_vals_of_models(
    model_a,
    model_b,
    bayes_factor,
    bf_times,
    log_file,
    save_to_file=None
):
    exp_msmts = model_aexperimental_measurements
    times = list(sorted(exp_msmts.keys()))
    experimental_exp_vals = [
        exp_msmts[t] for t in times
    ]
    # plt.clf()
    fig, ax1 = plt.subplots()
    # ax1 = plt.plot()

    ax1.set_ylabel('Exp Val')
    ax1.scatter(
        times,
        experimental_exp_vals,
        label='Exp data',
        color='red',
        alpha=0.6,
        s=5
    )
    # plt.legend()
    plot_probes = pickle.load(
        open(model_a.PlotProbePath, 'rb')
    )

    for mod in [model_a, model_b]:
        # TODO get final learned params,
        # generate hamiltonian from mod.model_terms_matrices
        # get exp vals against times list
        # plot using different colour

        final_params = mod.qinfer_updater.est_mean()
        final_ham = np.tensordot(
            final_params,
            mod.model_terms_matrices,
            axes=1
        )
        dim = int(np.log2(np.shape(final_ham)[0]))
        plot_probe = plot_probes[dim]

        mod_exp_vals = []
        for t in times:
            # print("Getting exp for t=", t)
            try:
                # todo get this from GenSimModel of mod instead of
                # instantiating class every time
                exp_val = mod.growth_class.expectation_value(
                    ham=final_ham,
                    t=t,
                    state=plot_probe,
                    log_file=log_file,
                    log_identifier='[remote_bayes_factor plots]'
                )
            except BaseException:
                raise
            mod_exp_vals.append(exp_val)
            # mod_exp_vals.append(t)
            # print("exp val found for t={}:{}".format(t, exp_val))
        ax1.plot(
            times,
            mod_exp_vals,
            label=str(mod.model_id)
        )
    ax2 = ax1.twinx()

    num_times = int(len(times)) - 1
    ax2.hist(
        bf_times,
        bins=num_times,
        # histtype='bar',
        histtype='stepfilled',
        fill=False,
        color='black',
        label=str("{} times total".format(len(bf_times))),
        alpha=0.3
    )

    ax2.set_ylabel('Frequency of time updated')
    bf = np.log10(bayes_factor)

    plt.title(
        "[$log_{10}$ Bayes Factor]: " + str(np.round(bf, 2))
    )
    # ax1.legend()
    # ax2.legend()
    plt.figlegend()

    if save_to_file is not None:
        plt.savefig(save_to_file, bbox_inches='tight')


def plot_posterior_marginals(
    model_a,
    updater_a_copy,
    qid,
    bf_data_folder
):
    old_post_marg = model_a.posterior_marginal
    before_bf_updates = []
    new_post_marg = []

    posterior_plot_path = str(
        bf_data_folder +
        '/posterior_marginal_pickle_{}_{}.p'.format(
            str(qid),
            str(model_a.model_id),
        )
    )

    pickle.dump(
        # model_a.qinfer_updater,
        updater_a_copy,
        open(
            posterior_plot_path,
            'wb'
        )
    )

    for i in range(len(old_post_marg)):
        before_bf_updates.append(
            updater_a_copy.posterior_marginal(idx_param=i)
        )

        new_post_marg.append(
            model_a.qinfer_updater.posterior_marginal(idx_param=i)
        )
        # new_post_marg = model_a.qinfer_updater.posterior_marginal(1)

    # print("OLD:", old_post_marg)
    # print("NEW:", new_post_marg)
    param_of_interest = 1

    for param_of_interest in range(len(old_post_marg)):
        posterior_plot_path = str(
            bf_data_folder +
            '/posterior_marginal_{}_mod{}_param{}.png'.format(
                str(qid),
                str(model_a.model_id),
                str(param_of_interest)
            )
        )
        if os.path.exists(posterior_plot_path):
            # ie a previous BF calculation has drawn these for the true model
            break
        plt.clf()
        plt.plot(
            before_bf_updates[param_of_interest][0],
            before_bf_updates[param_of_interest][1],
            color='blue',
            linestyle='-',
            label='Start BF',
            alpha=0.5
        )
        # plt.plot(
        #     new_post_marg[param_of_interest][0],
        #     new_post_marg[param_of_interest][1],
        #     color='y',
        #     linestyle = '-.',
        #     label='End BF',
        #     # alpha=0.5,
        # )
        init_post_marg = model_a.initial_prior[param_of_interest]
        # plt.plot(
        #     init_post_marg[0],
        #     init_post_marg[1],
        #     color='green',
        #     label='Start QML',
        #     linestyle='-',
        #     alpha=0.4,
        # )
        plt.plot(
            old_post_marg[param_of_interest][0],
            old_post_marg[param_of_interest][1],
            color='red',
            linestyle=':',
            label='End QML'
        )
        plt.legend()

        plt.savefig(posterior_plot_path)
