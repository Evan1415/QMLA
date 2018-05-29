from __future__ import print_function # so print doesn't show brackets

import qinfer as qi
import numpy as np
import scipy as sp
import warnings

from Evo import *
from ProbeStates import *
from MemoryTest import print_loc
from psutil import virtual_memory
import DataBase

global_print_loc=False
global debug_print
debug_print = False
global likelihood_dev
likelihood_dev = False

class GenSimQMD_IQLE(qi.FiniteOutcomeModel):
    r"""
    Describes the free evolution of a single qubit prepared in the
    :param np.array : :math:`\left|+\Psi\rangle` state under 
    a Hamiltonian :math:`H = \omega \sum_i \gamma_i / 2`
    of a set of (Pauli) operators given by 
    :param np.array oplist:  
    using the interactive QLE model proposed by [WGFC13a]_.
    
    :param np.array oplist: Set of operators whose sum defines the evolution Hamiltonian

    :param float min_freq: Minimum value for :math:`\omega` to accept as valid.
        This is used for testing techniques that mitigate the effects of
        degenerate models; there is no "good" reason to ever set this other
        than zero, other than to test with an explicitly broken model.
        
    :param str solver: Which solver to use for the Hamiltonian simulation.
        'scipy' invokes matrix exponentiation (i.e. time-independent evolution)
        -> fast, accurate when applicable
        'qutip' invokes ODE solver (i.e. time-dependent evolution can be also managed approx.)
        -> not invoked by deafult
    """
    
    ## INITIALIZER ##

    def __init__(self, oplist, modelparams, probecounter=None, true_oplist = None, truename=None, num_probes=40, probe_dict=None, trueparams = None, probelist = None, min_freq=0, solver='scipy', trotter=False, qle=True, use_exp_custom=True, exp_comparison_tol=None, enable_sparse=True, model_name=None, log_file='QMDLog.log', log_identifier=None):
        self._solver = solver #This is the solver used for time evolution scipy is faster, QuTip can handle implicit time dependent likelihoods
        self._oplist = oplist
        self._probecounter = probecounter
        self._a = 0
        self._b = 0 
        self.QLE = qle
        self._trotter = trotter
        self._modelparams = modelparams
        self._true_oplist = true_oplist
        self._trueparams = trueparams
        self._truename = truename
        self._true_dim = DataBase.get_num_qubits(self._truename)
        self.use_exp_custom = use_exp_custom
        self.enable_sparse = enable_sparse
        self.exp_comparison_tol = exp_comparison_tol  
        self._min_freq = min_freq
        self.ModelName = model_name
        self.inBayesUpdates = False
        self.ideal_probe = None
        self.IdealProbe = DataBase.ideal_probe(self.ModelName)
        self.ideal_probelist = None
        self.log_file = log_file
        self.log_identifier = log_identifier
        if true_oplist is not None and trueparams is None:
            raise(ValueError('\nA system Hamiltonian with unknown parameters was requested'))
        if true_oplist is None:
            warnings.warn("\nI am assuming the Model and System Hamiltonians to be the same", UserWarning)
            self._trueHam = None
        else:
           #self._trueHam = getH(trueparams, true_oplist)
#           self._trueHam = np.tensordot(trueparams, true_oplist, axes=1)
            self._trueHam = None

           #print("true ham = \n", self._trueHam)
