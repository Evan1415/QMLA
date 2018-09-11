import sys, os
import pickle
import matplotlib.pyplot as plt
import argparse
import numpy as np

import DataBase
import pandas
import PlotQMD as ptq


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

def parameter_sweep_analysis(directory_name, results_csv, save_to_file=None, use_log_times=False, use_percentage_models=False):

    import os, csv
    if not directory_name.endswith('/'):
        directory_name += '/'

    qmd_cumulative_results = pandas.DataFrame.from_csv(results_csv,
        index_col='ConfigLatex'
    )
    piv = pandas.pivot_table(qmd_cumulative_results, 
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
        
        
def average_parameters(results_path, 
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
    for mod in winning_models:
        params_dict[mod] = {}
        params = DataBase.get_constituent_names_from_name(mod)
        for p in params:
            params_dict[mod][p] = []

    for i in range(len(winning_models)):
        mod = winning_models[i]
        learned_parameters = list(results[ results['NameAlphabetical']==mod ]['LearnedParameters'])
        num_wins_for_mod = len(learned_parameters)
        for i in range(num_wins_for_mod):
            params = eval(learned_parameters[i])
            for k in list(params.keys()):
                params_dict[mod][k].append(params[k])

    average_params_dict = {}
    std_deviations = {}
    learned_priors = {}
    for mod in winning_models:
        average_params_dict[mod] = {}
        std_deviations[mod] = {}
        learned_priors[mod] = {}
        params = DataBase.get_constituent_names_from_name(mod)
        for p in params:
            if average_type == 'median':
                average_params_dict[mod][p] = np.median(
                    params_dict[mod][p]
                )
            else:
                average_params_dict[mod][p] = np.mean(
                    params_dict[mod][p]
                )
            if np.std(params_dict[mod][p]) > 0:                
                std_deviations[mod][p] = np.std(params_dict[mod][p])
            else:
                # if only one winner, give relatively broad prior. 
                std_deviations[mod][p] = 0.5 
            
            learned_priors[mod][p] = [
                average_params_dict[mod][p], 
                std_deviations[mod][p]
            ]
    
    return learned_priors        
        
def model_scores(directory_name):
#    sys.path.append(directory_name)

    os.chdir(directory_name)

    scores = {}

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
    return scores

def get_entropy(models_points, inf_gain=False):
    # TODO this calculation of entropy may not be correct
    # What is initial_entropy meant to be?
    num_qmd_instances = sum(list(models_points.values()))
    num_possible_qmd_instances = len(
        ptq.ising_terms_rotation_hyperfine()
    )
    # TODO don't always want ising terms only

    
    model_fractions = {}
    for k in list(models_points.keys()):
        model_fractions[k] = models_points[k]/num_qmd_instances    
    
    initial_entropy = np.log2(1/num_possible_qmd_instances)
    entropy = 0
    for i in list(models_points.keys()):
        success_prob = model_fractions[i]
        partial_entropy = success_prob * np.log2(success_prob)
        if np.isnan(partial_entropy):
            partial_entropy = 0 
        entropy -= partial_entropy
    
    if inf_gain:
        information_gain = initial_entropy - entropy
        return information_gain
    else:
        return entropy


def plot_scores(
        scores, 
        entropy=None,
        inf_gain=None, 
        save_file='model_scores.png'
    ):
    plt.clf()
    models = list(scores.keys())
    
    latex_model_names = [
        DataBase.latex_name_ising(model) for model in models
    ]

    scores = list(scores.values())

    fig, ax = plt.subplots()    
    width = 0.75 # the width of the bars 
    ind = np.arange(len(scores))  # the x locations for the groups
    ax.barh(ind, scores, width, color="blue")
    ax.set_yticks(ind+width/2)
    ax.set_yticklabels(latex_model_names, minor=False)
    
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

    plt.title(plot_title)
    plt.ylabel('Model')
    plt.xlabel('Number of wins')
    #plt.bar(scores, latex_model_names)
    
    plt.savefig(save_file, bbox_inches='tight')
    
    
def plot_tree_multi_QMD(
        results_csv, 
        all_bayes_csv, 
        avg_type='medians',
        entropy=None, 
        inf_gain=None, 
        save_to_file=None
    ):
#    res_csv="/home/bf16951/Dropbox/QML_share_stateofart/QMD/ExperimentalSimulations/Results/multtestdir/param_sweep.csv"
    qmd_res = pandas.DataFrame.from_csv(results_csv, index_col='LatexName')
    mods = list(qmd_res.index)
    winning_count = {}
    for mod in mods:
        winning_count[mod]=mods.count(mod)

    ptq.cumulativeQMDTreePlot(cumulative_csv=all_bayes_csv, 
        wins_per_mod=winning_count, only_adjacent_branches=True, 
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

arguments = parser.parse_args()
directory_to_analyse = arguments.results_directory
all_bayes_csv = arguments.bayes_csv
qhl_mode = bool(arguments.qhl_mode)

print("\nAnalysing and storing results in", directory_to_analyse)


if not directory_to_analyse.endswith('/'):
    directory_to_analyse += '/'

results_csv_name = 'param_sweep.csv'
results_csv = directory_to_analyse+results_csv_name
ptq.summariseResultsCSV(
    directory_name=directory_to_analyse, 
    csv_name=results_csv
)

if qhl_mode==True:
    r_squared_plot = str(directory_to_analyse + 'r_squared_QHL.png')
    ptq.r_squared_plot(
        results_csv_path = results_csv,
        save_to_file = r_squared_plot
    )
else:
    plot_file = directory_to_analyse+'model_scores.png'
    model_scores = model_scores(directory_to_analyse)
    entropy = get_entropy(model_scores, inf_gain=False)
    inf_gain = get_entropy(model_scores, inf_gain=True)
    plot_scores(
        scores = model_scores,
        entropy = entropy, 
        inf_gain = inf_gain, 
        save_file = plot_file
    )

    ptq.plotTrueModelBayesFactors_IsingRotationTerms(
        results_csv_path = all_bayes_csv,
        save_to_file = str(directory_to_analyse+'true_model_bayes_comparisons.png')
    )

    average_priors = average_parameters(
        results_path=results_csv,
        top_number_models = arguments.top_number_models 
    )
    pickle.dump(
        average_priors,
        open('average_priors.p', 'wb'), 
        protocol=2
    )
    param_plot = str(directory_to_analyse+'param_analysis_total.png')
    param_percent_plot = str(directory_to_analyse+'param_analysis_percentage.png')

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


    try:
        plot_tree_multi_QMD(results_csv = results_csv, 
            all_bayes_csv = all_bayes_csv, 
            entropy = entropy,
            inf_gain = inf_gain,
            save_to_file='multiQMD_tree.png'
        )

    except NameError:
        print("Can not plot multiQMD tree -- this might be because only \
            one instance of QMD was performed. All other plots generated \
            without error."
        )

    except ZeroDivisionError:
        print("Can not plot multiQMD tree -- this might be because only \
            one instance of QMD was performed. All other plots generated \
            without error."
        )





