"""
Functions for generation of new models.
"""

from __future__ import print_function # so print doesn't show brackets

import numpy as np
import itertools as itr

import os as os
import sys as sys 
import pandas as pd
import warnings
import copy
import time as time
#import Evo as evo
import DataBase 
import warnings
import ModelNames

# global paulis_list
# paulis_list = {'i' : np.eye(2), 'x' : evo.sigmax(), 'y' : evo.sigmay(), 'z' : evo.sigmaz()}

# Dict of max spawn depths, corresponding to different generation functions. 

##################################################################################
##################################################################################
"""
Essential functions. Functions below are specific, for generating terms according to given rules. new_model_list is the wrapper function which calls the selected generator rule.
"""
##################################################################################
##################################################################################

def time_seconds():
    import datetime
    now =  datetime.date.today()
    hour = datetime.datetime.now().hour
    minute = datetime.datetime.now().minute
    second = datetime.datetime.now().second
    time = str(str(hour)+':'+str(minute)+':'+str(second))
    return time

def log_print(to_print_list, log_file):
    identifier = str(str(time_seconds()) +" [MOD_GEN]")
    if type(to_print_list)!=list:
        to_print_list = list(to_print_list)

    print_strings = [str(s) for s in to_print_list]
    to_print = " ".join(print_strings)
    with open(log_file, 'a') as write_log_file:
        print(identifier, str(to_print), file=write_log_file, flush=True)


##################################################################################
##################### Model Generation Functions ############################################
##################################################################################



"""
Functions for generation of random model names for testing/debugging.
Functions for NV centre spin. 
"""

def process_transverse_term(term):
    # terms of form transverse_x_d3
    # transverse matrix is a single matrix of form,.e.g
    # XII + IXI + IIX
    # where num qubits=3, transverse axis=X
    
    components = term.split('_')
    components.remove('transverse')
    core_operators = list(sorted(DataBase.core_operator_dict.keys()))

    for l in components:
        if l[0] == 'd':
            dim = int(l.replace('d', ''))
        elif l in core_operators:
            transverse_axis = l
    mtx = transverse_axis_matrix(
        num_qubits = dim, 
        transverse_axis = transverse_axis
    )
    return mtx

def process_multipauli_term(term):
    # term of form pauliSet_aJb_iJk_dN
    # where a is operator on site i
    # b is operator on site k
    # N is total number of sites
    # e.g. pauliSet_xJy_1J3_d4
    
    components = term.split('_')
    components.remove('pauliSet')
    core_operators = list(sorted(DataBase.core_operator_dict.keys()))
    for l in components:
        if l[0] == 'd':
            dim = int(l.replace('d', ''))
        elif l[0] in core_operators:
            operators = l.split('J')
        else:
            sites = l.split('J')
    sites = [int(s) for s in sites] # get strings when splitting the list elements
    all_terms = list(zip(sites, operators)) # want tuples of (site, operator) for dict logic

    term_dict = {
        'dim' : dim,
        'terms' : [all_terms]
    }

    full_mod_str = ModelNames.full_model_string(term_dict)
    # print("Getting full matrix corresponding to:", full_mod_str)
    return DataBase.compute(full_mod_str)

def process_n_qubit_NV_centre_spin(term): 
    components = term.split('_')
    for l in components:
        if l[0] == 'd':
            dim = int(l.replace('d', ''))
        elif l == 'spin':
            term_type = 'spin'
        elif l == 'interaction' : 
            term_type = 'interaction'
        elif l in ['x', 'y', 'z']:
            pauli = l
    
    if term_type == 'spin':
        t_str = 'T'
        op_name = str(pauli)
        
        for d in range(dim - 1):
            op_name += str( t_str + 'i')
            t_str += 'T'
    elif term_type == 'interaction':
        p_str = 'P'*dim
        op_name = ''
        for d in range(dim - 1):
            t_str = 'T'
            single_term_name = str(pauli)
            for j in range(dim - 1):
                single_term_name += str(t_str)
                if d == j:
                    single_term_name += pauli
                else:
                    single_term_name += 'i'
                t_str += 'T'
            op_name += single_term_name
            if d < (dim-2):
                op_name += p_str
                    
    # print("Type {} ; name {}".format(term_type, op_name))
    return DataBase.compute(op_name)


"""
Functions for generation of random model names for testing/debugging.
Ising type models
"""

def process_1d_ising(term):
    components = term.split('_')
    components.remove('1Dising')
    include_transverse_component = include_chain_component = False
    
    for l in components:
        if l[0] == 'd':
            dim = int(l.replace('d', ''))
        elif l[0] == 'i':
            chain_axis = str(l.replace('i', ''))
            include_chain_component = True
        elif l[0] == 't' : 
            include_transverse_component = True
            transverse_axis = str(l.replace('t', ''))


    if include_chain_component == True:
        return ising_interaction_component(
            num_qubits = dim, 
            interaction_axis = chain_axis
        )

    elif include_transverse_component == True:
        return ising_transverse_component(
            num_qubits = dim, 
            transverse_axis = transverse_axis
        )

def transverse_axis_matrix(
    num_qubits, 
    transverse_axis
):
    individual_transverse_terms = []
    for i in range(1, 1+num_qubits):
        single_term = ''
        t_str = 'T'
        for q in range(1, 1+num_qubits):
            if i == q : 
                single_term += transverse_axis
            else:
                single_term += 'i'
            
            if q != num_qubits:
                single_term += t_str
                t_str += 'T'
                
        individual_transverse_terms.append(single_term)
    running_mtx = DataBase.compute(individual_transverse_terms[0])    
    for term in individual_transverse_terms[1:]:
        running_mtx += DataBase.compute(term)
    return running_mtx


def ising_transverse_component(
    num_qubits, 
    transverse_axis
):
    return transverse_axis_matrix(num_qubits, transverse_axis)

            
def ising_interaction_component(num_qubits, interaction_axis):
    
    individual_interaction_terms = []

    for i in range(1, num_qubits):
        single_term = ''
        t_str = 'T'
        for q in range(1, num_qubits+1):
            if i == q or i+1 == q :
                
                single_term += interaction_axis
            else:
                single_term += 'i'
            
            if q != num_qubits:
                single_term += t_str
                t_str += 'T'
                
        individual_interaction_terms.append(single_term)
        
    running_mtx = DataBase.compute(individual_interaction_terms[0])
    
    for term in individual_interaction_terms[1:]:
        running_mtx += DataBase.compute(term)
        
    return running_mtx


def ising_1d_chain_name(
    num_qubits, 
    interaction_axis, 
    include_transverse=False, 
    transverse_axis=None,
    ring=False
):
    model_identifier = '1Dising_'
    model_name = ''
    dimension_term = str( '_d' + str(num_qubits))

    interaction_term = str(model_identifier + 'i' + interaction_axis + dimension_term )
    p_str = 'P'*num_qubits
    
    
    full_model = interaction_term
    if include_transverse == True:
        transverse_term = str(model_identifier +  't' + transverse_axis + dimension_term)
        full_model += str( p_str + transverse_term)
    return full_model
    
    
def generate_models_ising_1d_chain(
    **kwargs
):
    from UserFunctions import initial_models, max_num_qubits_info, fixed_axes_by_generator, transverse_axis_by_generator
    growth_generator = kwargs['generator']
    model_list = kwargs['model_list']
    spawn_stage = kwargs['spawn_stage']
    max_num_qubits = max_num_qubits_info[growth_generator]
    interaction_axis = fixed_axes_by_generator[growth_generator]
    transverse_axis = transverse_axis_by_generator[growth_generator]
    
    largest_mod_num_qubits = max( [  
            DataBase.get_num_qubits(mod) for mod in model_list
        ] 
    )
    
    new_models = []

    if spawn_stage[-1] == None:
        for q in range(2, max_num_qubits+1): 
            # include qubit number = 1 so compared against all others fairly 
            new_models.append(
                ising_1d_chain_name(
                    num_qubits = q, 
                    interaction_axis = interaction_axis, 
                    include_transverse = False
                )
            )
        spawn_stage.append('non-transverse complete')
    elif spawn_stage[-1] == 'non-transverse complete':
        for q in range(2, max_num_qubits+1): 
            new_models.append(
                ising_1d_chain_name(
                    num_qubits = q, 
                    interaction_axis = interaction_axis, 
                    include_transverse = True, 
                    transverse_axis = transverse_axis
                )
            )
        spawn_stage.append('Complete')
    return new_models
        

        