#TODO: changing to try get update working for >1 qubit systems -Brian
        if debug_print: print("Gen sim. True ham has been set as : ")
        if debug_print: print(self._trueHam)
        
        if debug_print:print("True params & true_oplist: [which are passed to getH] ")
        if debug_print:print(trueparams)
        if debug_print:print(true_oplist)
        super(GenSimQMD_IQLE, self).__init__(self._oplist)
        #probestate = choose_randomprobe(self._probelist)
        probestate = def_randomprobe(oplist,modelpars=None)
        self.ProbeState=None
        self.NumProbes = num_probes
        if probe_dict is None: 
            self._probelist = seperable_probe_dict(max_num_qubits=12, num_probes = self.NumProbes) # TODO -- make same as number of qubits in model.
        else:
            self._probelist = probe_dict    
    ## PROPERTIES ##
    
    @property
    def n_modelparams(self):
        return len(self._oplist)

    # Modelparams is the list of parameters in the System Hamiltonian - the ones we want to know
    # Possibly add a second axis to modelparams.    
    @property
    def modelparam_names(self):
        modnames = ['w0']
        for modpar in range(self.n_modelparams-1):
            modnames.append('w' + str(modpar+1))
        return modnames

    # expparams are the {t, w1, w2, ...} guessed parameters, i.e. each element 
    # is a particle with a specific sampled value of the corresponding parameter
  
    @property
    def expparams_dtype(self):
        expnames = [('t', 'float')]
        for exppar in range(self.n_modelparams):
            expnames.append(('w_' + str(exppar+1), 'float'))
        return expnames
    
    @property
    def is_n_outcomes_constant(self):
        """
        Returns ``True`` if and only if the number of outcomes for each
        experiment is independent of the experiment being performed.
        
        This property is assumed by inference engines to be constant for
        the lifetime of a Model instance.
        """
        return True
    
    ## METHODS ##

    def are_models_valid(self, modelparams):
        return np.all(np.abs(modelparams) > self._min_freq, axis=1)
    
    def n_outcomes(self, expparams):
        """
        Returns an array of dtype ``uint`` describing the number of outcomes
        for each experiment specified by ``expparams``.
        
        :param numpy.ndarray expparams: Array of experimental parameters. This
            array must be of dtype agreeing with the ``expparams_dtype``
            property.
        """
        return 2
        

    def likelihood(self, outcomes, modelparams, expparams):
        super(GenSimQMD_IQLE, self).likelihood(
            outcomes, modelparams, expparams
        )
        print_loc(global_print_loc)
        cutoff=min(len(modelparams), 5)
        num_particles = modelparams.shape[0]
        #print("Likelihood called; _a=", self._a)
        self._a += 1
        if self._a % 2 == 1:
            self._b += 1
        #print("(a,b)= ", self._a, self._b)
        print_loc(global_print_loc)

        num_parameters = modelparams.shape[1]
        print_loc(global_print_loc)

        true_dim = np.log2(self._true_oplist[0].shape[0])
        sim_dim = np.log2(self._oplist[0].shape[0])
        
        
        if  num_particles == 1:
            sample = np.array([expparams.item(0)[1:]])[0:num_parameters]
            true_evo = True
            operators = self._true_oplist
            if true_dim > sim_dim: 
                operators = DataBase.reduced_operators(self._truename, int(sim_dim))
                #print("True dim=", true_dim, "Sim dim=", sim_dim)
                #print("operators:", operators)
            else:
                operators = self._true_oplist
            params = [self._trueparams]
            
        else:
            sample = np.array([expparams.item(0)[1:]])
            true_evo = False
            operators = self._oplist
            params = modelparams

#        ham_num_qubits = np.log2(self._oplist[0].shape[0])
        ham_num_qubits = np.log2(operators[0].shape[0])
        
        
        
        """
        if num_particles==1: 
          print("True (", self.ModelName , "); probe id: (", (self._b % int(self.NumProbes)), ", ",  ham_num_qubits, ")")
#          print("modelparams : ", modelparams) 
        else: 
          print("Simulated(", self.ModelName , "); probe id: (", (self._b % int(self.NumProbes)), ",",  ham_num_qubits, ")")      
        """
        
        if self.inBayesUpdates:
          if self.ideal_probe is not None:
            probe = self.ideal_probe # this won't work
          elif self.ideal_probelist is not None: 
            probe = self.ideal_probelist[self._b % 2] # this won't work
          else:
            print("Either ideal_probe or ideal_probes must be given")
        else:
          probe = self._probelist[(self._b % int(self.NumProbes)), ham_num_qubits]
        
        
        ham_minus = np.tensordot(sample, self._oplist, axes=1)[0]
        print_loc(global_print_loc)

        if len(modelparams.shape) == 1:
            modelparams = modelparams[..., np.newaxis]
            
        times = expparams['t']
        if self.QLE is True:
            pr0 = get_pr0_array_qle(t_list=times, modelparams=params, oplist=operators, probe=probe, use_exp_custom=self.use_exp_custom, exp_comparison_tol=self.exp_comparison_tol, enable_sparse = self.enable_sparse, log_file=self.log_file, log_identifier=self.log_identifier)    

        else: 
            pr0 = get_pr0_array_iqle(t_list=times, modelparams=params, oplist=operators, ham_minus=ham_minus, probe=probe, use_exp_custom=self.use_exp_custom, exp_comparison_tol=self.exp_comparison_tol, enable_sparse = self.enable_sparse, log_file=self.log_file, log_identifier=self.log_identifier)    

        likelihood_array = qi.FiniteOutcomeModel.pr0_to_likelihood_array(outcomes, pr0)
        return likelihood_array


def seperable_probe_dict(max_num_qubits, num_probes):
    seperable_probes = {}
    for i in range(num_probes):
        seperable_probes[i,0] = random_probe(1)
        for j in range(1, 1+max_num_qubits):
            if j==1:
                seperable_probes[i,j] = seperable_probes[i,0]
            else: 
                seperable_probes[i,j] = np.tensordot(seperable_probes[i,j-1], random_probe(1), axes=0).flatten(order='c')
            if np.linalg.norm(seperable_probes[i,j]) < 0.999999999 or np.linalg.norm(seperable_probes[i,j]) > 1.0000000000001:
                print("non-unit norm: ", np.linalg.norm(seperable_probes[i,j]))
    return seperable_probes

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
    if np.linalg.norm(probe) -1  > 1e-10:
        print("Probe not normalised. Norm factor=", np.linalg.norm(probe)-1)
    return probe


        
