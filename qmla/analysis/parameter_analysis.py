import numpy as np
import sys
import os
import copy 

import pickle
import pandas as pd
import matplotlib.pyplot as plt

import qmla.get_growth_rule
import qmla.database_framework
from qmla.analysis.analysis_and_plot_functions import fill_between_sigmas
plt.switch_backend('agg')

__all__ = [
    'average_parameters_across_instances',
    'average_parameter_estimates',
    'cluster_results_and_plot'
]

def rank_models(n): 
    # from
    # https://codegolf.stackexchange.com/questions/17287/sort-the-distinct-elements-of-a-list-in-descending-order-by-frequency
    return sorted(set(n), key=n.count)[::-1]


def average_parameters_across_instances(
    results_path,
    file_to_store=None, 
    top_number_models=3,
    average_type='median'
):
    r"""
    Find the median and standard deviation of parameters within all champion models
    across instances in this results directory. 

    :param results_path: path where results are stored in CSV. 
    :param file_to_store: path which is used to store the resulting priors. 
    :param top_number_models: Number of models to compute averages for 
        (top by number of instance wins). 

    :returns learned_priors: priors (median + std dev) of parameters
        of champion models. Can be stored.
    """

    results = pd.read_csv(
        results_path,
        index_col='QID'
    )
    all_winning_models = list(
        results.loc[:, 'NameAlphabetical']
    )
    winning_models = list(set(all_winning_models))
    if len(all_winning_models) > top_number_models:
        # restrict to the top N models, where N is user input
        winning_models = rank_models(all_winning_models)[0:top_number_models]

    params_dict = {}
    sigmas_dict = {}
    for mod in winning_models:
        params_dict[mod] = {}
        sigmas_dict[mod] = {}
        params = qmla.database_framework.get_constituent_names_from_name(mod)
        for p in params:
            params_dict[mod][p] = []
            sigmas_dict[mod][p] = []

    for i in range(len(winning_models)):
        mod = winning_models[i]
        learned_parameters = list(
            results[
                results['NameAlphabetical'] == mod
            ]['LearnedParameters']
        )
        final_sigmas = list(
            results[
                results['NameAlphabetical'] == mod
            ]['FinalSigmas']
        )
        num_wins_for_mod = len(learned_parameters)
        for i in range(num_wins_for_mod):
            params = eval(learned_parameters[i])
            sigmas = eval(final_sigmas[i])
            for k in list(params.keys()):
                params_dict[mod][k].append(params[k])
                sigmas_dict[mod][k].append(sigmas[k])

    average_params_dict = {}
    avg_sigmas_dict = {}
    std_deviations = {}
    learned_priors = {}
    for mod in winning_models:
        average_params_dict[mod] = {}
        avg_sigmas_dict[mod] = {}
        std_deviations[mod] = {}
        learned_priors[mod] = {}
        params = qmla.database_framework.get_constituent_names_from_name(mod)
        for p in params:
            avg_sigmas_dict[mod][p] = np.median(sigmas_dict[mod][p])
            averaging_weight = [1 / sig for sig in sigmas_dict[mod][p]]
            average_params_dict[mod][p] = np.average(
                params_dict[mod][p],
                weights=sigmas_dict[mod][p]
            )
            learned_priors[mod][p] = [
                average_params_dict[mod][p],
                avg_sigmas_dict[mod][p]
            ]

    if file_to_store is not None:
        pickle.dump(
            learned_priors,
            open(file_to_store, 'wb'),
            protocol=4
        )

    return learned_priors