def random_model_name(num_dimensions=1, num_terms=1):
    """
    Return a valid (simple) model name of given number of dimensions and terms. 
    """
    import random
    paulis = DataBase.pauli_cores_with_identity
    p_str = ''
    t_str = ''
    
    for i in range(num_dimensions):
        p_str += 'P'
    for j in range(num_dimensions -1):
        t_str += 'T'
    
    
    summed_term = ''
    for j in range(1, num_terms+1):
        this_term = generate_term(num_dimensions)
        summed_term += this_term
        if(j!=num_terms):
            summed_term += p_str
    
    
    # Don't allow returning just identity in any dimension #TODO?
    while summed_term == (
        'i' or 'iTi' or 'iTiTTi' or 'iTiTTiTTTi' or
        'iTiTTiTTTiTTTTi' or 'iTiTTiTTTiTTTTiTTTTTi' or 
        'iTiTTiTTTiTTTTiTTTTTiTTTTTTi' or 
        'iTiTTiTTTiTTTTiTTTTTiTTTTTTiTTTTTTTi'
    ):
        summed_term = random_model_name(num_dimensions, num_terms) 
    
    return summed_term


def random_ising_chain(
    num_dimensions=1, 
    include_identity = True, 
    num_directions = 1
):
    """
    Return a valid (simple) model name of given number of dimensions and terms. 
    """
    import random
    paulis_full  = DataBase.pauli_cores_no_identity
    if include_identity: paulis_full.append('i')

    if num_directions > len(paulis_full):
        paulis = paulis_full
        warnings.warn("Number of dimensions exceeded the Pauli ops space")
    else:      
        paulis = random.sample(paulis_full, num_directions)    

    if num_dimensions == 1:
        return random.choice(paulis)

    num_terms = num_dimensions-1    
    
    p_str = ''
    t_str = ''
    
    for i in range(num_dimensions):
        p_str += 'P'
    for j in range(num_dimensions -1):
        t_str += 'T'
    
    
    summed_term = ''
    for j in range(1, num_terms+1):
        this_term = generate_term(num_dimensions, paulis)
        summed_term += this_term
        if(j!=num_terms):
            summed_term += p_str
            
    return summed_term



def generate_term(
    num_dimensions, 
):
    """
    For use only in random_model_name() function. 
    """
    paulis = DataBase.pauli_cores_with_identity
    import random
    t_str = ''
    running_str =''
    
    if num_dimensions == 1:
        return random.choice(paulis)
    else:
        for j in range(num_dimensions):
            t_str += 'T'
            running_str += random.choice(paulis)
            
            if j != num_dimensions -1:
                running_str += t_str

        return running_str
            
def single_pauli_multiple_dim(
    num_dimensions, 
    pauli=None
):
    """
    For use only in random_model_name() function. 
    """
    import random
    paulis = DataBase.pauli_cores_with_identity
    t_str = ''
    running_str =''
    
    if pauli is None: pauli=random.choice(paulis)

    if num_dimensions == 1:
        return random.choice(paulis)
    else:
        for j in range(num_dimensions):
            t_str += 'T'
            running_str += pauli
            
            if j != num_dimensions -1:
                running_str += t_str

        return running_str



"""
Specific Hamiltonian generators. 
Return strings corresponding to model names following naming convention.
Use these strings with DataBase.operator class.
"""

def interaction_ham(qubit_list, operator_list, num_qubits):
    
    t_str = ''
    running_str = ''
    for i in range(num_qubits):
        t_str += 'T'
        
        if i in qubit_list:
            running_str += operator_list[qubit_list.index(i)]
            
        else: 
            running_str += 'i'
        if len(t_str)!=num_qubits:
            running_str += t_str
    return running_str

def ising_fully_interacting(num_qubits):
    # fully interacting Ising Hamiltonian name
    this_idx = 0
    max_idx = 0
    for i in range(num_qubits):
        max_idx += i ## Triangle number of 
    p_str = ''
    for a in range(num_qubits):
        p_str += 'P'
    
    running_str=''
    for i in range(num_qubits):
        for j in range(i, num_qubits):
            if i!=j:
                this_idx+=1
                op_list = ['z', 'z']
                qub_list = [i,j]
                new_term = interaction_ham(qubit_list=qub_list,
                    operator_list=op_list, num_qubits=num_qubits
                )
                running_str += new_term
                if(this_idx < max_idx):
                    running_str += p_str
    return running_str


## Manipulate input model names 

def identity_interact(subsystem, num_qubits, return_operator=False):
    new_string = ''
    sub_dim = DataBase.get_num_qubits(subsystem)
    if sub_dim >= num_qubits:
        if return_operator: 
            return op
        else: 
            return op.name
    
    for i in range(sub_dim, num_qubits):
        t_str = 'T'
        for j in range(i-1):
            t_str += 'T'
        new_string += t_str+'i'
    output_string = subsystem + new_string
    if return_operator: 
        return DataBase.operator(output_string)
    else:
        return output_string
        

def dimensionalise_name_by_name(name, true_dim, return_operator=False):
    op = DataBase.operator(name)
    constituents = op.constituents_names
    new_list=[]

    for term in constituents: 
        new_list.append(identity_interact(subsystem=term, num_qubits=true_dim))

    p_str = ''
    for i in range(true_dim):
        p_str+='P'    

    new_name = p_str.join(new_list)
    
    if return_operator: 
        return DataBase.operator(new_name)
    else: 
        return new_name

        
        
def dimensionalise_name_by_operator(op, true_dim, return_operator=False):
    constituents = op.constituents_names
    new_list=[]

    for term in constituents: 
        new_list.append(identity_interact(subsystem=term, num_qubits=true_dim))

    p_str = ''
    for i in range(true_dim):
        p_str+='P'    

    new_name = p_str.join(new_list)
    
    if return_operator: 
        return DataBase.operator(new_name)
    else: 
        return new_name


def dimensionalise_name_by_name_list(constituents, true_dim, return_operator=False):
    new_list=[]

    for term in constituents: 
        new_list.append(identity_interact(subsystem=term, num_qubits=true_dim))

    p_str = ''
    for i in range(true_dim):
        p_str+='P'    

    new_name = p_str.join(new_list)
    if return_operator: 
        return DataBase.operator(new_name)
    else: 
        return new_name
            
            
def simple_ising(
    generator_list, 
    **kwargs
):
    new_options = []
    options = DataBase.pauli_cores_no_identity,
    for gen in generator_list: 
        num_qubits = DataBase.get_num_qubits(gen)
        t_str = ''
        for a in range(num_qubits):
            t_str+='T'
        for opt in options:
            new_options.append(gen+t_str+opt)
    
    return new_options


### spawn function to match process followed during experimental QMD ###

def single_pauli_multiple_dim(
    num_qubits, 
    log_file, 
    pauli=None
):
    import random
    paulis = DataBase.pauli_cores_with_identity 
    t_str = ''
    running_str =''
    
    if pauli is None: pauli=random.choice(paulis)

    if num_qubits == 1:
        return random.choice(paulis)
    else:
        for j in range(num_qubits):
            t_str += 'T'
            running_str += pauli
            
            if j != num_qubits -1:
                running_str += t_str

        return running_str
        
def ising_non_transverse(
    model_list, 
    spawn_step, 
    log_file,
    **kwargs
):
    single_qubit_terms = ['xTi', 'yTi', 'zTi']
    nontransverse_terms = ['xTx', 'yTy', 'zTz']

    if len(model_list) > 1:
        log_print(["Only one model required for non-transverse Ising growth."],
            log_file
        )
        return False
    else:
        model = model_list[0]
    
    present_terms = model.split('PP')

    new_models = []
    if spawn_step in [1,2]:
        for term in single_qubit_terms:
            if term not in present_terms:
                new_model = model+'PP'+term
                new_models.append(new_model)

    elif spawn_step in [3,4,5]:
        for term in nontransverse_terms:
            if term not in present_terms:
                new_model = model+'PP'+term
                new_models.append(new_model)
                
    return new_models    


def ising_transverse(
    model_list, 
    spawn_step, 
    log_file,
    **kwargs
):
# TODO before using this function, need to add a max_spawn_depth to the dict above for ising_transverse. How many spawns can it support?
    single_qubit_terms = ['xTi', 'yTi', 'zTi']
    nontransverse_terms = ['xTx', 'yTy', 'zTz']
    all_transverse_terms = ['xTy', 'xTz', 'yTx', 'yTz', 'zTy', 'zTx']
    transverse_terms = ['xTy', 'xTz','yTz']
    all_two_qubit_terms = ( 
        single_qubit_terms
        + nontransverse_terms 
        + transverse_terms
    )
     
    if len(model_list) > 1:
        log_print(
            [
            "Only one model required for transverse Ising growth."
            ],
            log_file
        )
        return False
    else:
        model = model_list[0]

    present_terms = model.split('PP')

    new_models = []
    if spawn_step in [1,2]:
        for term in single_qubit_terms:
            if term not in present_terms:
                new_model = model+'PP'+term
                new_models.append(new_model)

    elif spawn_step in [3,4,5]:
        for term in nontransverse_terms:
            if term not in present_terms:
                new_model = model+'PP'+term
                new_models.append(new_model)

    else:
        for term in transverse_terms:
            if term not in present_terms:
                new_model = model+'PP'+term
                new_models.append(new_model)

    return new_models    

