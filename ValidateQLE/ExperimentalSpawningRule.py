from __future__ import print_function # so print doesn't show brackets
import os as os

#import argparse
#parser = argparse.ArgumentParser(description='Pass variables for (I)QLE.')

import warnings
warnings.filterwarnings("ignore")
## Parse input variables to use in QMD 

import numpy as np
import itertools as itr

import sys as sys 
import pandas as pd
import warnings
import time as time
import random
import pickle
pickle.HIGHEST_PROTOCOL = 2
sys.path.append(os.path.join("..", "Libraries","QML_lib"))

import GlobalVariables
global_variables = GlobalVariables.parse_cmd_line_args(sys.argv[1:])
# global_variables class now in scope


from RedisSettings import *
import Evo as evo
import DataBase 
from QMD import QMD #  class moved to QMD in Library
import QML
import ModelGeneration 
import BayesF
import matplotlib.pyplot as plt
#from pympler import asizeof
import matplotlib.pyplot as plt
paulis = ['x', 'y', 'z'] # will be chosen at random. or uncomment below and comment within loop to hard-set

import time as time 

###  START QMD ###

print("num times to use:", global_variables.num_times_bayes)
qle=global_variables.do_qle # True for QLE, False for IQLE
pickle_result_db = True

import time
start = time.time()

initial_op_list = ['xTi', 'yTi', 'zTi']
#initial_op_list = ['x', 'y', 'z']

num_ops = len(initial_op_list)
for i in range(global_variables.num_runs):
    print("\ni=",i)
    print(global_variables.num_particles, "Paricles for ", global_variables.num_experiments, "Experiments:")
    true_op = 'xTiPPyTiPPzTiPPxTxPPyTyPPzTz'
#    true_params = [np.random.rand()]
    #true_params = [0.19, 0.21, 0.8, 0.22, 0.20, 0.27]
    true_params = [0.25, 0.21, 0.28, 0.22, 0.23, 0.27]
    qmd = QMD(
        initial_op_list=initial_op_list, 
        true_operator=true_op, 
        true_param_list=true_params, 
        num_particles=global_variables.num_particles,
        num_experiments = global_variables.num_experiments, 
        num_times_for_bayes_updates = global_variables.num_times_bayes,
        qle=qle,
        num_probes=5,
        gaussian=True, 
        max_num_branches = 0,
        max_num_qubits = 10, 
        parallel = True,
        use_rq = global_variables.use_rq,
        use_exp_custom=False, 
        compare_linalg_exp_tol=None,
        #growth_generator='ising_non_transverse'
        growth_generator='hyperfine_like'
    )
   # qmd.learnModelNameList(model_name_list=['z'], blocking=True, use_rq=False)
    qmd.runRemoteQMD(num_spawns=3)
    
    if pickle_result_db:
        print("QMD complete. Pickling result.")
        pickle.dump(qmd, open("qmd_class.p", "wb"), protocol=2)
    
    qmd.plotVolumes(save_to_file='volumes_all_models.png')
    qmd.plotVolumes(branch_champions=True, save_to_file='volumes_branch_champs.png')
    
    
end = time.time()
print("\n\nTime taken:", end-start)

