from __future__ import print_function # so print doesn't show brackets
import qinfer as qi
import numpy as np
import scipy as sp
import inspect
import time
import sys as sys
import os as os
from MemoryTest import print_loc
sys.path.append((os.path.join("..")))

global_print_loc = False 
use_linalg = False
use_sparse = False 
 
try: 
    import hamiltonian_exponentiation as h
    # TODO set to true after testing
    ham_exp_installed = True
     
except:
    ham_exp_installed = False
 
if (use_linalg): 
    # override and use linalg.expm even if hamiltonian_exponentiation is installed
    ham_exp_installed = False


def log_print(to_print_list, log_file, log_identifier):
    # identifier = str(str(time_seconds()) +" [Expectation Values]")
    if type(to_print_list)!=list:
        to_print_list = list(to_print_list)

    print_strings = [str(s) for s in to_print_list]
    to_print = " ".join(print_strings)
    with open(log_file, 'a') as write_log_file:
        print(log_identifier, str(to_print), file=write_log_file, flush=True)

     
## Partial trace functionality
 
def expectation_value(
    ham, t, state=None, 
    choose_random_probe=False,
    use_exp_custom=True, 
    enable_sparse=True, 
    print_exp_details=False,
    exp_fnc_cutoff=20, 
    compare_exp_fncs_tol=None, 
    log_file='QMDLog.log',
    log_identifier=None, 
    debug_plot_print=False
):

    if choose_random_probe is True: 
        num_qubits = int(np.log2(np.shape(ham)[0]))
        state = random_probe(num_qubits)
    elif random_probe is False and state is None: 
        log_print(["expectation value function: you need to \
            either pass a state or set choose_random_probe=True"],
            log_file=log_file, log_identifier=log_identifier
        )
 #    log_print(
 #    	[
 #    	'[Exp val func] Probe:', state
 #    	],
 #    	log_file=log_file,
 #    	log_identifier=log_identifier
	# )
    
    if compare_exp_fncs_tol is not None: # For testing custom ham-exp function
        u_psi_linalg = evolved_state(ham, t, state, 
            use_exp_custom=False, print_exp_details=print_exp_details,
            exp_fnc_cutoff=exp_fnc_cutoff
        )
        u_psi_exp_custom = evolved_state(ham, t, state,
            use_exp_custom=True, print_exp_details=print_exp_details,
            exp_fnc_cutoff=exp_fnc_cutoff
        )
        
        diff = np.max(np.abs(u_psi_linalg-u_psi_exp_custom))
        if (np.allclose(u_psi_linalg, u_psi_exp_custom, 
            atol=compare_exp_fncs_tol) == False
        ):
            log_print(["Linalg/ExpHam give different evolved state by", diff],
                log_file=log_file, log_identifier=log_identifier
            )
            u_psi = u_psi_linalg
        else:
            u_psi = u_psi_exp_custom
            
    else: # compute straight away; don't compare exponentiations
        if use_exp_custom and ham_exp_installed: 
            try:
              u_psi = evolved_state(ham, t, state, use_exp_custom=True,
                  print_exp_details=print_exp_details, 
                  exp_fnc_cutoff=exp_fnc_cutoff
              )
            except ValueError:
                log_print(["Value error when exponentiating Hamiltonian. Ham:\n",
                    ham, "\nProbe: ", state], log_file=log_file,
                    log_identifier=log_identifier
                )
        else:
            u_psi = evolved_state(
                ham, t, state, 
                use_exp_custom=False,
                print_exp_details=print_exp_details, 
                exp_fnc_cutoff=exp_fnc_cutoff
            )
    
    probe_bra = state.conj().T
    try:
        psi_u_psi = np.dot(probe_bra, u_psi)
    except UnboundLocalError: 
        log_print(
            [
            "UnboundLocalError when exponentiating Hamiltonian. t=", t, 
            "\nHam:\n", ham,
            "\nProbe: ", state
            ], log_file=log_file,
            log_identifier=log_identifier
        )
        raise
    
    expec_value = np.abs(psi_u_psi)**2 ## TODO MAKE 100% sure about this!!
    
    expec_value_limit=1.10000000001 # maximum permitted expectation value
    
    if expec_value > expec_value_limit:
        log_print(["expectation value function has value ", 
            np.abs(psi_u_psi**2)], log_file=log_file, 
            log_identifier=log_identifier
        )
        log_print(["t=", t, "\nham = \n ", ham, "\nprobe : \n", state, 
            "\nprobe normalisation:", np.linalg.norm(state), "\nU|p>:", 
            u_psi, "\nnormalisation of U|p>:", np.linalg.norm(u_psi), 
            "\n<p|U|p>:", psi_u_psi, "\nExpec val:", expec_value],
            log_file=log_file, log_identifier=log_identifier
        )
        log_print(["Recalculating expectation value using linalg."],
            log_file=log_file, log_identifier=log_identifier
        )
        u_psi = evolved_state(ham, t, state, 
            use_exp_custom=False, log_file=log_file, 
            log_identifier=log_identifier
        )
        psi_u_psi = np.dot(probe_bra, u_psi)
        expec_value = np.abs(psi_u_psi)**2 ## TODO MAKE 100% sure about this!!
        raise NameError('UnphysicalExpectationValue') 
    
    return expec_value


 