def average_parameter_estimates(
    directory_name,
    results_path,
    results_file_name_start='results',
    growth_generator=None,
    unique_growth_classes=None,
    top_number_models=2,
    true_params_dict=None,
    save_to_file=None
):
    r"""
    Plots progression of parameter estimates against experiment number
    for the top models, i.e. those which win the most. 

    TODO: refactor this code - it should not need to unpickle
    all the files which have already been unpickled and stored in the summary
    results CSV.

    :param directory_name: path to directory where results .p files are stored.
    :param results_patha: path to CSV with all results for this run.
    :param growth_generator: the name of the growth generation rule used. 
    :param unique_growth_classes: dict with single instance of each growth rule class
        used in this run.
    :param top_number_models: Number of models to compute averages for 
        (top by number of instance wins). 
    :param true_params_dict: dict with true parameter for each parameter in the 
        true model.
    :param save_to_file: if not None, path to save PNG. 

    :returns None:
    """

    from matplotlib import cm
    plt.switch_backend('agg')  # to try fix plt issue on BC
    results = pd.read_csv(
        results_path,
        index_col='QID'
    )
    all_winning_models = list(results.loc[:, 'NameAlphabetical'])
    if len(all_winning_models) > top_number_models:
        winning_models = rank_models(all_winning_models)[0:top_number_models]
    else:
        winning_models = list(set(all_winning_models))

    os.chdir(directory_name)
    pickled_files = []
    for file in os.listdir(directory_name):
        if file.endswith(".p") and file.startswith(results_file_name_start):
            pickled_files.append(file)

    parameter_estimates_from_qmd = {}
    num_experiments_by_name = {}

    latex_terms = {}
    growth_rules = {}

    for f in pickled_files:
        fname = directory_name + '/' + str(f)
        result = pickle.load(open(fname, 'rb'))
        track_parameter_estimates = result['Trackplot_parameter_estimates']
    # for i in list(results.index):
    #     result = results.iloc(i)   
    #     track_parameter_estimates = eval(result['Trackplot_parameter_estimates'])

        alph = result['NameAlphabetical']
        if alph in parameter_estimates_from_qmd.keys():
            parameter_estimates_from_qmd[alph].append(
                track_parameter_estimates)
        else:
            parameter_estimates_from_qmd[alph] = [track_parameter_estimates]
            num_experiments_by_name[alph] = result['NumExperiments']

        if alph not in list(growth_rules.keys()):
            try:
                growth_rules[alph] = result['GrowthGenerator']
            except BaseException:
                growth_rules[alph] = growth_generator

    unique_growth_rules = list(set(list(growth_rules.values())))
    growth_classes = {}
    for g in list(growth_rules.keys()):
        try:
            growth_classes[g] = unique_growth_classes[growth_rules[g]]
        except BaseException:
            growth_classes[g] = None

    for name in winning_models:
        num_experiments = num_experiments_by_name[name]
        # epochs = range(1, 1+num_experiments)
        epochs = range(num_experiments_by_name[name] + 1)

        plt.clf()
        fig = plt.figure()
        ax = plt.subplot(111)

        parameters_for_this_name = parameter_estimates_from_qmd[name]
        num_wins_for_name = len(parameters_for_this_name)
        terms = sorted(qmla.database_framework.get_constituent_names_from_name(name))
        num_terms = len(terms)

        ncols = int(np.ceil(np.sqrt(num_terms)))
        nrows = int(np.ceil(num_terms / ncols))

        fig, axes = plt.subplots(
            figsize=(10, 7),
            nrows=nrows,
            ncols=ncols,
            squeeze=False,
        )
        row = 0
        col = 0
        axes_so_far = 0

        cm_subsection = np.linspace(0, 0.8, num_terms)
        colours = [cm.Paired(x) for x in cm_subsection]

        parameters = {}

        for t in terms:
            parameters[t] = {}

            for e in epochs:
                parameters[t][e] = []

        for i in range(len(parameters_for_this_name)):
            track_params = parameters_for_this_name[i]
            for t in terms:
                for e in epochs:
                    try:
                        parameters[t][e].append(track_params[t][e])
                    except:
                        parameters[t][e] = [track_params[t][e]]

        avg_parameters = {}
        std_devs = {}
        for p in terms:
            avg_parameters[p] = {}
            std_devs[p] = {}

            for e in epochs:
                avg_parameters[p][e] = np.median(parameters[p][e])
                std_devs[p][e] = np.std(parameters[p][e])

        for term in sorted(terms):
            ax = axes[row, col]
            axes_so_far += 1
            col += 1
            if (row == 0 and col == ncols):
                leg = True
            else:
                leg = False

            if col == ncols:
                col = 0
                row += 1
            # latex_terms[term] = qmla.database_frameworklatex_name_ising(term)
            latex_terms[term] = growth_classes[name].latex_name(term)
            averages = np.array(
                [avg_parameters[term][e] for e in epochs]
            )
            standard_dev = np.array(
                [std_devs[term][e] for e in epochs]
            )

            param_lw = 3
            try:
                true_val = true_params_dict[term]
                true_term_latex = growth_classes[name].latex_name(term)
                ax.axhline(
                    true_val,
                    label=str('True value'),
                    ls='--',
                    color='red',
                    lw=param_lw

                )
            except BaseException:
                pass

            ax.axhline(
                0,
                linestyle='--',
                alpha=0.5,
                color='black',
                label='0'
            )
            fill_between_sigmas(
                ax,
                parameters[term],
                epochs,
                # colour = 'blue', 
                # alpha = 0.3,
                legend=leg,
                only_one_sigma=True, 
            )
            ax.plot(
                [e + 1 for e in epochs],
                averages,
                # marker='o',
                # markevery=0.1,
                # markersize=2*param_lw,
                lw=param_lw,
                label=latex_terms[term],
                color='blue'
            )

            # ax.scatter(
            #     [e + 1 for e in epochs],
            #     averages,
            #     s=max(1, 50 / num_experiments),
            #     label=latex_terms[term],
            #     color='black'
            # )


            latex_term = growth_classes[name].latex_name(term)
            ax.set_title(str(latex_term))

        latex_name = growth_classes[name].latex_name(name)

        if save_to_file is not None:
            fig.suptitle(
                'Parameter Esimates for {}'.format(latex_name)
            )
            try:
                save_file = ''
                if save_to_file[-4:] == '.png':
                    partial_name = save_to_file[:-4]
                    save_file = str(partial_name + '_' + name + '.png')
                else:
                    save_file = str(save_to_file + '_' + name + '.png')
                # plt.tight_layout()
                fig.tight_layout(rect=[0, 0.03, 1, 0.95])
                plt.savefig(save_file, bbox_inches='tight')
            except BaseException:
                print("Filename too long. Defaulting to idx")
                save_file = ''
                if save_to_file[-4:] == '.png':
                    partial_name = save_to_file[:-4]
                    save_file = str(
                        partial_name +
                        '_' +
                        str(winning_models.index(name)) +
                        '.png'
                    )
                else:
                    save_file = str(save_to_file + '_' + name + '.png')
                # plt.tight_layout()
                fig.tight_layout(rect=[0, 0.03, 1, 0.95])
                plt.savefig(save_file, bbox_inches='tight')