def hyperfine_like(
    model_list, 
    spawn_step, 
    model_dict, 
    log_file,
    **kwargs
):
# TODO before using this function, need to add a max_spawn_depth to the dict above for ising_transverse. How many spawns can it support?
    import random
    single_qubit_terms = ['xTi', 'yTi', 'zTi']
    nontransverse_terms = ['xTx', 'yTy', 'zTz']
    transverse_terms = ['xTy', 'xTz', 'yTz']
    all_two_qubit_terms = ( single_qubit_terms + nontransverse_terms
        + transverse_terms
    )
    if len(model_list) > 1:
        log_print(["Only one model required for transverse Ising growth."],
            log_file
        )
        return False
    else:
        model = model_list[0]

    present_terms = model.split('PP')

    new_models = []
    if spawn_step in [1,2]:
        for term in single_qubit_terms:
            if term not in present_terms:
                new_model = model+'PP'+term
                new_models.append(new_model)
    elif spawn_step in [3,4,5]:
        for term in nontransverse_terms:
            if term not in present_terms:
                new_model = model+'PP'+term
                new_models.append(new_model)

    elif spawn_step == 6: 
        i=0
        while i < 3:
            term = random.choice(transverse_terms)
            
            if term not in present_terms:
                new_model = model+'PP'+term
                if ( 
                    DataBase.check_model_in_dict(new_model, model_dict) == False
                    and new_model not in new_models
                ):
                    
                    new_models.append(new_model)
                    i+=1
    elif spawn_step == 7: 
        i=0
        while i < 2:
            term = random.choice(transverse_terms)
            
            if term not in present_terms:
                new_model = model+'PP'+term
                if (
                    DataBase.check_model_in_dict(new_model, model_dict) == False
                    and new_model not in new_models
                ):
                    
                    new_models.append(new_model)
                    i+=1

    elif spawn_step == 8: 
        i=0
        while i < 1:
            term = random.choice(transverse_terms)
            
            if term not in present_terms:
                new_model = model+'PP'+term
                if (
                    DataBase.check_model_in_dict(new_model, model_dict) == False
                    and new_model not in new_models
                ):
                    
                    new_models.append(new_model)
                    i+=1
    return new_models    
        

def NV_centre_experiment_debug(
    model_list, 
    **kwargs 
):
    spawn_stage = kwargs['spawn_stage']
    spawn_stage.append('Complete')
    return model_list

def reduced_nv_experimental_method(
    model_list, 
    spawn_step, 
    model_dict, 
    log_file,
    **kwargs
):
    """
    For use only during development to minimise time taken for testing.
    """
    if spawn_step == 1:
        return ['xTiPPxTxPPyTiPPyTyPPzTiPPzTz']
    elif spawn_step == 2:
        kwargs['spawn_stage'].append('Complete')
        return [
            'xTiPPxTxPPxTzPPyTiPPyTyPPzTiPPzTz',
            'xTiPPxTxPPyTiPPyTyPPyTzPPzTiPPzTz',
            'xTiPPxTxPPxTyPPyTiPPyTyPPzTiPPzTz'
        ]



def test_multidimensional(
    model_list, 
    spawn_step, 
    log_file,
    **kwargs
):
    
    # a test generation rule to check if QMD still works across dimensions. 

    new_models = []
    
    for m in model_list:
        dim = DataBase.get_num_qubits(m)
        num_terms = len(DataBase.get_constituent_names_from_name(m))
        for i in range(2):
            new_mod = random_model_name(dim, num_terms+1)
            new_models.append(new_mod)
    
    log_print(
        [
        'Input models:', 
        model_list,
        'New models:', 
        new_models
        ],
        log_file = log_file
    )

    if spawn_step==max_spawn_depth_info['test_multidimensional']:
        log_print(
            [
            'Multidensional test at spawn step=', 
            spawn_step
            ],
            log_file
        )

    return new_models


def p_t_actions(name):
    num_qubits = DataBase.get_num_qubits(name)

    p_str = 'P'
    t_str = ''

    for i in range(num_qubits-1):
        p_str+='P'
        t_str+='T'

    actions = {
        'p' : p_str,
        't' : t_str
    }

    return actions    



def existing_branch_champs_test(    
    model_list, 
    spawn_step, 
    model_dict, 
    log_file,
    current_champs
):
    new_models = []
    
    for name in model_list:
        actions = p_t_actions(model_list)
        p_str = actions['p']
        one_qubit_terms  = DataBase.pauli_cores_no_identity
        individual_terms = name.split(p_str)
        
        remaining_terms = list( set(one_qubit_terms) - set(individual_terms) )
        if spawn_step < 3 : 
            for term in remaining_terms:
                new_mod = str(name)
                new_mod += str(p_str + term)
                new_models.append(new_mod)
        else: 
            # current_champs.append('xPyPzPi')
            return current_champs
            
    return new_models


def non_interacting_ising(model_list, **kwargs):
    new_models = []
    paulis =  DataBase.pauli_cores_no_identity
    # paulis=['y']
    for mod in model_list:
        t_str = p_t_actions(mod)['t']
        new_t_str = str( t_str + 'T')
        for p in paulis:
            new_model = str(mod + new_t_str + p)        
            new_models.append(new_model)
    return new_models


def non_interacting_ising_single_axis(model_list, **kwargs):
    new_models = []
    paulis =  DataBase.pauli_cores_no_identity
    for mod in model_list:
        t_str = p_t_actions(mod)['t']
        new_t_str = str( t_str + 'T')
        for p in paulis:
            if p in mod:
                core_pauli = p
                new_model = str(mod + new_t_str + core_pauli)        
                new_models.append(new_model)
    return new_models

def deterministic_noninteracting_ising_single_axis(
    model_list,
    **kwargs
):
    from UserFunctions import max_num_qubits_info   
    new_models = []
    num_qubits = max_num_qubits_info[
        'deterministic_noninteracting_ising_single_axis'
    ]
    for mod in model_list:
        new = non_interacting_ising_single_axis([mod])
        new_models.extend(new)
        dimension = DataBase.get_num_qubits(new)
        while dimension < num_qubits:
            new = non_interacting_ising_single_axis(new)
            new_models.extend(new)
            dimension = DataBase.get_num_qubits(new[0])
    return list(set(new_models))
        


def interacting_nearest_neighbour_ising(
    model_list,
    **kwargs
):
    new_models = []
    paulis =  DataBase.pauli_cores_no_identity
    for mod in model_list:
        potential_core_paulis = []
        for p in paulis:
            if p in mod and p not in potential_core_paulis:
                potential_core_paulis.append(p)
        if len(potential_core_paulis)==1:
            core_pauli = potential_core_paulis[0]
        else:
            core_pauli = potential_core_paulis[0]
            print("clashing potential core paulis in interacting \
                nearest neighbour growth function from model", 
                mod, 
                ". Input model should only have one pauli type. \
                Proceeding with core", 
                core_pauli
            )
        operations_of_mod = ModelNames.operations_dict_from_name(mod)
        previous_dim = operations_of_mod['dim']
        new_dim = previous_dim + 1
        present_terms = operations_of_mod['terms']
        
        num_terms = len(present_terms)
        all_new_separate_terms = []

        for t in present_terms:
            new_terms = copy.copy(t)
            new_terms.append( (new_dim, 'i') )

            all_new_separate_terms.append(new_terms)

        new_nn_term = []
        for j in range(1, new_dim-1):
            new_nn_term.append( (j, 'i') )
        for j in range(new_dim-1, new_dim+1):
            new_nn_term.append( (j, core_pauli) )    

        all_new_separate_terms.append(new_nn_term)

        new_mod_dict = {
            'dim' : new_dim, 
            'terms': all_new_separate_terms
        }

        new_mod_string = ModelNames.full_model_string(new_mod_dict)

        new_models.append(new_mod_string)

    return new_models

def deterministic_interacting_nn_ising_single_axis(
    model_list,
    **kwargs
):
    from UserFunctions import max_num_qubits_info   
    new_models = []
    num_qubits = max_num_qubits_info['deterministic_interacting_nn_ising_single_axis']
    for mod in model_list:
        new = interacting_nearest_neighbour_ising([mod])
        new_models.extend(new)
        dimension = DataBase.get_num_qubits(new)
        while dimension < num_qubits:
            new = interacting_nearest_neighbour_ising(new)
            new_models.extend(new)
            dimension = DataBase.get_num_qubits(new[0])
    return list(set(new_models))



def tensor_all_with_identity_at_end(name):
    import copy
    op_dict = ModelNames.operations_dict_from_name(name)
    num_qubits = op_dict['dim']
    terms = op_dict['terms']
    new_terms = []
    new_dimension = num_qubits + 1

    for i in range(len(terms)):

        new_term = copy.copy(terms[i])

        new_term.append( (new_dimension, 'i'))
        new_terms.append(new_term)


    new_op_dict = {
        'dim' : new_dimension, 
        'terms' : new_terms
    }
    new_mod_name = ModelNames.full_model_string(new_op_dict)
    return new_mod_name

