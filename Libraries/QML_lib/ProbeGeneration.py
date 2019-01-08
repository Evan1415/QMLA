import numpy as np
import qutip
# import ExpectationValues
import DataBase


## Simluated Probes: random
def separable_probe_dict(
    max_num_qubits, 
    num_probes,
    **kwargs
):
    separable_probes = {}
    for i in range(num_probes):
        separable_probes[i,0] = random_probe(1)
        for j in range(1, 1+max_num_qubits):
            if j==1:
                separable_probes[i,j] = separable_probes[i,0]
            else: 
                separable_probes[i,j] = (
                    np.tensordot(
                        separable_probes[i,j-1],
                        random_probe(1), 
                        axes=0
                    ).flatten(order='c')
                )
            norm = np.linalg.norm(separable_probes[i,j])
            while (
                np.abs( norm -1) >
                1e-13

            ):
                print(
                    "non-unit norm: ", 
                    norm
                )
                # keep replacing until a unit-norm 
                separable_probes[i,j] = (
                    np.tensordot(
                        separable_probes[i,j-1], 
                        random_probe(1),
                        axes=0
                    ).flatten(order='c')
                )
                norm = np.linalg.norm(separable_probes[i,j])
            # print("unit norm:", np.abs(1-norm) )

    return separable_probes

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
    # if np.isclose(1.0, np.linalg.norm(probe), atol=1e-14) is False:
    #     print("Probe not normalised. Norm factor=", np.linalg.norm(probe)-1)
    #     return random_probe(num_qubits)
    while (
        np.abs( np.linalg.norm(probe) ) - 1
        > 
        1e-14 
    ):
        print("generating new random probe..")
        probe = random_probe(num_qubits)

    # print("random probe generated with norm:", np.linalg.norm(probe))
    return probe



## Specific experimental probes

def NV_centre_ising_probes_plus(
    max_num_qubits=2, 
    num_probes=40,
    noise_level=0.03, #from 1000 counts - Poissonian noise = 1/sqrt(1000)
    minimum_tolerable_noise = 1e-6,
    # minimum_tolerable_noise needed
    # or else run the risk of having 
    # exact eigenstate and no learning occurs, and crashes. 
    **kwargs    
):
    """
    Returns a dict of separable probes where the first qubit always acts on 
    a plus state. 
    """
    
    if minimum_tolerable_noise  > noise_level:
        noise_level = minimum_tolerable_noise
        # print("using minimum_tolerable_noise")
    print("noise level in plus probe:", noise_level)
    plus_state = np.array([1+0j, 1])/np.sqrt(2)
    random_noise = noise_level * random_probe(1)    
    noisy_plus = plus_state + random_noise
    norm_factor = np.linalg.norm(noisy_plus)
    noisy_plus = noisy_plus/norm_factor
    print("\n\t noisy plus:", noisy_plus )
    # print("\n\t has type:", type(noisy_plus))
    
    separable_probes = {}
    for i in range(num_probes):
#        separable_probes[i,0] = plus_state
        separable_probes[i,0] = noisy_plus
        for j in range(1, 1+max_num_qubits):
            if j==1:
                separable_probes[i,j] = separable_probes[i,0]
            else: 
                separable_probes[i,j] = (
                    np.tensordot(
                        separable_probes[i,j-1],
                        random_probe(1),
                        axes=0
                    ).flatten(order='c')
                )
            while (
                np.isclose(
                    1.0, 
                    np.linalg.norm(separable_probes[i,j]), 
                    atol=1e-14
                ) is  False
            ):
                print("non-unit norm: ", 
                    np.linalg.norm(separable_probes[i,j])
                )
                # keep replacing until a unit-norm 
                separable_probes[i,j] = (
                    np.tensordot(
                        separable_probes[i,j-1],
                        random_probe(1),
                        axes=0
                    ).flatten(order='c')
                )
    return separable_probes
    
    


def experimental_NVcentre_ising_probes(
    max_num_qubits=2, 
    num_probes=40
):
    """
    Returns a dict of separable probes where the first qubit always acts on 
    a plus state. 
    """
    plus_state = np.array([1, 1])/np.sqrt(2)
    noise_level = 0.03 # from 1000 counts - Poissonian noise = 1/sqrt(1000)
    random_noise = noise_level * random_probe(1)    
    noisy_plus = plus_state + random_noise
    norm_factor = np.linalg.norm(noisy_plus)
    noisy_plus = noisy_plus/norm_factor
    
    separable_probes = {}
    for i in range(num_probes):
#        separable_probes[i,0] = plus_state
        separable_probes[i,0] = noisy_plus
        for j in range(1, 1+max_num_qubits):
            if j==1:
                separable_probes[i,j] = separable_probes[i,0]
            else: 
                separable_probes[i,j] = (
                    np.tensordot(
                        separable_probes[i,j-1],
                        random_probe(1), 
                        axes=0
                    ).flatten(order='c')
                )
            while (
                np.isclose(
                    1.0, 
                    np.linalg.norm(separable_probes[i,j]), 
                    atol=1e-14
                ) is  False
            ):
                print("non-unit norm: ", np.linalg.norm(separable_probes[i,j]))
                # keep replacing until a unit-norm 
                separable_probes[i,j] = (
                    np.tensordot(
                        separable_probes[i,j-1], 
                        random_probe(1),
                        axes=0
                    ).flatten(order='c')
                )
    return separable_probes
  

def n_qubit_plus_state(num_qubits):
    one_qubit_plus = (1/np.sqrt(2) + 0j) * np.array([1,1])
    plus_n = one_qubit_plus
    for i in range(num_qubits-1):
        plus_n = np.kron(plus_n, one_qubit_plus)
    return plus_n


def plus_probes_dict(
    max_num_qubits, 
    **kwargs
):
    probe_dict = {}
    noise_level = 0.03
    for i in range(1,1+max_num_qubits):
        # dict key is tuple of form (0,i) for consistency with other probe dict generation functions. 
        new_probe =  n_qubit_plus_state(i)
        noisy_state = random_probe(i) * noise_level
        noisy_probe = new_probe + noisy_state
        norm = np.linalg.norm(noisy_probe)
        noisy_probe = noisy_probe/norm
        probe_dict[(0,i)] = noisy_probe
    return probe_dict 


def ideal_probe_dict(
    true_operator, 
    max_num_qubits,
    **kwargs
):
    probe_dict = {}
    true_dim = DataBase.get_num_qubits(true_operator)
    ideal_probe = DataBase.ideal_probe(true_operator)
    qt_probe = qutip.Qobj(ideal_probe)
    density_mtx = qutip.ket2dm(qt_probe)
    
    for i in range(1, 1+max_num_qubits):
        dict_key = (0, i) # for consistency with other probe dict functions
        if i==true_dim:
            probe_dict[dict_key] = ideal_probe
        elif i < true_dim:
            # TODO trace out from density mtx and retrieve closest pure state for here. 
            probe_dict[dict_key] = random_probe(i)
        else:
            # TODO replace this with traced out probe for 
            # case where sim num qubits < true num qubits
            rand = random_probe(1)
            new_probe = np.kron(
                probe_dict[(0, i-1)], 
                rand,
            )
            probe_dict[dict_key] = new_probe
    return probe_dict

