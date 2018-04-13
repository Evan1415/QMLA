import sys, os
import pickle
import matplotlib.pyplot as plt
import argparse
import numpy as np

import DataBase

def model_scores(directory_name):
#    sys.path.append(directory_name)

    print("current:", os.getcwd())
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


def plot_scores(scores, save_file='model_scores.png'):
    plt.clf()
    models = list(scores.keys())
    
    latex_model_names = [DataBase.latex_name_ising(model) for model in models]
    scores = list(scores.values())


    fig, ax = plt.subplots()    
    width = 0.75 # the width of the bars 
    ind = np.arange(len(scores))  # the x locations for the groups
    ax.barh(ind, scores, width, color="blue")
    ax.set_yticks(ind+width/2)
    ax.set_yticklabels(latex_model_names, minor=False)
    
    plt.title('Number of QMD instances won by models')
    plt.ylabel('Model')
    plt.xlabel('Number of wins')
    #plt.bar(scores, latex_model_names)
    
    plt.savefig(save_file, bbox_inches='tight')
    

parser = argparse.ArgumentParser(description='Pass variables for (I)QLE.')

# Add parser arguments, ie command line arguments for QMD
## QMD parameters -- fundamentals such as number of particles etc
parser.add_argument(
  '-dir', '--results_directory', 
  help="Directory where results of multiple QMD are held.",
  type=str,
  default=os.getcwd()
)


arguments = parser.parse_args()
directory_to_analyse = arguments.results_directory
plot_file = directory_to_analyse+'/model_scores.png'
print("directory : ", directory_to_analyse)

model_scores = model_scores(directory_to_analyse)
plot_scores(model_scores, plot_file)