def tensor_all_with_identity_at_start(name):
    import copy
    op_dict = ModelNames.operations_dict_from_name(name)
    num_qubits = op_dict['dim']
    terms = op_dict['terms']
    new_terms = []
    new_dimension = num_qubits + 1

    new_terms = []
    for term in op_dict['terms']:
        new_term = [(1, 'i')]
        for a in term:
            new_tuple = (a[0]+1, a[1])
            new_term.append(new_tuple)
        new_terms.append(new_term)

    new_op_dict = {
        'dim' : new_dimension, 
        'terms' : new_terms
    }
    new_mod_name = ModelNames.full_model_string(new_op_dict)

    return new_mod_name

def add_fixed_axis_nn_interaction(name, fixed_axis):
    dimension = DataBase.get_num_qubits(name)
    op_dict = ModelNames.operations_dict_from_name(name)
    new_terms = []
    for i in range(1,dimension):
        term_one = (i, fixed_axis)
        term_two  = (i+1, fixed_axis)
        total_term = [term_one, term_two]
        new_terms.append(total_term)

    op_dict['terms'].extend(new_terms)
    new_name = ModelNames.full_model_string(op_dict)
    return new_name

def deterministic_transverse_ising_nn_fixed_axis(
    model_list, 
    **kwargs
):
    from UserFunctions import max_num_qubits_info
    from UserFunctions import fixed_axes_by_generator
    name = model_list[0] # for this growth rule, model_list should be of length 1, either x,y or z.
    models = []
    fixed_axis = fixed_axes_by_generator[
        'deterministic_transverse_ising_nn_fixed_axis'
    ]
    max_num_qubits = max_num_qubits_info[
        'deterministic_transverse_ising_nn_fixed_axis'
    ]
    one_qubit_larger_name = name
    starting_dimension = DataBase.get_num_qubits(name)
    for i in range(starting_dimension, max_num_qubits):
        name = DataBase.alph(one_qubit_larger_name)
        op_dict = ModelNames.operations_dict_from_name(name)
        terms = op_dict['terms']
        num_terms = len(terms)
        # full_model_string = ''
        all_term_strings= []

        for term in terms:
            this_term_string = '' 
            paulis = []

            for j in range(len(term)):
                action = term[j]
                if action[1] != 'i':
                    paulis.append(action[1])
            if len(paulis) == 1:
                core_pauli = paulis[0]
                break

        new_dimension = op_dict['dim'] + 1

        new_terms = []
        for i in range(1, new_dimension+1):
            this_term = []
            this_term.append((i, core_pauli))
            new_terms.append(this_term)

        new_op_dict = {
            'dim' : new_dimension,
            'terms' : new_terms
        }

        one_qubit_larger_name = ModelNames.full_model_string(
            new_op_dict
        )
        add_interaction = add_fixed_axis_nn_interaction(
            one_qubit_larger_name, 
            fixed_axis
        )

        models.extend(
            [one_qubit_larger_name, add_interaction]
        )
    return models
    
def test_changes_to_qmd(
    **kwargs
):
    from UserFunctions import initial_models
    growth_generator = kwargs['generator']
    model_list = kwargs['model_list']
    new_models = []


    base_terms = initial_models[growth_generator]
    this_dimension = DataBase.get_num_qubits(model_list[0])
    base_dimension = DataBase.get_num_qubits(base_terms[0])

    for mod in model_list:
        present_terms = DataBase.get_constituent_names_from_name(mod)
        base_models_this_dim = []
        if this_dimension == base_dimension:
            base_models_this_dim = base_terms
        else:
            for b in base_terms:
                new_mod = tensor_all_with_identity_at_start(b)
                for i in range(base_dimension+1, this_dimension):
                    new_mod = tensor_all_with_identity_at_start(new_mod)

                base_models_this_dim.append(new_mod)    

        base_terms_not_present = list(
            set(base_models_this_dim) - set(present_terms)
        ) 
        num_qubits = DataBase.get_num_qubits(mod)



        p_str = ''
        for i in range(num_qubits):
            p_str += 'P'

        for b in base_terms_not_present:
            new_mod = str(
                mod + p_str + b
            )
            new_models.append(new_mod)

        # new_models.append(tensor_all_with_identity_at_end(mod))


    return new_models

def NV_centre_spin_large_bath(
    **kwargs
):
    model_list = kwargs['model_list']
    spawn_step = kwargs['spawn_step']
    spawn_stage = kwargs['spawn_stage']    


    print(
        "[ModelGeneration.NV_centre_spin_large_bath]",
        "Spawn stage:", spawn_stage
    )


    max_num_qubits = max(
        [DataBase.get_num_qubits(mod) for mod in model_list]
    )
    new_gali_model = gali_model_nv_centre_spin(max_num_qubits + 1)
    return [new_gali_model]


def gali_model_nv_centre_spin(num_qubits):
    axes = ['x', 'y', 'z']
    p_str = 'P' * num_qubits
    model_terms = []
    for axis in axes:
        for contribution in ['interaction', 'spin']:
            model_terms.append(
                'nv_{}_{}_d{}'.format(contribution, axis, num_qubits)
            )
            
    model = p_str.join(model_terms)
    return model

def heisenberg_nontransverse(
    **kwargs
):
    from UserFunctions import initial_models
    # print("[ModGen] kwargs:", kwargs)
    growth_generator = kwargs['generator']
    # growth_generator = generator
    model_list = kwargs['model_list']
    spawn_step = kwargs['spawn_step']
    ghost_branches = kwargs['ghost_branches']
    branch_champs_by_qubit_num = kwargs['branch_champs_by_qubit_num']
    spawn_stage = kwargs['spawn_stage']
    # print("spawn stage", spawn_stage)
    # print("len:", len(spawn_stage))
    if len(spawn_stage) == 0:
        spawn_stage.append(0)
    else:
        spawn_stage.append(spawn_stage[-1]+1)

    new_models = []
    base_terms = initial_models[growth_generator]
    
    this_dimension = DataBase.get_num_qubits(model_list[0])
    base_dimension = DataBase.get_num_qubits(base_terms[0])

    base_models_this_dim = []
    if this_dimension == base_dimension:
        base_models_this_dim = base_terms
    else:
        for b in base_terms:
            new_mod = tensor_all_with_identity_at_start(b)
            for i in range(base_dimension+1, this_dimension):
                new_mod = tensor_all_with_identity_at_start(new_mod)

            base_models_this_dim.append(new_mod)    
    
    for mod in model_list:
        present_terms = DataBase.get_constituent_names_from_name(mod)
        base_terms_not_present = list(
            set(base_models_this_dim) - set(present_terms)
        ) 
        num_qubits = DataBase.get_num_qubits(mod)
        p_str = ''
        for i in range(num_qubits):
            p_str += 'P'
    

        if this_dimension in list(ghost_branches.keys()):
                new_mod = tensor_all_with_identity_at_end(mod)
                print("new mod:", new_mod)
                new_models.append(new_mod)
        elif len(base_terms_not_present) == 0:             
                new_models = branch_champs_by_qubit_num[
                    this_dimension
                ]
                ghost_branches[this_dimension] = True
        elif len(base_terms_not_present) > 0:
            for b in base_terms_not_present:
                new_mod = str(
                    mod + p_str + b
                )
                new_models.append(new_mod)

        else:
            print("[heisenberg_nontransverse] none of conditions met")

    return new_models