def evolved_state(ham, t, state, use_exp_custom=True, 
    enable_sparse=True, print_exp_details=False, exp_fnc_cutoff=10, log_file=None,
    log_identifier=None
):
    #import hamiltonian_exponentiation as h
    from scipy import linalg
    print_loc(global_print_loc)
  
    if t>1e6: ## Try limiting times to use to 1 million
        import random
        t = random.randint(1e6, 3e6) # random large number but still computable without error
    
#        t=1e6 # TODO PUT BACK IN. testing high t to find bug. 

    if use_exp_custom and ham_exp_installed:
        if log_file is not None:
            log_print(
                ["Using custom expm. Exponentiating\nt=",t, "\nHam=\n", ham],
                log_file, log_identifier
            )
        unitary = h.exp_ham(ham, t, enable_sparse_functionality=enable_sparse,
            print_method=print_exp_details, scalar_cutoff=t+1
        )
    else:
        if log_file is not None:
            iht = (-1j*ham*t)
            log_print(["Using linalg.expm. Exponentiating\nt=",t, "\nHam=\n",
                ham, "\n-iHt=\n", iht, "\nMtx elements type:", 
                type(iht[0][0]), "\nMtx type:", type(iht)], 
                log_file, log_identifier
            )
        unitary = linalg.expm(-1j*ham*t)
        
        if log_file is not None:
            log_print(["linalg.expm gives \nU=\n",unitary], log_file, log_identifier)
    
    ev_state = np.dot(unitary, state)

    if log_file is not None:
        log_print(["evolved state fnc. Method details printed in worker log. \nt=",
            t, "\nHam=\n", ham, "\nprobe=", state, "\nU=\n", unitary, "\nev_state=",
            ev_state], log_file, log_identifier
        )
    del unitary # to save space
    return ev_state


def traced_expectation_value_project_one_qubit_plus(
    ham,
    t, 
    state, 
):
    #TODO for simulations, don't want to use this -- want to use projection with access to full state, so not tracing out. 
    """ 
    Expectation value tracing out all but 
    first qubit to project onto plus state
    """
    import qutip 
    import numpy as np
    
    one_over_sqrt_two = 1/np.sqrt(2) + 0j 
    plus = np.array([one_over_sqrt_two, one_over_sqrt_two])
    one_qubit_plus = qutip.Qobj(plus)
    
    ev_state = evolved_state(ham, t, state)
    qstate = qutip.Qobj(ev_state)
    qstate.dims= [[2,2], [1,1]]
    traced_state = qstate.ptrace(0) # TODO: to generalise, make this exclude everything apart from 0th dimension ?
    expect_value = np.abs(qutip.expect(traced_state, one_qubit_plus))**2
    
    return expect_value
    

# Expecactation value function using Hahn inversion gate:

def hahn_evolution(ham, t, state, log_file=None, log_identifier=None):
    import qutip 
    import numpy as np
#    print("Hahn evo")
    #hahn_angle = np.pi/2
    #hahn = np.kron(hahn_angle*sigmaz(), np.eye(2))
    #inversion_gate = linalg.expm(-1j*hahn)
    # inversion gate generated as above, done once and hardocded since this doesn't change.
    inversion_gate = np. array([
        [0.-1.j, 0.+0.j, 0.+0.j, 0.+0.j],
        [0.+0.j, 0.-1.j, 0.+0.j, 0.+0.j],
        [0.+0.j, 0.+0.j, 0.+1.j, 0.+0.j],
        [0.+0.j, 0.+0.j, 0.+0.j, 0.+1.j]]
    )
    even_time_split = False
    if even_time_split:

        unitary_time_evolution = h.exp_ham(ham, t)

        total_evolution = np.dot(
            unitary_time_evolution,
            np.dot(inversion_gate,
                  unitary_time_evolution)
        )
    else:
        first_unitary_time_evolution = h.exp_ham(ham, t)
        second_unitary_time_evolution = h.exp_ham(ham, 2*t)
        total_evolution = np.dot(
            second_unitary_time_evolution,
            np.dot(inversion_gate,
                  first_unitary_time_evolution)
        )