def cluster_results_and_plot(
    path_to_results,  # results_summary_csv to be clustered
    true_expec_path,
    plot_probe_path,
    true_params_path,
    growth_generator,
    # measurement_type,
    upper_x_limit=None,
    save_param_clusters_to_file=None,
    save_param_values_to_file=None,
    save_redrawn_expectation_values=None,
):
    from matplotlib import cm
    growth_class = qmla.get_growth_rule.get_growth_generator_class(growth_generator)
    results_csv = pd.read_csv(path_to_results)
    unique_champions = list(
        set(list(results_csv['NameAlphabetical']))
    )

    true_info_dict = pickle.load(
        open(true_params_path, 'rb')
    )
    try:
        growth_generator = true_info_dict['growth_generator']
    except BaseException:
        pass

    true_params_dict = true_info_dict['params_dict']
    if true_params_dict is not None:
        for k in list(true_params_dict.keys()):
            latex_key = growth_class.latex_name(
                name=k
            )
            true_params_dict[latex_key] = true_params_dict[k]
            true_params_dict.pop(k)

    all_learned_params = {}
    champions_params = {}

    for i in range(len(unique_champions)):
        champ = unique_champions[i]
        all_learned_params[champ] = (
            results_csv.loc[results_csv['NameAlphabetical']
                            == champ]['LearnedParameters'].values
        )
        this_champs_params = sorted(
            list(eval(all_learned_params[champ][0]).keys()))
        champions_params[champ] = this_champs_params

    all_possible_params = []
    for p_list in champions_params.values():
        all_possible_params.extend(p_list)

    all_possible_params = list(
        set(list(all_possible_params))
    )
    clusters = {}
    params_for_clustering = {}
    # this_champ = unique_champions[0]
    for this_champ in unique_champions:
        num_results_for_this_champ = len(all_learned_params[this_champ])
        params_this_champ = sorted(
            list(eval(all_learned_params[this_champ][0]).keys())
        )
        params = np.empty([num_results_for_this_champ,
                           len(champions_params[this_champ])])
        for i in range(num_results_for_this_champ):
            learned_param_dict = eval(all_learned_params[this_champ][i])
            test_list = [i for i in champions_params[this_champ]]
            params[i] = [
                learned_param_dict[this_param] for this_param in champions_params[this_champ]
            ]

        params_for_clustering[this_champ] = params

    for this_champ in unique_champions:
        num_results_for_this_champ = len(
            all_learned_params[this_champ]
        )
        try:
            ms = MeanShift()
            ms.fit(params_for_clustering[this_champ])
            labels = ms.labels_
            cluster_centers = ms.cluster_centers_

            labels_unique = np.unique(labels)
            n_clusters_ = len(labels_unique)

            clusters[this_champ] = cluster_centers
        except BaseException:
            # NOTE: in case where clusters can't be formed,
            # that model is represented only by the first set of results..
            # should they be averaged somehow?
            clusters[this_champ] = np.array(
                [params_for_clustering[this_champ][0]])

    available_clustered_models = list(clusters.keys())
    clustered_parameters_this_model = {}
    clusters_by_model = {}
    cluster_descriptions_by_model = {}
    all_clusters_params = []
    all_clusters_descriptions = []
    all_centroids_of_each_param = {}

    for mod in available_clustered_models:
        clusters_by_model[mod] = {}
        cluster_descriptions_by_model[mod] = []
        terms = champions_params[mod]
        this_model_clusters = clusters[mod]

        for j in range(len(this_model_clusters)):
            single_cluster = {}
            for i in range(len(terms)):
                single_cluster[terms[i]] = this_model_clusters[j][i]
                try:
                    all_centroids_of_each_param[terms[i]].append(
                        this_model_clusters[j][i])
                except BaseException:
                    all_centroids_of_each_param[terms[i]] = [
                        this_model_clusters[j][i]]

            latex_mod_name = growth_class.latex_name(
                name=mod
            )
            cluster_description = str(
                latex_mod_name + ' (' + str(j) + ')'
            )
            all_clusters_params.append(single_cluster)
            all_clusters_descriptions.append(
                cluster_description
            )
            clusters_by_model[mod][cluster_description] = single_cluster
            cluster_descriptions_by_model[mod].append(
                cluster_description
            )

    for k in list(all_centroids_of_each_param.keys()):
        latex_term = growth_class.latex_name(name=k)
        all_centroids_of_each_param[latex_term] = all_centroids_of_each_param[k]
        all_centroids_of_each_param.pop(k)

    cm_subsection = np.linspace(
        0, 0.8, len(all_possible_params)
    )
    plot_colours = [cm.Paired(x) for x in cm_subsection]

    term_colours = {}
    latex_terms = {}
    for term in all_possible_params:
        latex_rep = growth_class.latex_name(name=term)

        latex_terms[term] = latex_rep

    for i in range(len(all_possible_params)):
        name = latex_terms[all_possible_params[i]]
        term_colours[name] = plot_colours[i]
    total_num_clusters = 0
    for c in clusters:
        total_num_clusters += len(clusters[c])

    #######
    # Plot centroids by parameter
    #######
    unique_latex_params = list(
        set(list(all_centroids_of_each_param.keys()))
    )
    total_num_params = len(unique_latex_params)
    ncols = int(np.ceil(np.sqrt(total_num_params)))
    nrows = int(np.ceil(total_num_params / ncols))

    fig, axes = plt.subplots(
        figsize=(10, 7),
        nrows=nrows,
        ncols=ncols,
        squeeze=False
    )
    row = 0
    col = 0

    # from here below has to be put on an array layout

    for param in sorted(unique_latex_params):
        ax = axes[row, col]
        ax.get_shared_y_axes().join(ax, axes[row, 0])
        this_param_values = all_centroids_of_each_param[param]
        try:
            true_param = true_params_dict[param]
            ax.axhline(
                true_param,
                linestyle='--',
                label='True',
                color=term_colours[param]
            )
        except BaseException:
            pass

        for v in this_param_values:
            if this_param_values.index(v) == 0:
                ax.axhline(
                    v,
                    color=term_colours[param],
                    label=param
                )
            else:
                ax.axhline(
                    v,
                    color=term_colours[param],
                )
        ax.legend(loc=1)
        col += 1
        if col == ncols:
            col = 0
            row += 1

    if save_param_values_to_file is not None:
        plt.savefig(
            save_param_values_to_file,
            bbox_to_inches='tight'
        )

    # Plot centroids by cluster
    ncols = int(np.ceil(np.sqrt(total_num_clusters)))
    nrows = int(np.ceil(total_num_clusters / ncols))

    fig, axes = plt.subplots(
        figsize=(10, 7),
        nrows=nrows,
        ncols=ncols,
        squeeze=False
    )
    row = 0
    col = 0

    # from here below has to be put on an array layout
    for mod in sorted(clusters_by_model):
        for cluster_description in sorted(
            list(clusters_by_model[mod].keys())
        ):
            cluster = clusters_by_model[mod][cluster_description]
            ax = axes[row, col]
            for term in sorted(cluster.keys()):
                label = growth_class.latex_name(
                    name=term
                )
                ax.axhline(
                    cluster[term],
                    label=label,
                    color=term_colours[label]
                )
                ax.set_title(cluster_description)

            col += 1
            # TODO add legend for all individual params/colours...
            # single legend accross subplots??
            # if col == ncols and row == 0:
            ax.legend(loc=1)
            if col == ncols:
                col = 0
                row += 1

    if save_param_clusters_to_file is not None:
        plt.title('Parameter clusters')
        plt.savefig(
            save_param_clusters_to_file,
            bbox_to_inches='tight'
        )

    replot_expectation_values(
        params_dictionary_list=all_clusters_params,  # list of params_dicts
        model_descriptions=all_clusters_descriptions,
        true_expec_vals_path=true_expec_path,
        plot_probe_path=plot_probe_path,
        growth_generator=growth_generator,
        # measurement_method=measurement_type,
        upper_x_limit=upper_x_limit,  # can play with this
        save_to_file=save_redrawn_expectation_values
    )