def heisenberg_transverse(
    **kwargs
):
    from UserFunctions import initial_models, max_num_qubits_info, fixed_axes_by_generator
    # print("[ModGen] kwargs:", kwargs)
    growth_generator = kwargs['generator']
    # growth_generator = generator
    model_list = kwargs['model_list']
    spawn_step = kwargs['spawn_step']
    ghost_branches = kwargs['ghost_branches']
    branch_champs_by_qubit_num = kwargs['branch_champs_by_qubit_num']
    spawn_stage = kwargs['spawn_stage']
    max_num_qubits = max_num_qubits_info[growth_generator]
    
    new_models = []
    base_terms = initial_models[growth_generator]
    
    this_dimension = DataBase.get_num_qubits(model_list[0])
    base_dimension = DataBase.get_num_qubits(base_terms[0])

    base_models_this_dim = []
    if this_dimension == base_dimension:
        base_models_this_dim = base_terms
    else:
        for b in base_terms:
            new_mod = tensor_all_with_identity_at_start(b)
            for i in range(base_dimension+1, this_dimension):
                new_mod = tensor_all_with_identity_at_start(new_mod)

            base_models_this_dim.append(new_mod)    
    
    for mod in model_list:
        present_terms = DataBase.get_constituent_names_from_name(mod)
        base_terms_not_present = list(
            set(base_models_this_dim) - set(present_terms)
        ) 
        num_qubits = DataBase.get_num_qubits(mod)
        p_str = ''
        for i in range(num_qubits):
            p_str += 'P'

    print("SPAWN STAGE:", spawn_stage)
    if spawn_stage[-1] == None:
        # ie grow the non transverse terms
        ghost_branch_dims = list(ghost_branches.keys())
        if this_dimension in ghost_branch_dims:
            new_mod = tensor_all_with_identity_at_end(mod)
            new_models.append(new_mod)
            print("Ghost branch for dimension:", this_dimension)
            if this_dimension == max_num_qubits:
                print("APPENDING SPAWN STAGE")
                spawn_stage.append('all_dimensions_learned')
            
        elif len(base_terms_not_present) == 0:             
            new_models = branch_champs_by_qubit_num[
                this_dimension
            ]
            ghost_branches[this_dimension] = True
        elif len(base_terms_not_present) > 0:
            for b in base_terms_not_present:
                new_mod = str(
                    mod + p_str + b
                )
                new_models.append(new_mod)
    elif spawn_stage[-1] == 'all_dimensions_learned':
        print("Final dimensional ghost branch being generated.")
        all_champs = []
        for v in list(branch_champs_by_qubit_num.values()):
            all_champs.extend(v)
        print("all champs:", all_champs)
        new_models = all_champs
        spawn_stage.append('nontransverse_ghost_branch_complete')
    elif spawn_stage[-1] == 'nontransverse_ghost_branch_complete':
        all_champs = []
        for v in list(branch_champs_by_qubit_num.values()):
            all_champs.extend(v)
        try:
            transverse_axis = fixed_axes_by_generator[
                growth_generator
            ]
        except:
            transverse_axis = fixed_axes_by_generator[
                None
            ]
        all_champs = list(set(all_champs))

        print(
            "Making transverse terms out of all champs so far:",
            all_champs
        )
        for champ in all_champs:
            new_models.append(
                ModelNames.make_term_transverse(
                    term = champ,
                    transverse_axis = transverse_axis
                )
            )
        print("Made new models:", new_models)
        spawn_stage.append('Complete')
    
    return new_models

def process_heisenberg_xyz(term):
    components = term.split('_')
    components.remove('Heis')
    include_transverse_component = include_chain_component = False
    
    for l in components:
        if l[0] == 'd':
            dim = int(l.replace('d', ''))
        elif l[0] == 'i':
            chain_axis = str(l.replace('i', ''))
            include_chain_component = True
        elif l[0] == 't' : 
            include_transverse_component = True
            transverse_axis = str(l.replace('t', ''))

    if include_chain_component == True:
        return single_axis_nearest_neighbour_interaction_chain(
            num_qubits = dim, 
            interaction_axis = chain_axis
        )

    elif include_transverse_component == True:
        return single_axis_transverse_component(
            num_qubits = dim, 
            transverse_axis = transverse_axis
        )

            
def single_axis_nearest_neighbour_interaction_chain(
    num_qubits, 
    interaction_axis='x'
):
    
    individual_interaction_terms = []

    for i in range(1, num_qubits):
        single_term = ''
        t_str = 'T'
        for q in range(1, num_qubits+1):
            if i == q or i+1 == q :
                
                single_term += interaction_axis
            else:
                single_term += 'i'
            
            if q != num_qubits:
                single_term += t_str
                t_str += 'T'
                
        individual_interaction_terms.append(single_term)
        
    running_mtx = DataBase.compute(individual_interaction_terms[0])
    
    for term in individual_interaction_terms[1:]:
        running_mtx += DataBase.compute(term)
        
    return running_mtx

def single_axis_transverse_component(
    num_qubits, 
    transverse_axis='z'
):
    
    individual_transverse_terms = []

    for i in range(1, 1+num_qubits):
        single_term = ''
        t_str = 'T'
        for q in range(1, 1+num_qubits):
            if i == q : 
                single_term += transverse_axis
            else:
                single_term += 'i'
            
            if q != num_qubits:
                single_term += t_str
                t_str += 'T'
                
        individual_transverse_terms.append(single_term)
        
        
    running_mtx = DataBase.compute(individual_transverse_terms[0])
    
    for term in individual_transverse_terms[1:]:
        running_mtx += DataBase.compute(term)
        
        
    return running_mtx

def get_heisenberg_xyz_name(
    num_qubits, 
    transverse_axis='z',
    include_transverse=False
):
    model_identifier = 'Heis_'
    model_name = ''
    dimension_term = str( '_d' + str(num_qubits))

    interaction_terms = []
    for axis in ['x', 'y', 'z']:
        axis_interaction_term = str(
            model_identifier +
            'i' +
            axis +
            dimension_term
        )
        interaction_terms.append(axis_interaction_term)
    p_str = 'P'*num_qubits
    print(interaction_terms)
    
    full_model = ''
    for term in interaction_terms:
        if interaction_terms.index(term)>0:
            full_model += str( p_str )
        full_model += str(   term )
    
    if include_transverse == True:
        transverse_term = str(model_identifier +  't' + transverse_axis + dimension_term)
        full_model += str( p_str + transverse_term)
    return full_model


def generate_models_heisenberg_xyz(
    **kwargs
):
    from UserFunctions import initial_models, max_num_qubits_info, fixed_axes_by_generator, transverse_axis_by_generator
    growth_generator = kwargs['generator']
    model_list = kwargs['model_list']
    spawn_stage = kwargs['spawn_stage']
    max_num_qubits = max_num_qubits_info[growth_generator]
#     interaction_axis = fixed_axes_by_generator[growth_generator]
    transverse_axis = transverse_axis_by_generator[growth_generator]

    new_models = []
    if spawn_stage[-1] == None:
        for q in range(2, max_num_qubits+1): 
            # include qubit number = 1 so compared against all others fairly 
            new_models.append(
                get_heisenberg_xyz_name(
                    num_qubits = q, 
#                     interaction_axis = interaction_axis, 
                    include_transverse = False
                )
            )
        spawn_stage.append('non-transverse complete')
    elif spawn_stage[-1] == 'non-transverse complete':
        for q in range(2, max_num_qubits+1): 
            new_models.append(
                get_heisenberg_xyz_name(
                    num_qubits = q, 
#                     interaction_axis = interaction_axis, 
                    include_transverse = True, 
                    transverse_axis = transverse_axis
                )
            )
        spawn_stage.append('Complete')
    return new_models
    

##################### ##################### #####################
##################### Hubbard rules #####################
##################### ##################### #####################

### Fermi Hubbard 
import fermilib
from fermilib.transforms import get_sparse_operator
from fermilib.ops import FermionOperator
# Note to extend e.g. to bosonic:
# https://github.com/quantumlib/OpenFermion/blob/master/src/openfermion/hamiltonians/_hubbard.py

def process_fermi_hubbard_term(term):
#     term ~ FHhop_ihj_s_dN, FHonsite_i_dN, FHchemical_i_dN: 
#     (i,j) sites to hop between; s spin type to hop ('up' or 'down')
#     i site to count; N number sites total
    
    constituents = term.split('_')
    for c in constituents:
        if c == 'FHhop':
            constituents.remove(c)
            mtx = process_fermi_hubbard_hopping(constituents) 
        elif c == 'FHonsite':
            constituents.remove(c)
            mtx = process_fermi_hubbard_onsite(constituents) 
        elif c == 'FHchemical':
            constituents.remove(c)
            mtx = process_fermi_hubbard_chemical(constituents)
    return mtx


def jordan_wigner_mtx(fermion_operator):
    """
    Calls fermilib functinoality to compute complete matrix given a 
    FermionOperator class fermion. 
    """
    return fermilib.transforms.get_sparse_operator(fermion_operator).todense()

def fermionic_hopping_term(i, j, num_sites):
    dimensional_description = "{}".format(2*num_sites-1)
    dimensional_fermion_op = FermionOperator(dimensional_description)

    hopping_term = FermionOperator(((i, 1), (j, 0)))
    hopping_term += FermionOperator(((j, 1), (i, 0)))
    hopping_term += dimensional_fermion_op

    mtx = jordan_wigner_mtx(hopping_term) - jordan_wigner_mtx(dimensional_fermion_op)
    return np.array(mtx)

def process_fermi_hubbard_chemical(constituents):
#     constituents ~ ['dN', 'i'], N = num sites, i = site index for onsite term
    for c in constituents:
        if c[0] == 'd':
            num_sites = int(c[1:])
        else:
            site_number = int(c)
    
    
    dimensional_description = "{}".format(2*num_sites-1)
    dimensional_fermion_op = FermionOperator(dimensional_description)
    
    i = 2*site_number - 2 # index with respect to basis (site_number, spin_type)
    down_term = FermionOperator( ( (i,0), ) )
    up_term = FermionOperator( ( (i,1), ) )
    down_term += dimensional_fermion_op
    up_term += dimensional_fermion_op
    
    mtx = jordan_wigner_mtx(up_term) + jordan_wigner_mtx(down_term) - 2*jordan_wigner_mtx(dimensional_fermion_op)
    return np.array(mtx)
    


