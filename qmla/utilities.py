import numpy as np
import scipy as sp
import os
import time
import copy
import qinfer as qi
import random 

import redis
import pickle
import matplotlib.colors



def resource_allocation(
    base_qubits,
    base_terms,
    max_num_params,
    this_model_qubits,
    this_model_terms,
    num_experiments,
    num_particles,
    given_resource_as_cap=True
):
    new_resources = {}
    if given_resource_as_cap == True:
        # i.e. reduce number particles for models with fewer params
        proportion_of_particles_to_receive = (
            this_model_terms / max_num_params
        )
        print(
            "Model gets proportion of particles:",
            proportion_of_particles_to_receive
        )

        if proportion_of_particles_to_receive < 1:
            new_resources['num_experiments'] = num_experiments
            new_resources['num_particles'] = max(
                int(
                    proportion_of_particles_to_receive
                    * num_particles
                ),
                10
            )
        else:
            new_resources['num_experiments'] = num_experiments
            new_resources['num_particles'] = num_particles

    else:
        # increase proportional to number params/qubits
        qubit_factor = float(this_model_qubits / base_qubits)
        terms_factor = float(this_model_terms / base_terms)

        overall_factor = int(qubit_factor * terms_factor)

        if overall_factor > 1:
            new_resources['num_experiments'] = overall_factor * num_experiments
            new_resources['num_particles'] = overall_factor * num_particles
        else:
            new_resources['num_experiments'] = num_experiments
            new_resources['num_particles'] = num_particles

    print("New resources:", new_resources)
    return new_resources



def round_nearest(x,a):
    return round(round(x/a)*a ,2)



def format_experiment(
    qinfer_model, 
    qhl_final_param_estimates, 
    time,
    final_learned_params=None, 
):
    exp = np.empty(
        len(time),
        dtype=qinfer_model.expparams_dtype
    )
    exp['t'] = time
    try:
        for dtype in qinfer_model.expparams_dtype:
            term = dtype[0]
            if term in qhl_final_param_estimates:
                exp[term] = qhl_final_param_estimates[term]
    except BaseException:
        print("failed to set exp from param estimates.\nReturning:", exp)
    return exp

def flatten(l): return [item for sublist in l for item in sublist]


class StorageUnit():
    r""" 
    Generic object to which results can be pickled for later use/analysis. 
    """
    def __init__(self, data_to_store=None):
        if data_to_store is not None:
            for k in data_to_store:
                self.__setattr__(
                    k, data_to_store[k]
                )


def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100):
    new_cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
        'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=minval, b=maxval),
        cmap(np.linspace(minval, maxval, n)))
    return new_cmap