def replot_expectation_values(
    params_dictionary_list,  # list of params_dicts
    true_expec_vals_path,
    plot_probe_path,
    growth_generator,
    # measurement_method='full_access',
    upper_x_limit=None,
    model_descriptions=None,
    save_to_file=None
):
    r"""
    Standalone function to redraw expectation values
    of QHL given the params_dict it learned, and
    the path to the dict of true expectation values
    it was emulating
    """

    # print("[replot] ",
    #     "\ntrue_expec_vals_path", true_expec_vals_path,
    #     "\nplot_probe_path", plot_probe_path,
    #     "\ngrowth_generator", growth_generator,
    #     "\nmeasurement_method", measurement_method
    # )
    growth_class = qmla.get_growth_rule.get_growth_generator_class(
        growth_generation_rule=growth_generator
    )
    sim_colours = ['b', 'g', 'c', 'y', 'm', 'k']
    plot_probes = pickle.load(open(plot_probe_path, 'rb'))
    # true_expec_vals_path = str(
    #     directory_name + 'true_expec_vals.p'
    # )
    # print(
    #     "Reconstructed QHL with expectation value method:",
    #     measurement_method
    # )
    true_exp_vals = pickle.load(open(true_expec_vals_path, 'rb'))
    exp_times = sorted(list(true_exp_vals.keys()))

    sim_times = copy.copy(exp_times)[0::5]

    num_times = len(exp_times)
    max_time = max(exp_times)
    # sim_times = list(sorted(
    #     np.linspace(0, 2*max_time, num_times))
    # )

    if (
        upper_x_limit is not None
        and
        upper_x_limit > max(exp_times)
    ):
        additional_sim_times = np.linspace(max(exp_times), upper_x_limit, 30)
        sim_times.extend(additional_sim_times)
        sim_times = sorted(sim_times)

    if type(params_dictionary_list) == dict:
        params_dictionary_list = [params_dictionary_list]

    num_plots = len(params_dictionary_list)
    ncols = int(np.ceil(np.sqrt(num_plots)))
    nrows = int(np.ceil(num_plots / ncols))

    fig, axes = plt.subplots(
        figsize=(10, 7),
        nrows=nrows,
        ncols=ncols,
        squeeze=False
    )
    row = 0
    col = 0

    true_exp = [true_exp_vals[t] for t in exp_times]
    for params_dict in params_dictionary_list:
        ax = axes[row, col]
        sim_ops_names = list(params_dict.keys())
        sim_params = [
            params_dict[k] for k in sim_ops_names
        ]
        sim_ops = [
            qmla.database_framework.compute(k) for k in sim_ops_names
        ]
        sim_ham = np.tensordot(sim_params, sim_ops, axes=1)

        sim_num_qubits = qmla.database_framework.get_num_qubits(sim_ops_names[0])
        # p_str=''
        # for i in range(2):
        #     p_str+='P'
        p_str = 'P' * sim_num_qubits
        probe = plot_probes[sim_num_qubits]

        sim_exp_vals = {}
        for t in sim_times:
            sim_exp_vals[t] = growth_class.expectation_value(
                ham=sim_ham,
                state=probe,
                t=t
            )

        sim_exp = [sim_exp_vals[t] for t in sim_times]
        list_id = params_dictionary_list.index(params_dict)
        sim_colour = sim_colours[list_id % len(sim_colours)]

        if model_descriptions is not None:
            model_label = model_descriptions[list_id]
        else:
            sim_op_string = p_str.join(sim_ops_names)
            latex_name = growth_class.latex_name(name=sim_op_string)
            model_label = latex_name

        ax.plot(
            sim_times,
            sim_exp,
            marker='o',
            markersize=3,
            markevery=5,
            label=str(model_label),
            color=sim_colour
        )
        ax.set_title(model_label)
        ax.scatter(
            exp_times,
            true_exp,
            label='True',
            color='red',
            s=3
        )
        ax.set_xlim(0, upper_x_limit)

        col += 1
        # if col == ncols and row == 0:
        ax.legend(loc=1)
        if col == ncols:
            col = 0
            row += 1

    # plt.legend(loc=1)
    fig.suptitle("Expectation Value of clustered parameters.")
    if save_to_file is not None:
        plt.savefig(save_to_file, bbox_inches='tight')
    else:
        plt.show()