def process_fermi_hubbard_onsite(constituents):
#     constituents ~ ['dN', 'i'], N = num sites, i = site index for onsite term
    for c in constituents:
        if c[0] == 'd':
            num_sites = int(c[1:])
        else:
            site_number = int(c)
    dimensional_description = "{}".format(2*num_sites-1)
    dimensional_fermion_op = FermionOperator(dimensional_description)
    
    i = 2*site_number - 2 # index with respect to basis (site_number, spin_type)
    num_term = FermionOperator( ( (i,1), (i,0), (i+1, 1), (i+1, 0)) )
    # operator of form {c^{\dagger}_i c_i c^{\dagger}_{i+1} c_{i+1}}
    num_term += dimensional_fermion_op
    
    mtx = jordan_wigner_mtx(num_term) - jordan_wigner_mtx(dimensional_fermion_op)
    return np.array(mtx)

def process_fermi_hubbard_hopping(constituents):
    for c in constituents:
        if c in ['down', 'up']:
            spin_type = c
        elif c[0] == 'd':
            num_sites = int(c[1:])
        else:
            sites = [int(s) for s in c.split('h')]        

    i_idx = 2*(sites[0]-1) - 2 # 2i -2
    j_idx = 2*(sites[1]-1) - 2 # 2j -2   
    if spin_type == 'down':
        i_idx = 2*(sites[0] - 1)
        j_idx = 2*(sites[1] - 1)
    elif spin_type == 'up':
        i_idx = 2*(sites[0]) - 1
        j_idx = 2*(sites[1]) - 1
    

    dimensional_description = "{}".format(2*num_sites-1)
    dimensional_fermion_op = FermionOperator(dimensional_description)

    hopping_term = FermionOperator(((i_idx, 1), (j_idx, 0)))
    hopping_term += FermionOperator(((j_idx, 1), (i_idx, 0)))
    hopping_term += dimensional_fermion_op

    mtx = jordan_wigner_mtx(hopping_term) - jordan_wigner_mtx(dimensional_fermion_op)
    return np.array(mtx)



### Old "Hubbard" rules (not physically correct; just hopping in most cases)
def hubbard_square_lattice_generalised(**kwargs):
    from UserFunctions import initial_models, max_num_qubits_info, fixed_axes_by_generator
    growth_generator = kwargs['generator']
    model_list = kwargs['model_list']
    spawn_stage = kwargs['spawn_stage']
    max_num_qubits = max_num_qubits_info[growth_generator]
    
    new_models = []
    misc = kwargs['miscellaneous']
    if spawn_stage[-1] == None:
        topology = initialise_topology_2x2_square_lattice()
        misc['topology'] = topology
        
        # now get new model name and update topology in same step
        new_mod = new_hubbard_model_from_square_lattice(misc['topology'])
        new_models.append(new_mod)
        spawn_stage.append('topology_generated')
    elif spawn_stage[-1] == 'topology_generated':
        print("generating new topology. Starting from:\n", misc['topology'])
        new_mod = new_hubbard_model_from_square_lattice(misc['topology'])
        new_models.append(new_mod)
    
    if np.any(
        np.array([DataBase.get_num_qubits(mod) for mod in new_models]) >= 
        max_num_qubits
    ):
        print("Max num qubits {} reached".format(max_num_qubits))
        spawn_stage.append('Complete')

    return new_models

# def process_hubbard_operator(
#     term
# ):
#     # for use in computing base level terms in a model, used in DataBase.
#     return hopping_matrix(term)

def compute_hubbard_basis_vector(
    spin_type, 
    site, 
    num_sites,
    basis_vectors
):
    basis_vec = 1
    spin_vec = basis_vectors[spin_type] 
    vac = basis_vectors['vac']
    
    for i in range(1, num_sites+1):
        if i == site:
            basis_vec = np.kron(basis_vec, spin_vec)
        else:
            basis_vec = np.kron(basis_vec, vac)
    return basis_vec

def process_hopping_term(term):
    basis_vectors = {
        'vac' : np.array([1,0,0,0]),
        'down' : np.array([0,1,0,0]),
        'up' : np.array([0,0,1,0]),
        'double' : np.array([0,0,0,1])
    }
    constituents = term.split('_')

    for c in constituents:
        if c == 'hop':
            continue # do nothing - just registers what type of matrix to construct
        elif c in list(basis_vectors.keys()):
            spin_type = c
        elif c[0] == 'd':
            num_sites = int(c[1:])
        else:
            sites = [int(s) for s in c.split('h')]        
    
    ## size of Hamiltonian # 2^2n for n sites (2n for v,up,down,double at each site)
    dim = 2**(2*num_sites) 
    vectors = [
        compute_hubbard_basis_vector(
            spin_type = spin_type, 
            site = s,
            num_sites = num_sites,
            basis_vectors = basis_vectors
        ) 
        for s in sites
    ]

    if len(vectors) == 1:
        hopping_mtx = np.outer(vectors[0], vectors[0])
    else:
        hopping_mtx = np.outer(vectors[0], vectors[1]) + np.outer(vectors[1], vectors[0])

    return hopping_mtx


def hopping_matrix(term):
    # to get a matrix given a term consisting of Hopping type terms
    # e.g. h_1_2_d3PPPh_1_3_d3
    from ModelNames import full_model_string
    print("hopping_matrix func. term:", term)
    split_term = term.split('_')
    sites = []
    for i in split_term:
        print("ind term:", i)
        if i[0] == 'd':
            # dim = int(i[1])
            dim = int(i.replace('d', ''))
        elif i[0] == 'e':
            energy_term = True
            hopping_term = False
        elif i != 'h': 
            hopping_term = True
            energy_term = False
            sites.append(int(i))
    
    if (len(sites) > 0 and max(sites) > dim):
        raise ValueError(
            "Hopping term", 
            term, 
            "has site index", 
            max(sites), 
            "higher than the dimension", 
            dim
        )
    print(
        "Hopping matrix. term:", term, 
        "\nenergy term:", energy_term, 
        "\n hopping_term:", hopping_term,
        "dimension:", dim
    )

    if energy_term is True:
        full_name = interaction_energy_pauli_term(dim)

    elif hopping_term is True:
        term_1 = []
        term_2  = []
        
        term_1.append((sites[0], 'a'))
        term_1.append((sites[1], 's'))
        term_2.append((sites[1], 'a'))
        term_2.append((sites[0], 's'))

        terms = [term_1, term_2]
        op_dict = {
            'dim' : dim, 
            'terms' : terms
        }
        full_name = full_model_string(op_dict)
    # mtx = DataBase.operator(full_name).matrix

    mtx = DataBase.compute(full_name)

    return mtx



def hubbard_chain_increase_dimension_full_chain(mod):
    # if going up a dimension and want to consider all newly available hopping terms one by one
    import copy
    orig_mod = deconstruct_hopping_term(mod)
    orig_sites = orig_mod['sites']
    this_num_qubits = orig_mod['dim']

    individual_terms = DataBase.get_constituent_names_from_name(mod)
    new_num_qubits = this_num_qubits + 1

    new_site_list = []
    for i in range(1, new_num_qubits):
        new_site = [i, new_num_qubits]
        new_site_list.append(new_site)

    new_models = [] 
    new_model_sites = copy.copy(orig_sites)
    for new_site in new_site_list:
        new_model_sites.append(new_site)
    new_model_string = generate_hopping_term(
        {
            'sites' : new_model_sites, 
            'dim' : new_num_qubits
        }
    )
    new_models.append(new_model_string)
    return new_models

def hubbard_chain_just_hopping(**kwargs):
    model_list = kwargs['model_list']

    new_models = []
    for mod in model_list:
        new_mods = hubbard_chain_increase_dimension_full_chain(mod)
        new_models.extend(new_mods)
    return new_models

# def generate_hopping_term(
#     deconstructed, 
#     include_interaction_energy=False
# ):
#     sites_list = deconstructed['sites']
#     dim = deconstructed['dim']
    
#     if type(sites_list[0]) != list:
#         sites_list = [sites_list]
#     p_str = ''
#     for i in range(dim):
#         p_str += 'P'
        
#     overall_term = ''
#     first_term = True

#     for sites in sites_list:
#         hopping_string = 'h'
#         for s in sites:
#             # hopping_string += '_'
#             hopping_string += 'h'
#             hopping_string += str(s)
#         hopping_string += str( '_d' + str(dim)) 
    
#         if first_term == False:
#             overall_term += p_str 
#         else:
#             first_term = False
#         overall_term += str(hopping_string)

#     if include_interaction_energy == True:
#         overall_term += str(
#             p_str 
#             + 
#             interaction_energy_pauli_term(dim)
#         )
#     return overall_term

def interaction_energy_pauli_term(dim):
    interaction_energy = ''
    p_str = ''
    for i in range(dim):
        p_str += 'P'

    first_term = True
    for i in range(1, dim+1):

        op_dict = {
            'terms' : [[(i, 'z')]],
            'dim' : dim
        }
        new_term = ModelNames.full_model_string(op_dict)

        if first_term == False:
            interaction_energy += p_str
        else:
            first_term = False
        interaction_energy += new_term
    return interaction_energy    


