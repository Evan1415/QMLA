import sys, os
import pickle
import matplotlib.pyplot as plt
plt.switch_backend('agg')
from matplotlib.lines import Line2D

import argparse
import numpy as np

import DataBase
import pandas
import PlotQMD as ptq
import ModelNames
import UserFunctions 

#This is a simple test comment
"""
def summariseResultsCSV(directory_name, csv_name='all_results.csv'):
    import os, csv
    if not directory_name.endswith('/'):
        directory_name += '/'

    if not csv_name.endswith('.csv'):
        csv_name += '.csv'
        
    pickled_files = []
    for file in os.listdir(directory_name):
        if file.endswith(".p") and file.startswith("results"):
            pickled_files.append(file)

    filenames = [directory_name+str(f) for f in pickled_files ]
    some_results = pickle.load(open(filenames[0], "rb"))
    result_fields = list(some_results.keys())
    
    
#    results_csv = str(directory_name+str(csv_name))
    results_csv = str(csv_name)

    
    with open(results_csv, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=result_fields)
        writer.writeheader()

        for f in filenames:
            results = pickle.load(open(f, "rb"))
            writer.writerow(results)
"""

def parameter_sweep_analysis(
    directory_name, 
    results_csv, 
    save_to_file=None, 
    use_log_times=False, 
    use_percentage_models=False
):

    import os, csv
    if not directory_name.endswith('/'):
        directory_name += '/'

    qmd_cumulative_results = pandas.DataFrame.from_csv(results_csv,
        index_col='ConfigLatex'
    )
    piv = pandas.pivot_table(
        qmd_cumulative_results, 
        values=['CorrectModel', 'Time', 'Overfit', 'Underfit', 'Misfit'], 
        index=['ConfigLatex'], 
        aggfunc={
            'Time':[np.mean, np.median, min, max], 
            'CorrectModel' : [np.sum, np.mean],
            'Overfit' : [np.sum, np.mean],
            'Misfit' : [np.sum, np.mean],
            'Underfit' : [np.sum, np.mean] 
        }
    )

    time_means = list(piv['Time']['mean'])
    time_mins = list(piv['Time']['min'])
    time_maxs = list(piv['Time']['max'])
    time_medians = list(piv['Time']['median'])
    correct_count = list(piv['CorrectModel']['sum'])
    correct_ratio = list(piv['CorrectModel']['mean'])
    overfit_count = list(piv['Overfit']['sum'])
    overfit_ratio = list(piv['Overfit']['mean'])
    underfit_count = list(piv['Underfit']['sum'])
    underfit_ratio = list(piv['Underfit']['mean'])
    misfit_count = list(piv['Misfit']['sum'])
    misfit_ratio = list(piv['Misfit']['mean'])
    num_models = len(time_medians)

    configs = piv.index.tolist()
    percentages = [a*100 for a in correct_ratio]


    plt.clf()
    fig, ax = plt.subplots()
    if num_models <= 5 :
        plot_height = num_models
    else:
        plot_height = num_models/2
    
    fig.set_figheight(plot_height)
    #fig.set_figwidth(num_models/4)

    ax2 = ax.twiny()
    width = 0.5 # the width of the bars 
    ind = np.arange(len(correct_ratio))  # the x locations for the groups

    if use_log_times:
        times_to_use = [np.log10(t) for t in time_medians]
        ax2.set_xlabel('Time ($log_{10}$ seconds)')
    else:
        times_to_use = time_medians
        ax2.set_xlabel('Median Time (seconds)')

    if use_percentage_models:
        correct = [a*100 for a in correct_ratio]
        misfit = [a*100 for a in misfit_ratio]
        underfit = [a*100 for a in underfit_ratio]
        overfit = [a*100 for a in overfit_ratio]
        ax.set_xlabel('% Models')
    else:
        correct = correct_count
        misfit = misfit_count
        overfit = overfit_count
        underfit = underfit_count
        ax.set_xlabel('Number of Models')

    max_x = correct[0] + misfit[0] + overfit[0] + underfit[0]
    time_colour = 'b'
    ax2.barh(ind, times_to_use, width/4, color=time_colour, label='Time')
    
    times_to_mark = [60,600, 3600, 14400, 36000]
    if use_log_times:
        times_to_mark = [np.log10(t) for t in times_to_mark]

    max_time = max(times_to_use)
    for t in times_to_mark:
        if t < max_time:
            ax2.axvline(x=t, color=time_colour)


    left_pts = [0] * num_models
    ax.barh(ind, correct, width, color='g', align='center', 
        label='Correct Models', left=left_pts
    )
    left_pts = [sum(x) for x in zip(left_pts, correct)]

    ax.barh(ind, underfit, width, color='r', align='center', 
        label='Underfit Models', left=left_pts
    )
    left_pts = [sum(x) for x in zip(left_pts, underfit)]
    
    ax.barh(ind, misfit, width, color='orange', align='center', 
        label='Misfit Models', left=left_pts
    )
    left_pts = [sum(x) for x in zip(left_pts, misfit)]

    ax.barh(ind, overfit, width, color='y', align='center', 
        label='Overfit Models', left=left_pts
    )
    left_pts = [sum(x) for x in zip(left_pts, overfit)]

#    ax.axvline(x=max_x/2, color='g', label='50% Models correct')   
    ax.set_yticks(ind)
    ax.set_yticklabels(configs, minor=False)
    ax.set_ylabel('Configurations')

    lines, labels = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc='upper center',
        bbox_to_anchor=(0.5, -0.2), ncol=2
    )

    if save_to_file is not None:
        plt.savefig(save_to_file, bbox_inches='tight')
        
        