#    print("total ev:\n", total_evolution)
    ev_state = np.dot(total_evolution, state)

    density_matrix = np.kron( ev_state, (ev_state.T).conj() )
    density_matrix = np.reshape(density_matrix, [4,4])
    reduced_matrix = partial_trace_out_second_qubit(
        density_matrix,
        qubits_to_trace = [1]
    )

    plus_state = np.array([1, 1])/np.sqrt(2)
    noise_level = 0.00 # from 1000 counts - Poissonian noise = 1/sqrt(1000) # should be ~0.03
    random_noise = noise_level * random_probe(1)    
    noisy_plus = plus_state + random_noise
    norm_factor = np.linalg.norm(noisy_plus)
    noisy_plus = noisy_plus/norm_factor
#    noisy_plus = np.array([1, 1])/np.sqrt(2)
    bra = noisy_plus.conj().T
    rho_state = np.dot(reduced_matrix, noisy_plus)
    expect_value = np.abs(np.dot(bra, rho_state))
#    print("Hahn. Time=",t, "\t ex = ", expect_value)
    
    return 1-expect_value
#    return expect_value



def swap_vector_elements_positions(input_vector, pos1, pos2):
    import copy
    new_vector = copy.deepcopy(input_vector)
    new_vector[pos1] = input_vector[pos2]
    new_vector[pos2] = input_vector[pos1]
    
    return new_vector

def partial_trace_out_second_qubit(global_rho, qubits_to_trace=[1]):
    
    # INPUTS
    """
     - global_rho: numpy array of the original full density matrix
     - qubits_to_trace: list of the qubit indexes to trace out from the full system
    """
    #print("trace fnc. global rho", global_rho)
    len_input_state = len(global_rho)
    input_num_qubits = int(np.log2(len_input_state))

    qubits_to_trace.reverse()

    num_qubits_to_trace = len(qubits_to_trace)
    output_matrix = [] #initialise the output reduced matrix

    for i in range(num_qubits_to_trace):
        k = qubits_to_trace[i]

        if k == num_qubits_to_trace:
            for p in range(0, int(len_input_state), 2):

                odd_positions = global_rho[p][::2]    # pick odd positions in the original matrix
                even_positions = global_rho[p+1][1::2]   #pick even positions in the original matrix

                output_matrix.append(
                    odd_positions + even_positions  
                )
    output_matrix = np.array(output_matrix)
    return output_matrix
    

def random_probe(num_qubits):
    dim = 2**num_qubits
    real = []
    imaginary = []
    complex_vectors = []
    for i in range(dim):
        real.append(np.random.uniform(low=-1, high=1))
        imaginary.append(np.random.uniform(low=-1, high=1))
        complex_vectors.append(real[i] + 1j*imaginary[i])

    a=np.array(complex_vectors)
    norm_factor = np.linalg.norm(a)
    probe = complex_vectors/norm_factor
    if np.isclose(1.0, np.linalg.norm(probe), atol=1e-14) is False:
        print("Probe not normalised. Norm factor=", np.linalg.norm(probe)-1)
        return random_probe(num_qubits)

    return probe


## for easy access to plus states to plot against
def n_qubit_plus_state(num_qubits):
    one_qubit_plus = (1/np.sqrt(2) + 0j) * np.array([1,1])
    plus_n = one_qubit_plus
    for i in range(num_qubits-1):
        plus_n = np.kron(plus_n, one_qubit_plus)
    return plus_n

 
# ##### ---------- -------------------- #####  
# """
# Wrapper function for expectation value, relying on above defined functions
# """
expec_val_function_dict = {
    'full_access' : expectation_value, 
    'hahn' : hahn_evolution,
    'trace_all_but_first' : traced_expectation_value_project_one_qubit_plus
}


    
def expectation_value_wrapper(method, **kwargs):       
    # print("method:", method)
    expectation_value_function = expec_val_function_dict[method]
    return expectation_value_function(**kwargs)

    