# def deconstruct_hopping_term(hopping_string):
    
#     dim = DataBase.get_num_qubits(hopping_string)
#     individual_terms = DataBase.get_constituent_names_from_name(hopping_string)
    
#     deconstructed = {
#         'sites' : [], 
#         'dim' : dim
#     }
    
#     for term in individual_terms:
#         split_term = term.split('_')
#         sites = []
#         for i in split_term:
#             if i[0] == 'd':
#                 dim = int(i[1])
#             elif i != 'h': 
#                 sites.append(int(i))
#         deconstructed['sites'].append(sites)

#     return deconstructed

# def deconstruct_hopping_term(hopping_string):
    
#     dim = DataBase.get_num_qubits(hopping_string)
#     individual_terms = DataBase.get_constituent_names_from_name(hopping_string)
    
#     deconstructed = {
#         'sites' : [], 
#         'dim' : dim
#     }
    
#     for term in individual_terms:
#         split_term = term.split('_')
#         sites = []
#         for i in split_term:
#             if i[0] == 'd':
#                 dim = int(i[1])
#             elif i != 'h':
#                 print("i=", i)
#                 sites = i.split('h')
#                 sites = [int(a) for a in sites]
# #                 sites.append(int(i))
#                 deconstructed['sites'].append(sites)

#     return deconstructed

def process_hubbard_operator(
    term
):
    # for use in computing base level terms in a model, used in DataBase.
    return base_hubbard_grouped_term(term)


def base_hubbard_grouped_term(term):
    # from ModelGeneration import interaction_energy_pauli_term
    from ModelNames import full_model_string

    split_term = term.split('_')
    sites = []
    all_sites = []
    for i in split_term:
        if i[0] == 'd':
            # dim = int(i[1])
            dim = int(i.replace('d', ''))
        elif i[0] == 'e':
            energy_term = True
            hopping_term = False
        elif i != 'h': 
            hopping_sites = i.split('h')
            hopping_sites = [int(s) for s in hopping_sites]
            all_sites.append(hopping_sites)
            hopping_term = True
            energy_term = False
    #             sites.append(int(i))

    if (len(sites) > 0 and max(sites) > dim):
        raise ValueError(
            "Hopping term", 
            term, 
            "has site index", 
            max(sites), 
            "higher than the dimension", 
            dim
        )
    if energy_term is True:
        # self energy
        full_name = interaction_energy_pauli_term(dim)
        mtx = DataBase.compute(full_name)


    elif hopping_term is True:
        matrices = []
        mtx = None
        for sites in all_sites:
            term_1 = []
            term_2  = []

            term_1.append((sites[0], 'a'))
            term_1.append((sites[1], 's'))
            term_2.append((sites[1], 'a'))
            term_2.append((sites[0], 's'))

            terms = [term_1, term_2]
            op_dict = {
                'dim' : dim, 
                'terms' : terms
            }
            full_name = full_model_string(op_dict)
            # print("[base hopping process] op dict:", op_dict)
            # this_mtx = DataBase.operator(full_name).matrix

            this_mtx = DataBase.compute(full_name)
            if mtx is None:
                mtx = this_mtx
            else:
                mtx += this_mtx

    return mtx

def generate_hopping_term(
    deconstructed, 
    include_interaction_energy=False
):
    sites_list = deconstructed['sites']
    dim = deconstructed['dim']
    try:
        interaction_energy = deconstructed['interaction_energy']
    except:
        interaction_energy = include_interaction_energy
    
    if type(sites_list[0]) != list:
        sites_list = [sites_list]
    p_str = ''
    for i in range(dim):
        p_str += 'P'
    overall_term = ''
    first_term = True
    
    hopping_string = 'h'

    for sites in sites_list:
        hopping_string += str(
            '_' + 
            str(sites[0]) + 
            'h' + 
            str(sites[1])
        )
    
    hopping_string += str( '_d' + str(dim)) 
    overall_term += hopping_string

    if interaction_energy == True:
        interaction_term = str(
            'h_e_d' + str(dim) 
        )
        overall_term += str(
            p_str +
            interaction_term
        )
#         overall_term += str(
#             p_str 
#             + 
#             interaction_energy_pauli_term(dim)
#         )
    return overall_term

def deconstruct_hopping_term(hopping_string):
    dim = DataBase.get_num_qubits(hopping_string)
    individual_terms = DataBase.get_constituent_names_from_name(hopping_string)
    deconstructed = {
        'sites' : [], 
        'dim' : dim,
        'interaction_energy' : False
    }
    
    for term in individual_terms:
        split_term = term.split('_')
        sites = []
        for i in split_term:
            if i[0] == 'd':
                # dim = int(i[1])
                dim = dim = int(i.replace('d', ''))
            elif 'e' in i:
                deconstructed['interaction_energy'] = True
            elif i != 'h':
                sites = i.split('h')
                sites = [int(a) for a in sites]
                deconstructed['sites'].append(sites)
    return deconstructed

def generate_hubbard_chain(
    num_qubits, 
    include_interaction_energy=False
):
    sites = []
    for i in range(1,num_qubits):
        new_site = [i,i+1]
        sites.append(new_site)
    chain_dict = {
        'dim' : num_qubits,
        'sites' : sites
    }
    model_string = generate_hopping_term(
        chain_dict, 
        include_interaction_energy = include_interaction_energy
    )
    return model_string

def hubbard_chain(**kwargs):
    model_list = kwargs['model_list']
    spawn_stage = kwargs['spawn_stage']
    growth_generator = kwargs['generator']
    from UserFunctions import max_num_qubits_info
    max_num_qubits = max_num_qubits_info[growth_generator]
    new_models = []
    for mod in model_list:
        if spawn_stage[-1] == None:
            for i in range(2, max_num_qubits+1):
                new_mod = generate_hubbard_chain(i)
                new_models.append(new_mod)
            spawn_stage.append('just_hopping_complete')
        elif spawn_stage[-1] == 'just_hopping_complete':
            for i in range(2, max_num_qubits+1):
                new_mod = generate_hubbard_chain(
                    i, 
                    include_interaction_energy=True
                )
                new_models.append(new_mod)
            spawn_stage.append('Complete')
    return new_models











### Below is probably no longer needed -- replaced by system topology class
# TODO check and remove 



def check_nearest_neighbour_sites(site_1, site_2):
    # simply checks whether sites are adjacent (or comptues distance)
    # assumes Cartesian coordinates
    if len(site_1) != len(site_2):
        print(
            "Site distance calculation: both sites must have same number of dimensions.",
            "Given:", site_1, site_2
        )
        raise NameError('Unequal site dimensions.')
    
    dim = len(site_1)
    dist = 0 
    for d in range(dim):
        dist += np.abs(site_1[d] - site_2[d])
        
    if dist == 1:
        return True
    else:
        return False
    
def get_nearest_neighbour_list(topology):
    coordinates = topology['coordinates']
    site_indices = list(coordinates.keys())
    nearest_neighbours = []
    
    for i in range(len(site_indices)):
        idx_1 = site_indices[i]
        for j in range(i, len(site_indices)):
            idx_2 = site_indices[j]
            nn = check_nearest_neighbour_sites(
                site_1 = coordinates[idx_1],
                site_2 = coordinates[idx_2],
            )
            if nn is True:
                nearest_neighbours.append( (idx_1, idx_2) )
                
    return nearest_neighbours


def add_new_coordinate_2d_lattice(topology):
    # grows in a manner which minimises area of the topology
    rows = topology['occupation']['rows']
    cols = topology['occupation']['cols']

    row_values = rows.keys()
    col_values = cols.keys() 
    min_span_row = None
    min_span_col = None        

    for row_idx in rows:
        span = max(rows[row_idx]) - min(rows[row_idx])
        if (
            min_span_row is None 
            or
            span < min_span_row
        ):
            min_span_row = span
            min_span_row_idx = row_idx

    for col_idx in cols:
        span = max(cols[col_idx]) - min(cols[col_idx])
        if (
            min_span_col is None 
            or
            span < min_span_col
        ):
            min_span_col = span
            min_span_col_idx = col_idx

    if min_span_col < min_span_row:
        # growing downward in y-axis
        new_row = max(cols[min_span_col_idx]) + 1
        new_col = min_span_col_idx
    else:
        # growing rightward in x-axis
        new_col = max(rows[min_span_row_idx]) + 1
        new_row = min_span_row_idx

    new_coordinate = [new_row, new_col]
    print("new coordinate:", new_coordinate)

    try:
        topology['occupation']['rows'][new_row].append(new_col)
    except:
        topology['occupation']['rows'][new_row] = [new_col]

    try:
        topology['occupation']['cols'][new_col].append(new_row)
    except:
        topology['occupation']['cols'][new_col] = [new_row]


    max_site_idx = max(list(topology['coordinates'].keys()))
    new_site_idx = max_site_idx + 1
    topology['coordinates'][new_site_idx] = new_coordinate
    return new_site_idx