def average_parameters(
    results_path, 
    top_number_models=3,
    average_type='median'
):

    results = pandas.DataFrame.from_csv(
        results_path,
        index_col='QID'
    )

    all_winning_models = list(results.loc[:, 'NameAlphabetical'])
    rank_models = lambda n:sorted(set(n), key=n.count)[::-1] 
    # from https://codegolf.stackexchange.com/questions/17287/sort-the-distinct-elements-of-a-list-in-descending-order-by-frequency
    
    if len(all_winning_models) > top_number_models:
        winning_models = rank_models(all_winning_models)[0:top_number_models]
    else:
        winning_models = list(set(all_winning_models))    


    params_dict = {}
    sigmas_dict = {}
    for mod in winning_models:
        params_dict[mod] = {}
        sigmas_dict[mod] = {}
        params = DataBase.get_constituent_names_from_name(mod)
        for p in params:
            params_dict[mod][p] = []
            sigmas_dict[mod][p] = []

    for i in range(len(winning_models)):
        mod = winning_models[i]
        learned_parameters = list(
            results[ results['NameAlphabetical']==mod ]
            ['LearnedParameters']
        )
        final_sigmas = list(
            results[ results['NameAlphabetical']==mod ]
            ['FinalSigmas']
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
        params = DataBase.get_constituent_names_from_name(mod)
        for p in params:
            # if average_type == 'median':
            #     average_params_dict[mod][p] = np.median(
            #         params_dict[mod][p]
            #     )
            # else:
            #     average_params_dict[mod][p] = np.mean(
            #         params_dict[mod][p]
            #     )
            # if np.std(params_dict[mod][p]) > 0:                
            #     std_deviations[mod][p] = np.std(params_dict[mod][p])
            # else:
            #     # if only one winner, give relatively broad prior. 
            #     std_deviations[mod][p] = 0.5 
            

            # learned_priors[mod][p] = [
            #     average_params_dict[mod][p], 
            #     std_deviations[mod][p]
            # ]


            avg_sigmas_dict[mod][p] = np.median(sigmas_dict[mod][p])
            averaging_weight = [1/sig for sig in sigmas_dict[mod][p]]
            # print("[mod][p]:", mod, p)
            # print("Attempting to avg this list:", params_dict[mod][p])
            # print("with these weights:", averaging_weight)

            average_params_dict[mod][p] = np.average(
                params_dict[mod][p], 
                weights=sigmas_dict[mod][p]
            )
            # print("avg sigmas dict type:", type(avg_sigmas_dict[mod][p]))
            # print("type average_params_dict:", type(average_params_dict[mod][p]))
            # print("avg sigmas dict[mod][p]:", avg_sigmas_dict[mod][p])
            # print("average_params_dict[mod][p]:", average_params_dict[mod][p])
            learned_priors[mod][p] = [
                average_params_dict[mod][p], 
                avg_sigmas_dict[mod][p]
            ]
    
    return learned_priors   

def average_parameter_estimates(
    directory_name, 
    results_path, 
    results_file_name_start='results',
    growth_generator=None, 
    top_number_models=2,
    true_params_dict=None,
    save_to_file=None
):
    from matplotlib import cm
    plt.switch_backend('agg') #  to try fix plt issue on BC
    results = pandas.DataFrame.from_csv(
        results_path,
        index_col='QID'
    )

    all_winning_models = list(results.loc[:, 'NameAlphabetical'])
    rank_models = lambda n:sorted(set(n), key=n.count)[::-1] 
    # from https://codegolf.stackexchange.com/questions/17287/sort-the-distinct-elements-of-a-list-in-descending-order-by-frequency

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
        fname = directory_name+'/'+str(f)
        result = pickle.load(open(fname, 'rb'))
        alph = result['NameAlphabetical']
        track_parameter_estimates = result['TrackParameterEstimates']
        
        # num_experiments = result['NumExperiments']
        if alph in parameter_estimates_from_qmd.keys():
            parameter_estimates_from_qmd[alph].append(track_parameter_estimates)
        else:
            parameter_estimates_from_qmd[alph] = [track_parameter_estimates]
            num_experiments_by_name[alph] = result['NumExperiments']

        if alph not in list(growth_rules.keys()):
            try:
                growth_rules[alph] = result['GrowthGenerator']
            except:
                growth_rules[alph] = growth_generator


    for name in winning_models:
        num_experiments = num_experiments_by_name[name]
        # epochs = range(1, 1+num_experiments)
        epochs = range(num_experiments_by_name[name])

        plt.clf()
        fig = plt.figure()
        ax = plt.subplot(111)

        parameters_for_this_name = parameter_estimates_from_qmd[name]
        num_wins_for_name = len(parameters_for_this_name)
        terms = sorted(DataBase.get_constituent_names_from_name(name))
        num_terms = len(terms)

        ncols = int(np.ceil(np.sqrt(num_terms)))
        nrows = int(np.ceil(num_terms/ncols))

        fig, axes = plt.subplots(
            figsize = (10, 7), 
            nrows=nrows, 
            ncols=ncols,
            squeeze=False,
        )
        row = 0
        col = 0
        axes_so_far = 0

        cm_subsection = np.linspace(0,0.8,num_terms)
#        colours = [ cm.magma(x) for x in cm_subsection ]
        colours = [ cm.Paired(x) for x in cm_subsection ]

        parameters = {}

        for t in terms:
            parameters[t] = {}

            for e in epochs:
                parameters[t][e] = []

        for i in range( len( parameters_for_this_name )):
            track_params =  parameters_for_this_name[i]
            for t in terms:
                for e in epochs:
                    parameters[t][e].append( track_params[t][e] )

        avg_parameters = {}
        std_devs = {}
        for p in terms :
            avg_parameters[p] = {}
            std_devs[p] = {}

            for e in epochs:
                avg_parameters[p][e] = np.median(parameters[p][e])
                std_devs[p][e] = np.std(parameters[p][e])

        for term in sorted(terms):
            ax = axes[row, col]
            axes_so_far += 1
            col += 1
            if (row==0 and col==ncols):
                leg=True
            else:
                leg=False

            if col == ncols:
                col=0
                row+=1
            # latex_terms[term] = DataBase.latex_name_ising(term)
            latex_terms[term] = UserFunctions.get_latex_name(
                name=term,
                growth_generator = growth_rules[name]
            )
            averages = np.array( 
                [ avg_parameters[term][e] for e in epochs  ]
            )
            standard_dev = np.array(
                [ std_devs[term][e] for e in epochs]
            )
            
            try:
                true_val = true_params_dict[term]
                # true_term_latex = DataBase.latex_name_ising(term)
                true_term_latex = UserFunctions.get_latex_name(
                    name = term,
                    growth_generator = growth_generator
                )
                ax.axhline(
                    true_val, 
                    # label=str(true_term_latex+ ' True'), 
                    # color=colours[terms.index(term)]
                    label=str('True value'), 
                    color='black'

                )
            except:
                pass

            ax.axhline(
                0, 
                linestyle='--', 
                alpha=0.5, 
                color='black', 
                label='0'
            )
            ptq.fill_between_sigmas(
                ax, 
                parameters[term], 
                # [e +1 for e in epochs],
                epochs, 
                legend=leg
            )
            
            ax.scatter(
                [e +1 for e in epochs],
#                epochs, 
                averages, 
                s=max(1,50/num_experiments),
                label=latex_terms[term],
                # color=colours[terms.index(term)]
                color='black'
            )

            # latex_term = DataBase.latex_name_ising(term)
            latex_term = UserFunctions.get_latex_name(
                name = term,
                growth_generator = growth_rules[name]
            )
            # latex_term = latex_terms[term]
            ax.set_title(str(latex_term))
            
        """
        plot_title= str(
            'Average Parameter Estimates '+ 
            # str(DataBase.latex_name_ising(name)) +
            ' [' +
            str(num_wins_for_name) + # TODO - num times this model won 
            ' instances].'
        )
        ax.set_ylabel('Parameter Esimate')
        ax.set_xlabel('Experiment')
        plt.title(plot_title)
        ax.legend(
            loc='center left', 
            bbox_to_anchor=(1, 0.5), 
            title='Parameter'
        )    
        """
        
        latex_name = UserFunctions.get_latex_name(
            name=name,
            growth_generator = growth_rules[name]
        )

        if save_to_file is not None:
            fig.suptitle(
                'Parameter Esimates for {}'.format(latex_name)
            )
            save_file=''
            if save_to_file[-4:] == '.png':
                partial_name = save_to_file[:-4]
                save_file = str(partial_name + '_' + name + '.png')
            else:
                save_file = str(save_to_file + '_' + name + '.png')
            # plt.tight_layout()
            fig.tight_layout(rect=[0, 0.03, 1, 0.95])
            plt.savefig(save_file, bbox_inches='tight')


def Bayes_t_test(
    directory_name, 
    dataset, 
    results_path,
    results_file_name_start='results',
    use_experimental_data=False,
    true_expectation_value_path=None,
    growth_generator = None, 
    plot_probe_file = None,
    top_number_models=2,
    save_true_expec_vals_alone_plot=True,
    save_to_file=None
):
    plt.switch_backend('agg')
    print("Drawing avg expectation values from file:", results_path)
    from matplotlib import cm
    from scipy import stats

    
    results = pandas.DataFrame.from_csv(
        results_path,
        index_col='QID'
    )

    all_winning_models = list(results.loc[:, 'NameAlphabetical'])
    rank_models = lambda n:sorted(set(n), key=n.count)[::-1] 
    # from https://codegolf.stackexchange.com/questions/17287/sort-the-distinct-elements-of-a-list-in-descending-order-by-frequency
    
    if len(all_winning_models) > top_number_models:
        winning_models = rank_models(all_winning_models)[0:top_number_models]
    else:
        winning_models = list(set(all_winning_models))    


    cm_subsection = np.linspace(0,0.8,len(winning_models))
    colours = [ cm.viridis(x) for x in cm_subsection ]
    # colours = [ cm.Spectral(x) for x in cm_subsection ]

    # Relies on Results folder structure -- not safe?!
    # ie ExperimentalSimulations/Results/Sep_10/14_32/results_001.p, etc
    if use_experimental_data == True:
        os.chdir(directory_name)
        os.chdir("../../../../ExperimentalSimulations/Data/")
        experimental_measurements = pickle.load(
            open(str(dataset), 'rb')
        )
    elif true_expectation_value_path is not None:
        experimental_measurements = pickle.load(
            open(str(true_expectation_value_path), 'rb')
        )
    else:
        print("Either set \
            use_experimental_data=True or \
            provide true_expectation_value_path"
        )
        return False

    expectation_values_by_name = {}
    os.chdir(directory_name)
    pickled_files = []
    for file in os.listdir(directory_name):
        # if file.endswith(".p") and file.startswith("results"):
        if (
            file.endswith(".p") 
            and 
            file.startswith(results_file_name_start)
        ):
            pickled_files.append(file)

    growth_rules = {}
    for f in pickled_files:
        fname = directory_name+'/'+str(f)
        result = pickle.load(open(fname, 'rb'))
        alph = result['NameAlphabetical']
        expec_values = result['ExpectationValues']

        if alph in expectation_values_by_name.keys():
            expectation_values_by_name[alph].append(expec_values)
        else:
            expectation_values_by_name[alph] = [expec_values]

        if alph not in list(growth_rules.keys()):
            growth_rules[alph] = result['GrowthGenerator']


    # expectation_values = {}
    # for t in list(experimental_measurements.keys()):
    #     expectation_values[t] = []
    true_model = UserFunctions.default_true_operators_by_generator[
        growth_generator
    ]

    success_rate_by_term = {}
    nmod = len(winning_models)  
    ncols = int(np.ceil(np.sqrt(nmod)))
    nrows = int(np.ceil(nmod/ncols)) + 1 # 1 extra row for "master"

    # fig = plt.figure()
    # ax = plt.subplot(111)

    # fig, axes = plt.subplots(
    #     figsize = (20, 10), 
    #     nrows=nrows, 
    #     ncols=ncols,
    #     squeeze=False,
    #     sharex='col',
    #     sharey='row'
    # )

    fig = plt.figure(
        figsize = (15, 8), 
        # constrained_layout=True,
        tight_layout=True
    )
    from matplotlib.gridspec import GridSpec
    gs = GridSpec(
        nrows, 
        ncols, 
        # figure=fig # not available on matplotlib 2.1.1 (on BC)
    )

    row = 1
    col = 0

    axes_so_far = 1
    # full_plot_axis = axes[0,0]
    full_plot_axis = fig.add_subplot(gs[0,:])
    # i=0


    for term in winning_models:
        # plt.clf()
        # ax.clf()
        # ax = axes[row, col]
        ax = fig.add_subplot(gs[row, col])
        expectation_values = {}
        num_sets_of_this_name = len(
            expectation_values_by_name[term]
        )
        for i in range(num_sets_of_this_name):
            learned_expectation_values = (
                expectation_values_by_name[term][i]
            )

            for t in list(experimental_measurements.keys()):
                try:
                    expectation_values[t].append(
                        learned_expectation_values[t]
                    )
                except:
                    try:
                        expectation_values[t] = [
                            learned_expectation_values[t]
                        ]
                    except:
                        # if t can't be found, move on
                        pass

        means = {}
        std_dev = {}
        true = {}
        t_values = {}
        # times = sorted(list(experimental_measurements.keys()))
        true_times = sorted(list(expectation_values.keys()))
        times = sorted(list(expectation_values.keys()))
        flag=True
        one_sample=True
        for t in times:
            means[t] = np.mean(expectation_values[t])
            std_dev[t] = np.std(expectation_values[t])
            true[t] = experimental_measurements[t]
            if num_sets_of_this_name > 1:
                expec_values_array = np.array(
                    [ [i] for i in expectation_values[t]]
                )
                # print("shape going into ttest:", np.shape(true_expec_values_array))
                if use_experimental_data==True:
                    t_val = stats.ttest_1samp( 
                        expec_values_array, # list of expec vals for this t
                        true[t], # true expec val of t
                        axis=0, 
                        nan_policy='omit'
                    )
                else:
                    true_dist = stats.norm.rvs(
                        loc = true[t],
                        scale=0.001,
                        size=np.shape(expec_values_array)
                    )
                    t_val = stats.ttest_ind( 
                        expec_values_array, # list of expec vals for this t
                        true_dist, # true expec val of t
                        axis=0, 
                        nan_policy='omit'
                    )


                # if flag==True and t>0:
                #     print("t=", t)
                #     print("true:", expec_values_array)
                #     print("true", true[t])
                #     print("t_val:", t_val)
                #     flag=False

                if np.isnan(float(t_val[1]))==False:
                    # t_values[t] = 1-t_val[1]
                    t_values[t] = t_val[1]
                else:
                    print("t_val is nan for t=",t)

        num_runs = num_sets_of_this_name # TODO should this be the number of times this model won???
        success_rate = 0

        for t in times: 

            true_likelihood = true[t]
            mean = means[t]
            std = std_dev[t]
            credible_region = ( 2/np.sqrt(num_runs) ) * std

            if (
                ( true_likelihood  < (mean + credible_region) )
                and
                ( true_likelihood > (mean - credible_region) ) 
            ):
                success_rate += 1/len(times)

        mean_exp = np.array( [means[t] for t in times] )
        std_dev_exp = np.array( [std_dev[t] for t in times] )
        # name=DataBase.latex_name_ising(term)
        name=UserFunctions.get_latex_name(
            name = term,
            growth_generator = growth_rules[term]
        )
        description = str(
                name + 
                ' (' + str(num_sets_of_this_name)  + ')'
            )
        if term == true_model:
            description += ' (True)'

        description_w_bayes_t_value = str(
                name + ' : ' + 
                str(round(success_rate, 2)) + 
                ' (' + str(num_sets_of_this_name)  + ').'
            )


#        ax.errorbar(times, mean_exp, xerr=std_dev_exp, label=description)
        # if num_sets_of_this_name > 1:
        #     bayes_t_values_avail_times = sorted(list(t_values.keys()))
        #     bayes_t_values = [t_values[t] for t in bayes_t_values_avail_times]
        #     median_b_t_val = np.median(bayes_t_values)
        #     # print("Bayes t values:", bayes_t_values)

        #     ax.plot(
        #         bayes_t_values_avail_times, 
        #         bayes_t_values,
        #         label=str(
        #             'Bayes t-value (median '+ 
        #             str(np.round(median_b_t_val,2))+
        #             ')'
        #         ),
        #         color=colours[winning_models.index(term)],
        #         linestyle='--',
        #         alpha=0.3
        #     )

        ax.plot(
            times, 
            mean_exp, 
            c = colours[winning_models.index(term)],
            label=description
        )
        ax.fill_between(
            times, 
            mean_exp-std_dev_exp, 
            mean_exp+std_dev_exp, 
            alpha=0.2,
            facecolor = colours[winning_models.index(term)],
        )
        ax.set_ylim(0,1)
        ax.set_xlim(0,max(times))

        success_rate_by_term[term] = success_rate

        # plt.title('Mean Expectation Values')
        # plt.xlabel('Time')
        # plt.ylabel('Expectation Value')
        # true_exp = [true[t] for t in times]
        # ax.set_xlim(0,1)
        # plt.xlim(0,1)


        ax.set_title('Mean Expectation Values')
        # if col == 0:
        #     ax.set_ylabel('Expectation Value')
        # if row == nrows-1:
        #     ax.set_xlabel('Time')
        true_exp = [true[t] for t in times]
        # ax.set_xlim(0,1)
        # plt.xlim(0,1)

        ax.scatter(
            times, 
            true_exp, 
            color='r', 
            s=5, 
            label='True Expectation Value'
        )
        ax.plot(
            times, 
            true_exp, 
            color='r', 
            alpha = 0.3
        )

        # ax.legend(
        #     loc='center left', 
        #     bbox_to_anchor=(1, 0.5), 
        #     title=' Model : Bayes t-test (instances)'
        # )    
        
        # fill in "master" plot

        high_level_label = str(name)
        if term == true_model:
            high_level_label += ' (True)'


        full_plot_axis.plot(
            times, 
            mean_exp, 
            c = colours[winning_models.index(term)],
            label=high_level_label
        )
        """
        full_plot_axis.fill_between(
            times, 
            mean_exp-std_dev_exp, 
            mean_exp+std_dev_exp, 
            alpha=0.2,
            facecolor = colours[winning_models.index(term)],
        )
        """
        if axes_so_far == 1:
            full_plot_axis.scatter(
                times, 
                true_exp, 
                color='r', 
                s=5, 
                label='True Expectation Value'
            )
            full_plot_axis.plot(
                times, 
                true_exp, 
                color='r', 
                alpha = 0.3
            )
        full_plot_axis.legend(
            loc='center left', 
            bbox_to_anchor=(1, 0), 
        )
        # full_plot_axis.legend(
        #     ncol = ncols,
        #     loc='lower center', 
        #     bbox_to_anchor=(0.5, -1.3), 
        # )
        full_plot_axis.set_ylim(0,1)
        full_plot_axis.set_xlim(0,max(times))

        axes_so_far += 1
        col += 1
        if col == ncols:
            col=0
            row+=1
        # ax.set_title(str(name))
        ax.set_title(description)


        # if save_to_file is not None:
        #     save_file=''
        #     # save_file = save_to_file[:-4]
        #     save_file = str(
        #         save_to_file[:-4]+
        #         '_'+
        #         str(term) + '.png'
        #     )
        #     print("Saving to ",save_file )
        #     plt.savefig(save_file, bbox_inches='tight')

    # fig.set_xlabel('Time')
    # fig.set_ylabel('Expectation Value')

    fig.text(0.45, -0.04, 'Time', ha='center')
    fig.text(-0.04, 0.5, 'Expectation Value', va='center', rotation='vertical')
    
    if save_to_file is not None:
        fig.suptitle("Expectation Values of learned models.")
        # fig.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.savefig(save_to_file, bbox_inches='tight')


    # Also save an image of the true expectation values without overlaying results
    if save_true_expec_vals_alone_plot == True:
        plt.clf()
        # plt.scatter(
        #     times, 
        #     true_exp, 
        #     color='r', 
        #     s=5, 
        #     label='True Expectation Value'
        # )
        plt.plot(
            times, 
            true_exp, 
            marker='o',
            color='r', 
            label='True System'
            # alpha = 0.3
        )
        plt.xlabel('Time')
        plt.ylabel('Expectation Value')
        plt.legend()
        true_only_fig_file = str(
            save_to_file[:-4]
            + '_true_expec_vals.png'
        )
        plt.title("Expectation Values of True model.")
        plt.savefig(
            true_only_fig_file,
            bbox_inches='tight'
        )

# def fill_between_sigmas(
#     ax, 
#     distribution, 
#     times, 
#     legend=False,
#     only_one_sigma = True, 
# ):
#     # to draw distributions on a given axis, ax.
#     # where distribution must be a dict
#     # distribution[t] = [...], a list of values for the distribution at that time
    
#     sigmas = { # standard sigma values 
#         1 : 34.13,
#         2 : 13.59,
#         3 : 2.15, 
#         4 : 0.1,
#     }

#     upper_one_sigma = [np.percentile(np.array(distribution[t]), 50 + sigmas[1]) for t in times] 
#     lower_one_sigma = [np.percentile(np.array(distribution[t]), 50 - sigmas[1]) for t in times] 
#     upper_two_sigma = [np.percentile(np.array(distribution[t]), 50 + sigmas[1] + sigmas[2]) for t in times] 
#     lower_two_sigma = [np.percentile(np.array(distribution[t]), 50 - sigmas[1] - sigmas[2]) for t in times] 
#     upper_three_sigma = [np.percentile(np.array(distribution[t]), 50 + sigmas[1] + sigmas[2] + sigmas[3]) for t in times] 
#     lower_three_sigma = [np.percentile(np.array(distribution[t]), 50 - sigmas[1] - sigmas[2] - sigmas[3]) for t in times] 
#     upper_four_sigma = [np.percentile(np.array(distribution[t]),  50 + sigmas[1] + sigmas[2] + sigmas[3] + sigmas[4]) for t in times] 
#     lower_four_sigma = [np.percentile(np.array(distribution[t]),  50 - sigmas[1] - sigmas[2] - sigmas[3] - sigmas[4]) for t in times] 

#     fill_alpha = 0.2
#     one_sigma_colour='green'
#     two_sigma_colour='red'
#     three_sigma_colour='blue'
#     four_sigma_colour='orange'
#     ax.fill_between(
#         # times, 
#         [t+1 for t in times],
#         upper_one_sigma, 
#         lower_one_sigma, 
#         alpha=fill_alpha,
#         facecolor=one_sigma_colour,
#         label='$1 \sigma$ '
#     )


#     if only_one_sigma == False:
#         ax.fill_between(
#             # times, 
#             [t+1 for t in times],
#             upper_two_sigma,
#             upper_one_sigma, 
#             alpha=fill_alpha,
#             facecolor=two_sigma_colour,
#             label='$2 \sigma$ '
#         )
#         ax.fill_between(
#             # times, 
#             [t+1 for t in times],
#             lower_one_sigma, 
#             lower_two_sigma,
#             alpha=fill_alpha,
#             facecolor=two_sigma_colour,
#         )

#         ax.fill_between(
#             # times, 
#             [t+1 for t in times],
#             upper_three_sigma,
#             upper_two_sigma, 
#             alpha=fill_alpha,
#             facecolor=three_sigma_colour,
#             label='$3 \sigma$ '
#         )
#         ax.fill_between(
#             # times, 
#             [t+1 for t in times],
#             lower_two_sigma, 
#             lower_three_sigma,
#             alpha=fill_alpha,
#             facecolor=three_sigma_colour,
#         )

#         ax.fill_between(
#             # times, 
#             [t+1 for t in times],
#             upper_four_sigma,
#             upper_three_sigma, 
#             alpha=fill_alpha,
#             facecolor=four_sigma_colour,
#             label='$4 \sigma$ '
#         )
#         ax.fill_between(
#             # times, 
#             [t+1 for t in times],
#             lower_three_sigma, 
#             lower_four_sigma,
#             alpha=fill_alpha,
#             facecolor=four_sigma_colour,
#         )

#     if legend==True:
#         ax.legend(
#             loc='center right', 
#             bbox_to_anchor=(1.5, 0.5), 
# #             title=''
#         )



def r_sqaured_average(
    results_path, 
    top_number_models=2,
    save_to_file=None
):
    from matplotlib import cm
    plt.clf()
    fig = plt.figure()
    ax = plt.subplot(111)

    results = pandas.DataFrame.from_csv(
        results_path,
        index_col='QID'
    )
    all_winning_models = list(results.loc[:, 'NameAlphabetical'])
    rank_models = lambda n:sorted(set(n), key=n.count)[::-1] 
    # from https://codegolf.stackexchange.com/questions/17287/sort-the-distinct-elements-of-a-list-in-descending-order-by-frequency
    
    if len(all_winning_models) > top_number_models:
        winning_models = rank_models(all_winning_models)[0:top_number_models]
    else:
        winning_models = list(set(all_winning_models))    

    names = winning_models
    num_models = len(names)
    cm_subsection = np.linspace(0,0.8,num_models)
    #        colours = [ cm.magma(x) for x in cm_subsection ]
    colours = [ cm.viridis(x) for x in cm_subsection ]

    i=0
    for i in range(len(names)):
        name = names[i]
        r_squared_values = list(
            results[ results['NameAlphabetical']==name]['RSquaredByEpoch']
        )

        r_squared_lists = {}
        num_wins = len(r_squared_values)
        for j in range(num_wins):
            rs = eval(r_squared_values[j])
            for t in list(rs.keys()):
                try:
                    r_squared_lists[t].append(rs[t])
                except:
                    r_squared_lists[t] = [rs[t]]

        times = sorted(list(r_squared_lists.keys()))
        means = np.array(
            [ np.mean(r_squared_lists[t]) for t in times]
        )

        std_dev = np.array(
            [ np.std(r_squared_lists[t]) for t in times]
        )

        # term = DataBase.latex_name_ising(name)
        term = UserFunctions.get_latex_name(
            name = name,
            growth_generator = growth_generator 
        )
        plot_label = str(term + ' ('+ str(num_wins) + ')')
        colour = colours[ i ]
        ax.plot(
            times, 
            means,
            label=plot_label,
            marker='o'
        )
        ax.fill_between(
            times, 
            means-std_dev,
            means+std_dev,
            alpha=0.2
        )
        ax.legend(
            bbox_to_anchor=(1.0, 0.9), 
            title='Model (# instances)'
        )
    plt.xlabel('Epoch')
    plt.ylabel('$R^2$')
    plt.title('$R^2$ average')

    if save_to_file is not None:
        plt.savefig(save_to_file, bbox_inches='tight')



def volume_average(
    results_path, 
    top_number_models=2,
    save_to_file=None
):
    from matplotlib import cm
    plt.clf()
    fig = plt.figure()
    ax = plt.subplot(111)

    results = pandas.DataFrame.from_csv(
        results_path,
        index_col='QID'
    )
    all_winning_models = list(results.loc[:, 'NameAlphabetical'])
    rank_models = lambda n:sorted(set(n), key=n.count)[::-1] 
    # from https://codegolf.stackexchange.com/questions/17287/sort-the-distinct-elements-of-a-list-in-descending-order-by-frequency
    
    if len(all_winning_models) > top_number_models:
        winning_models = rank_models(all_winning_models)[0:top_number_models]
    else:
        winning_models = list(set(all_winning_models))    

    names = winning_models
    num_models = len(names)
    cm_subsection = np.linspace(0,0.8,num_models)
    #        colours = [ cm.magma(x) for x in cm_subsection ]
    colours = [ cm.viridis(x) for x in cm_subsection ]

    i=0
    for i in range(len(names)):
        name = names[i]
        volume_values = list(
            results[ results['NameAlphabetical']==name]['TrackVolume']
        )

        volume_lists = {}
        num_wins = len(volume_values)
        for j in range(num_wins):
            rs = eval(volume_values[j])
            for t in list(rs.keys()):
                try:
                    volume_lists[t].append(rs[t])
                except:
                    volume_lists[t] = [rs[t]]

        times = sorted(list(volume_lists.keys()))
        means = np.array(
            [ np.mean(volume_lists[t]) for t in times]
        )

        std_dev = np.array(
            [ np.std(volume_lists[t]) for t in times]
        )

        # term = DataBase.latex_name_ising(name)
        term = UserFunctions.get_latex_name(
            name = name,
            growth_generator = growth_generator 
        )
        plot_label = str(term + ' ('+ str(num_wins) + ')')
        colour = colours[ i ]
        ax.plot(
            times, 
            means,
            label=plot_label,
            marker='o',
            markevery=10
        )
        ax.fill_between(
            times, 
            means-std_dev,
            means+std_dev,
            alpha=0.2
        )
        ax.legend(
            bbox_to_anchor=(1.0, 0.9), 
            title='Model (# instances)'
        )
    plt.semilogy()
    plt.xlabel('Epoch')
    plt.ylabel('Volume')
    plt.title('Volume average')

    if save_to_file is not None:
        plt.savefig(save_to_file, bbox_inches='tight')


def all_times_learned_histogram(
    results_path = "summary_results.csv",
    top_number_models=2,
    save_to_file=None
):
    print("\n\n\n[ANALYSE] all_times_learned_histogram",
        "saving to:", save_to_file
    )
    from matplotlib import cm
    plt.clf()
    fig = plt.figure()
    ax = plt.subplot(111)

    results = pandas.DataFrame.from_csv(
        results_path,
        index_col='QID'
    )
    all_winning_models = list(results.loc[:, 'NameAlphabetical'])
    rank_models = lambda n:sorted(set(n), key=n.count)[::-1] 
    # from https://codegolf.stackexchange.com/questions/17287/sort-the-distinct-elements-of-a-list-in-descending-order-by-frequency

    if len(all_winning_models) > top_number_models:
        winning_models = rank_models(all_winning_models)[0:top_number_models]
    else:
        winning_models = list(set(all_winning_models))    

    names = winning_models
    num_models = len(names)
    cm_subsection = np.linspace(0,0.8,num_models)
    #        colours = [ cm.magma(x) for x in cm_subsection ]
    colours = [ cm.viridis(x) for x in cm_subsection ]
    print("[Time histogram] names:", names)
    print("[Time histogram] colours:", colours)

    times_by_model = {}
    max_time = 0
    for i in range(len(names)):
        name = names[i]
        model_colour = colours[i]
        times_by_model[name] = []
        this_model_times_separate_runs = list(
            results[ results['NameAlphabetical']==name]['TrackTimesLearned']
        )

        num_wins = len(this_model_times_separate_runs)
        for j in range(num_wins):
            this_run_times = eval(this_model_times_separate_runs[j])
            times_by_model[name].extend(this_run_times)
            if max(this_run_times) > max_time:
                max_time = max(this_run_times)
        times_this_model = times_by_model[name]
        model_label = str(
            list(results[results['NameAlphabetical']==name]['ChampLatex'])[0]
        )

        plt.hist(
            times_this_model,
            color=model_colour,
            # histtype='stepfilled',
            histtype='step',
            # histtype='bar',
            fill=False,
            label=model_label
        )

    # presuming all models used same heuristics .... TODO change if models can use ones
    heuristic_type = list(results[results['NameAlphabetical']==names[0]]['Heuristic'])[0]

    plt.legend()    
    plt.title("Times learned on [{}]".format(heuristic_type))
    plt.xlabel("Time")
    plt.ylabel("Frequency")
    plt.show()
    plt.semilogy()
    if max_time > 100:
        plt.semilogx()
    if save_to_file is not None:
        plt.savefig(save_to_file, bbox_inches='tight')




        
def model_scores(directory_name):
#    sys.path.append(directory_name)

    os.chdir(directory_name)

    scores = {}
    growth_rules = {}

    pickled_files = []
    for file in os.listdir(directory_name):
        if file.endswith(".p") and file.startswith("results"):
            pickled_files.append(file)
    
    for f in pickled_files:
        fname = directory_name+'/'+str(f)
        result = pickle.load(open(fname, 'rb'))
        alph = result['NameAlphabetical']

        if alph in scores.keys():
            scores[alph] += 1
        else:
            scores[alph] = 1

        if alph not in list(growth_rules.keys()):
            growth_rules[alph] = result['GrowthGenerator']

    return scores, growth_rules

def get_entropy(
    models_points, 
    growth_generator=None,
    inf_gain=False
):
    # TODO this calculation of entropy may not be correct
    # What is initial_entropy meant to be?
    num_qmd_instances = sum(list(models_points.values()))
    num_possible_qmd_instances = len(
        # ptq.ising_terms_rotation_hyperfine()
        UserFunctions.get_all_model_names(
            growth_generator = growth_generator,
            return_branch_dict = 'latex_terms'
        )
    )
    # TODO don't always want ising terms only

    
    model_fractions = {}
    for k in list(models_points.keys()):
        model_fractions[k] = models_points[k]/num_qmd_instances    
    
    initial_entropy = -1*np.log2(1/num_possible_qmd_instances)
    entropy = 0
    for i in list(models_points.keys()):
        success_prob = model_fractions[i]
        partial_entropy = success_prob * np.log2(success_prob)
        if np.isnan(partial_entropy):
            partial_entropy = 0 
        entropy -= partial_entropy
    
    if inf_gain:
        # information gain is entropy loss
        information_gain =  initial_entropy - entropy
        return information_gain
    else:
        return entropy


def plot_scores(
        scores, 
        growth_rules, 
        entropy=None,
        inf_gain=None, 
        true_operator = None, 
        growth_generator = None,
        batch_nearest_num_params_as_winners = True,
        save_file='model_scores.png'
    ):
    plt.clf()
    models = list(scores.keys())

    
    latex_true_op = UserFunctions.get_latex_name(
            name=true_operator, 
            growth_generator=growth_generator
    )   

    latex_model_names = [
        # DataBase.latex_name_ising(model) for model in models
        UserFunctions.get_latex_name(
            name=model, 
            growth_generator=growth_rules[model]
        ) for model in models
    ]

    batch_correct_models = []
    if batch_nearest_num_params_as_winners == True:
        num_true_params = len(
            DataBase.get_constituent_names_from_name(
                true_operator
            )
        )
        for mod in models:
            num_params = len(
                DataBase.get_constituent_names_from_name(mod)
            )

            if (
                num_true_params - num_params == 1
            ):
                # must be exactly one parameter smaller
                batch_correct_models.append(
                    mod
                )

    mod_scores = scores
    scores = list(scores.values())
    num_runs = sum(scores)
    fig, ax = plt.subplots()    
    width = 0.75 # the width of the bars 
    ind = np.arange(len(scores))  # the x locations for the groups
    colours = ['blue' for i in ind]
    batch_success_rate = correct_success_rate = 0
    for mod in batch_correct_models: 
        mod_latex = UserFunctions.get_latex_name(
            name=mod, 
            growth_generator=growth_rules[mod]
        ) 
        mod_idx = latex_model_names.index(mod_latex)
        colours[mod_idx] = 'orange'
        batch_success_rate += mod_scores[mod]
    if true_operator in models:
        batch_success_rate += mod_scores[true_operator]
        correct_success_rate = mod_scores[true_operator]

    batch_success_rate /= num_runs
    correct_success_rate /= num_runs
    batch_success_rate *= 100
    correct_success_rate *= 100 #percent


    try:
        true_idx = latex_model_names.index(
            latex_true_op
        )
        colours[true_idx] = 'green'

    except:
        # print(
        #     "[plot_scores]",
        #     "True model", 
        #     latex_true_op, 
        #     "not in ", 
        #     latex_model_names
        # )
        # raise
        pass


    # ax.barh(ind, scores, width, color="blue")
    ax.barh(ind, scores, width, color=colours)
    ax.set_yticks(ind+width/2)
    ax.set_yticklabels(latex_model_names, minor=False)
    custom_lines = [
        Line2D([0], [0], color='green', lw=4),
        Line2D([0], [0], color='orange', lw=4),
        Line2D([0], [0], color='blue', lw=4),
    ]
    custom_handles = [
        'True ({}%)'.format(int(correct_success_rate)), 
        'True/Close ({}%)'.format(int(batch_success_rate)), 
        'Other'
    ]
    
    plot_title = str(
        'Number of QMD instances won by models.' 
    )

    if entropy is not None:
        plot_title += str( 
            '\n$\mathcal{S}$=' 
            + str(round(entropy, 2))
        )
    if inf_gain is not None:
        plot_title += str(
            '\t $\mathcal{IG}$=' 
            + str(round(inf_gain, 2))
        )
    plt.legend(custom_lines, custom_handles)
    plt.title(plot_title)
    plt.ylabel('Model')
    plt.xlabel('Number of wins')
    #plt.bar(scores, latex_model_names)
    
    plt.savefig(save_file, bbox_inches='tight')
    
    
def plot_tree_multi_QMD(
        results_csv, 
        all_bayes_csv, 
        latex_mapping_file,
        avg_type='medians',
        growth_generator=None,
        entropy=None, 
        inf_gain=None, 
        save_to_file=None
    ):
    qmd_res = pandas.DataFrame.from_csv(
        results_csv, 
        index_col='LatexName'
    )
    mods = list(qmd_res.index)
    winning_count = {}
    for mod in mods:
        winning_count[mod]=mods.count(mod)

    ptq.cumulativeQMDTreePlot(
        cumulative_csv=all_bayes_csv, 
        wins_per_mod=winning_count,
        latex_mapping_file=latex_mapping_file, 
        growth_generator=growth_generator,
        only_adjacent_branches=False, 
        avg=avg_type, entropy=entropy, inf_gain=inf_gain,
        save_to_file=save_to_file
    )        



parser = argparse.ArgumentParser(description='Pass variables for (I)QLE.')

# Add parser arguments, ie command line arguments for QMD
## QMD parameters -- fundamentals such as number of particles etc
parser.add_argument(
    '-dir', '--results_directory', 
    help="Directory where results of multiple QMD are held.",
    type=str,
    default=os.getcwd()
)

parser.add_argument(
    '-bcsv', '--bayes_csv', 
    help="CSV given to QMD to store all Bayes factors computed.",
    type=str,
    default=os.getcwd()
)

parser.add_argument(
    '-top', '--top_number_models', 
    help="N, for top N models by number of QMD wins.",
    type=int,
    default=3
)

parser.add_argument(
    '-qhl', '--qhl_mode', 
    help="Whether QMD is being used in QHL mode.",
    type=int,
    default=0
)

parser.add_argument(
    '-fqhl', '--further_qhl_mode', 
    help="Whether in further QHL stage.",
    type=int,
    default=0
)
# parser.add_argument(
#     '-data', '--dataset', 
#     help="Which dataset QMD was run using..",
#     type=str,
#     default='NVB_dataset'
# )

parser.add_argument(
    '-params', '--true_params',
    help="Path to pickled true params info.",
    type=str,
    default=None
)


parser.add_argument(
    '-true_expec', '--true_expectation_value_path',
    help="Path to pickled true expectation values.",
    type=str,
    default=None
)

parser.add_argument(
    '-exp', '--use_experimental_data',
    help="Bool: whether or not to use experimental data.",
    type=int,
    default=0
)

parser.add_argument(
    '-ggr', '--growth_generation_rule',
    help='Rule applied for generation of new models during QMD. \
    Corresponding functions must be built into ModelGeneration',
    type=str,
    default=None
)

# parser.add_argument(
#   '-meas', '--measurement_type',
#   help='Which measurement type to use. Must be written in Evo.py.',
#   type=str,
#   default='full_access'
# )

parser.add_argument(
    '-latex', '--latex_mapping_file',
    help='File path to save tuples which give model \
        string names and latex names.',
    type=str,
    default=None
)
parser.add_argument(
  '-plot_probes', '--plot_probe_file', 
  help="File to pickle probes against which to plot expectation values.",
  type=str,
  default=None
)
parser.add_argument(
  '-plus', '--force_plus_probe', 
  help="Whether to enforce plots to use |+>^n as probe.",
  type=int,
  default=0
)




arguments = parser.parse_args()
directory_to_analyse = arguments.results_directory
all_bayes_csv = arguments.bayes_csv
qhl_mode = bool(arguments.qhl_mode)
further_qhl_mode = bool(arguments.further_qhl_mode)
true_params_path = arguments.true_params
exp_data = arguments.use_experimental_data
true_expec_path = arguments.true_expectation_value_path
growth_generator = arguments.growth_generation_rule
dataset = UserFunctions.get_experimental_dataset(growth_generator)
latex_mapping_file = arguments.latex_mapping_file
plot_probe_file = arguments.plot_probe_file
force_plus_probe = bool(arguments.force_plus_probe)
measurement_type = UserFunctions.get_measurement_type(growth_generator)


if true_params_path is not None:
    true_params_info = pickle.load(
        open(
            true_params_path, 
            'rb'
        )
    )
    true_params_dict = true_params_info['params_dict']
    true_operator = true_params_info['true_op']
else:
    true_params_dict = None
    true_operator = UserFunctions.default_true_operators_by_generator[
        growth_generator
    ]

if exp_data is False:
    name = true_params_info['true_op']
    terms = DataBase.get_constituent_names_from_name(name)
    params=[]
    ops=[]
    for t in terms:
        params.append(true_params_dict[t])
        ops.append( DataBase.compute(t) )
        
    true_ham = np.tensordot(params, ops, axes=1)

#######################################
### Now analyse the results. 
#######################################
print("\nAnalysing and storing results in", directory_to_analyse)


if not directory_to_analyse.endswith('/'):
    directory_to_analyse += '/'


if further_qhl_mode==True:
    results_csv_name = 'summary_further_qhl_results.csv'
    results_csv = directory_to_analyse+results_csv_name
    results_file_name_start='further_qhl_results'
    ptq.summariseResultsCSV(
        directory_name=directory_to_analyse, 
        results_file_name_start=results_file_name_start,
        csv_name=results_csv
    )
    plot_desc='further_'

else:
    results_csv_name = 'summary_results.csv'
    results_csv = directory_to_analyse+results_csv_name
    results_file_name_start='results'
    ptq.summariseResultsCSV(
        directory_name=directory_to_analyse, 
        results_file_name_start=results_file_name_start,
        csv_name=results_csv
    )
    plot_desc=''

try:
    average_priors = average_parameters(
        results_path=results_csv,
        top_number_models = arguments.top_number_models 
    )

    avg_priors = str(directory_to_analyse+'average_priors.p')

    pickle.dump(
        average_priors,
        open(avg_priors, 'wb'), 
        protocol=2
    )
except:
    # for compatability with old versions
    pass

average_parameter_estimates(
    directory_name = directory_to_analyse, 
    results_path = results_csv, 
    top_number_models = arguments.top_number_models,
    results_file_name_start=results_file_name_start,
    growth_generator = growth_generator,
    true_params_dict = true_params_dict,
    save_to_file=  str(
        directory_to_analyse + 
        plot_desc + 
        'param_avg.png'
    )
)

# if exp_data:
Bayes_t_test( # average expected values
    directory_name = directory_to_analyse, 
    dataset = dataset, 
    results_path = results_csv,
    use_experimental_data = exp_data, 
    results_file_name_start = results_file_name_start,
    true_expectation_value_path = true_expec_path,
    growth_generator = growth_generator, 
    top_number_models = arguments.top_number_models,
    plot_probe_file = plot_probe_file,
    save_to_file=str(
        directory_to_analyse+
        plot_desc +
        'expec_vals.png'
    )
)

r_sqaured_average(
    results_path = results_csv,
    top_number_models = arguments.top_number_models,
    save_to_file=  str(
        directory_to_analyse + 
        plot_desc +
        'r_squared_averages.png'
    )
)

ptq.average_quadratic_losses(
    results_path = results_csv, 
    growth_generator = growth_generator, 
    top_number_models = arguments.top_number_models,
    save_to_file=  str(
        directory_to_analyse + 
        plot_desc +
        'quadratic_losses_avg.png'
    )
)


volume_average(
    results_path = results_csv,
    top_number_models = arguments.top_number_models,
    save_to_file=  str(
        directory_to_analyse + 
        plot_desc +
        'volume_averages.png'
    )
)

all_times_learned_histogram(
    results_path = results_csv,
    top_number_models = arguments.top_number_models,
    save_to_file=  str(
        directory_to_analyse + 
        plot_desc +
        'times_histogram.png'
    )
)



"""

if qhl_mode==True:
    r_squared_plot = str(
        directory_to_analyse + 
        'r_squared_QHL.png'
    )
    ptq.r_squared_plot(
        results_csv_path = results_csv,
        save_to_file = r_squared_plot
    )
"""

if further_qhl_mode == False:
    print("FURTHER QHL=FALSE. PLOTTING STUFF")
    plot_file = directory_to_analyse+'model_scores.png'
    model_scores, growth_rules = model_scores(directory_to_analyse)
    
    print("GROWTH RULES:", growth_rules, "\n\n\n")
    try:
        entropy = get_entropy(model_scores, 
            growth_generator = growth_generator, 
            inf_gain=False
        )
        inf_gain = get_entropy(
            model_scores, 
            growth_generator  = growth_generator,
            inf_gain=True
        )
    except:
        entropy = inf_gain = 0.0
    plot_scores(
        scores = model_scores,
        entropy = entropy,
        true_operator = true_operator, 
        growth_generator = growth_generator,
        growth_rules = growth_rules, 
        inf_gain = inf_gain, 
        save_file = plot_file
    )
    try:
        ptq.plotTrueModelBayesFactors_IsingRotationTerms(
            results_csv_path = all_bayes_csv,
            # correct_mod='xTiPPyTiPPzTiPPxTxPPyTyPPzTz',
            correct_mod = true_operator,
            growth_generator = growth_generator,
            save_to_file = str(
                directory_to_analyse+
                'bayes_comparisons_true_model.png'
            )
        )
    except:
        print("Could not plot histogram of Bayes factors for True model.")
        # raise
    param_plot = str(directory_to_analyse+'sweep_param_total.png')
    param_percent_plot = str(directory_to_analyse+'sweep_param_percentage.png')

    try:
        parameter_sweep_analysis(
            directory_name = directory_to_analyse, 
            results_csv=results_csv, 
            save_to_file=param_plot)
        parameter_sweep_analysis(
            directory_name = directory_to_analyse,
            results_csv=results_csv,
            use_log_times=True,
            use_percentage_models=True, 
            save_to_file=param_percent_plot
        )
    except:
        print("Parameter sweep analysis failed.")
        pass

    do_clustering = True
    if do_clustering:
        try:
            ptq.cluster_results_and_plot(
                path_to_results = results_csv, 
                true_expec_path = true_expec_path, 
                plot_probe_path = plot_probe_file, 
                true_params_path = true_params_path,
                growth_generator = growth_generator, 
                measurement_type = measurement_type, 
                save_param_values_to_file = str(plot_desc + 'clusters_by_param.png'),
                save_param_clusters_to_file = str(plot_desc + 'clusters_by_model.png'),
                save_redrawn_expectation_values = str(plot_desc + 'clusters_expec_vals.png')
            )
        except:
            print("Failed to cluster and replot results.")
            pass
        # raise


    valid_growth_rules_for_multiQMD_tree_plot = [
        'two_qubit_ising_rotation',
        'two_qubit_ising_rotation_hyperfine', 
        'two_qubit_ising_rotation_hyperfine_transverse' ,
        'hyperfine_like'
    ]

    try:
        # if growth_generator in valid_growth_rules_for_multiQMD_tree_plot:

        plot_tree_multi_QMD(
            results_csv = results_csv, 
            latex_mapping_file=latex_mapping_file, 
            all_bayes_csv = all_bayes_csv, 
            growth_generator=growth_generator,
            entropy = entropy,
            inf_gain = inf_gain,
            save_to_file='multiQMD_tree.png'
        )
    except NameError:
        print("Can not plot multiQMD tree -- this might be because only \
            one instance of QMD was performed. All other plots generated \
            without error."
        )
        # raise

    except ZeroDivisionError:
        print("Can not plot multiQMD tree -- this might be because only \
            one instance of QMD was performed. All other plots generated \
            without error."
        )
        raise
    except:
        print("Could not plot Multi QMD tree.")
        # raise