def add_sites_to_topology(topology):
    all_sites_greater_than_2_nearest_neighbours = False
    while all_sites_greater_than_2_nearest_neighbours == False:
        new_site_idx = add_new_coordinate_2d_lattice(topology)
        site_indices = list(topology['coordinates'].keys())

        new_coords  = topology['coordinates'][new_site_idx] 
        topology['nearest_neighbours'][new_site_idx] = []

        for i in site_indices:
            other_coords = topology['coordinates'][i] 

            nearest_neighbour = check_nearest_neighbour_sites(
                site_1 = new_coords,
                site_2 = other_coords
            )

            if nearest_neighbour is True:
                if i not in topology['nearest_neighbours'][new_site_idx]:
                    topology['nearest_neighbours'][new_site_idx].append(i)
                if new_site_idx not in topology['nearest_neighbours'][i]:
                    topology['nearest_neighbours'][i].append(new_site_idx)

        nn_lists = list(topology['nearest_neighbours'].values())
        num_nearest_neighbours = np.array([len(a) for a in nn_lists])
        all_sites_greater_than_2_nearest_neighbours = np.all(
            num_nearest_neighbours >= 2
        )

def initialise_topology_2x2_square_lattice():
    # Initialises a 2x2 square lattice
    topology = {
        'lattice_dimension' : 2,
        'span' : [0,0],
        'occupation' : {
            'rows' : {
                1 : [1, 2],
                2 : [1, 2]
            },
            'cols' : {
                1 : [1, 2], 
                2 : [1, 2]
            }
        },
        'coordinates' : {
            1 : [1,1],
            2 : [1,2], 
            3 : [2,1],
            4 : [2,2]
        },
        'nearest_neighbours' : {
            1 : [2,3],
            2 : [1,4], 
            3 : [1,4], 
            4 : [2,3]
        }
    }
    
    return topology


def new_hubbard_model_from_square_lattice(topology):

    add_sites_to_topology(topology)
    nearest_neighbours_list = get_nearest_neighbour_list(topology)
    nearest_neighbours_list = [list(a) for a in nearest_neighbours_list]
    num_qubits = len(topology['coordinates'])

    hubbard_model_dict = {
        'sites' : nearest_neighbours_list, 
        'dim' : num_qubits
    }

    new_model = generate_hopping_term(
        hubbard_model_dict, 
        include_interaction_energy=True, 
    )
    return new_model

##################################################################################
##################### Nondeterministic growth rules ############################################
##################################################################################
def possible_hopping_terms_new_site(site_id):
    new_terms = []
    dim = site_id
    for i in range(1, site_id):
        new_term = str(
            'h_' + 
            str(i) + 'h' + str(site_id)
            + '_d'+str(dim)
        )
        new_terms.append(new_term)
        
    return new_terms

def append_model_with_new_terms(mod, new_terms):
    dimension = DataBase.get_num_qubits(mod)
    p_str = 'P'*dimension
    
    new_mods = []
    
    for term in new_terms:
        new = str(
            mod + p_str
            + term
        )
        new_mods.append(new)
    return new_mods

def increase_dimension_maintain_distinct_interactions(
    mod, 
    dim_inc=1
):
    # here distinct means EVERY pair of sites corresponds to a separate parameter.
    dec = deconstruct_hopping_term(mod)
    new_dim = dec['dim'] + dim_inc
    sites = dec['sites']
    p_str = 'P'*new_dim
    
    overall_model = ''
    for site in sites:
        new_model_dec = {
            'dim' : new_dim,
            'sites' : [site]
        }
        new_term = generate_hopping_term(new_model_dec)
        if sites.index(site) != 0:
            overall_model += p_str
        overall_model += str(new_term)
        
    return overall_model

def generate_models_hopping_topology(
    **kwargs
):
    from UserFunctions import \
        initial_models, max_num_qubits_info, \
        fixed_axes_by_generator, transverse_axis_by_generator
        
    growth_generator = kwargs['generator']
    model_list = kwargs['model_list']
    spawn_stage = kwargs['spawn_stage']
    max_dimension = max_num_qubits_info[growth_generator]
    branch_champs_by_qubit_num = kwargs['branch_champs_by_qubit_num']
#     interaction_axis = fixed_axes_by_generator[growth_generator]
#     transverse_axis = transverse_axis_by_generator[growth_generator]
    
    new_models = []
    mod = model_list[0]

    if spawn_stage[-1] == None:
        spawn_stage.append((2,'c'))
        # return [h_1h2_d3PPPh_1h3_d3, h_1h2_d3PPPh_2h3_d3]
        # spawn stage -> (3,1)
        # dim = DataBase.get_num_qubits(mod)
        # new_dim = dim + 1
        # increased_dim_model = increase_dimension_maintain_distinct_interactions(mod)
        # new_terms = possible_hopping_terms_new_site(new_dim)
        # new_models = append_model_with_new_terms(increased_dim_model, new_terms)
        # spawn_stage.append((dim+1,1))

    if type(spawn_stage[-1]) == tuple:
        dim = spawn_stage[-1][0]
        num_branches_this_dim = spawn_stage[-1][1] # either a number or 'c'
        
        if dim == max_dimension:
            at_max_dim = True
        else:
            at_max_dim = False
        if spawn_stage[-1][1] == 'c':
            this_dimension_complete = True # champ this dim found
        else:
            this_dimension_complete = False
        if spawn_stage[-1][1] == dim - 1 :
            this_dimension_exhausted = True # all possible models this dim considered
        else:
            this_dimension_exhausted = False

        # now complete logic depending on which spawn_stage passed
        if (
            this_dimension_exhausted == False
            and 
            this_dimension_complete == False
        ):
            # add one parameter to given mod, 
            # return a list
            # spawn_stage -> (N, num_branches+1)
            present_terms = DataBase.get_constituent_names_from_name(mod)
            possible_new_terms_this_dimension = possible_hopping_terms_new_site(dim)
            nonpresent_possible_terms = list(
                set(possible_new_terms_this_dimension)
                - set(present_terms)
            )
            new_models = append_model_with_new_terms(mod, nonpresent_possible_terms)
            spawn_stage.append( (dim, num_branches_this_dim+1) )
        elif (
            this_dimension_complete == False
            and
            this_dimension_exhausted == True
        ):
            
            new_models = branch_champs_by_qubit_num[dim]
            spawn_stage.append((dim, 'c'))
            
            # return branch champs corresponding to this num qubits
            # to form a ghost branch
            # spawn_stage -> (N, 'c')
        
        elif (
            this_dimension_complete == True
            and
            at_max_dim == False
        ):
            increased_dim_model = increase_dimension_maintain_distinct_interactions(
                mod
            )
            # new_terms = possible_hopping_terms_new_site(dim+1)
            # new_models = append_model_with_new_terms(
            #     increased_dim_model, 
            #     new_terms
            # )
            new_models = [increased_dim_model]
            spawn_stage.append((dim+1, 0))
            # spawn_stage.append((dim+1, 1))
            
            # this num qubits complete, 
            # move up to higher dimension
            # return mod, since that was the winner of previous branch
            # and therefore winner for this num_qubits
            # spawn_stage -> (N+1, 1)
        elif (
            at_max_dim == True
            and
            this_dimension_complete == True
        ):
            spawn_stage.append('Complete')
#             new_models = branch champions which won their ghost as well
            
            all_branch_champions = []
            for q in range(2, max_dimension+1):
                all_branch_champions.extend(
                    branch_champs_by_qubit_num[q]
                )
            unique_branch_champs = list(set(all_branch_champions))
            won_multiple_branches = []
            for m in unique_branch_champs:
                if all_branch_champions.count(m) >= 2:
                    won_multiple_branches.append(m)

            min_dim = min(
                branch_champs_by_qubit_num.keys()
            )
            won_multiple_branches.extend(
                branch_champs_by_qubit_num[min_dim]
            )
            new_models = won_multiple_branches
    
    return new_models

    


##################################################################################
##################### Tree Finished Functions ############################################
##################################################################################


def spawn_depth_check(
    generator,
    max_spawn_depth_info,
    spawn_step, 
    **kwargs
):

    # print(
    #     "[ModGen] ", generator, 
    #     "\tspawn step:", 
    #     spawn_step, 
    #     "\t max:", 
    #     max_spawn_depth_info[generator]
    # )
    if spawn_step == max_spawn_depth_info[generator]:
        print("[ModGen] MAX SPAWN DEPTH REACHED FOR RULE ", generator)
        return True 
    else:
        return False


def max_num_qubits_reached_check(
    generator,
    max_num_qubits_info, 
    current_num_qubits, 
    **kwargs
):
    # print(
    #     "[ModGen] ", generator, 
    #     "\tcurrent_num_qubits:", 
    #     current_num_qubits, 
    #     "\t max:", 
    #     max_num_qubits_info[generator]
    # )
    if (
        current_num_qubits 
        == 
        max_num_qubits_info[generator]
    ):
        return True 
    else:
        return False

##################################################################################
##################### Topology classes ###########################################
##################################################################################

