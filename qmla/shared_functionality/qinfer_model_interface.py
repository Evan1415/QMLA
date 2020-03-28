from __future__ import print_function  # so print doesn't show brackets

import numpy as np
import sys
import warnings
import copy

import scipy as sp
import qinfer as qi

import qmla.experimental_data_processing
import qmla.get_growth_rule
import qmla.memory_tests
import qmla.shared_functionality.probe_set_generation
import qmla.database_framework
import qmla.logging 

global_print_loc = False
global debug_print
debug_print = False
global debug_log_print
debug_log_print = False
global debug_print_file_line
debug_print_file_line = False


class QInferModelQMLA(qi.FiniteOutcomeModel):
    r"""
    Describes the free evolution of a single qubit prepared in the
    :param np.array : :math:`\left|+\Psi\rangle` state under
    a Hamiltonian :math:`H = \omega \sum_i \gamma_i / 2`
    of a set of (Pauli) operators given by
    :param np.array oplist:
    using the interactive QLE model proposed by [WGFC13a]_.

    :param np.array oplist: Set of operators whose sum
        defines the evolution Hamiltonian

    :param float min_freq: Minimum value for :math:`\omega` to accept as valid.
        This is used for testing techniques that mitigate the effects of
        degenerate models; there is no "good" reason to ever set this other
        than zero, other than to test with an explicitly broken model.

    :param str solver: Which solver to use for the Hamiltonian simulation.
        'scipy' invokes matrix exponentiation (i.e. time-independent evolution)
        -> fast, accurate when applicable
        'qutip' invokes ODE solver (i.e. time-dependent evolution can
        be also managed approx.)
        -> not invoked by deafult
    """

    ## INITIALIZER ##

    def __init__(
        self,
        model_name,
        modelparams,
        oplist,
        true_oplist,
        truename,
        trueparams,
        num_probes,
        probe_dict,
        sim_probe_dict,
        growth_generation_rule,
        use_experimental_data,
        experimental_measurements,
        experimental_measurement_times,
        log_file,
        **kwargs
    ):
        self._oplist = oplist
        self._a = 0
        self._b = 0
        self._modelparams = modelparams
        self.signs_of_inital_params = np.sign(modelparams)
        self._true_oplist = true_oplist
        self._trueparams = trueparams
        self._truename = truename
        self._true_dim = qmla.database_framework.get_num_qubits(self._truename)
        self.use_experimental_data = use_experimental_data
        self.log_file = log_file
        self.growth_generation_rule = growth_generation_rule
        try:
            self.growth_class = qmla.get_growth_rule.get_growth_generator_class(
                growth_generation_rule=self.growth_generation_rule,
                use_experimental_data=self.use_experimental_data,
                log_file=self.log_file
            )
        except BaseException:
            self.log_print(
                [
                    "Could not instantiate growth rule {}. Terminating".foramt(
                        self.growth_generation_rule
                    )
                ]
            )
        self.experimental_measurements = experimental_measurements
        self.experimental_measurement_times = experimental_measurement_times
        self._min_freq = 0 # what does this do?
        self._solver = 'scipy'
        # This is the solver used for time evolution scipy is faster
        # QuTip can handle implicit time dependent likelihoods

        self.model_name = model_name
        self.model_dimension = qmla.database_framework.get_num_qubits(self.model_name)
        self.inBayesUpdates = False
        if true_oplist is not None and trueparams is None:
            raise(
                ValueError(
                    '\nA system Hamiltonian with unknown \
                    parameters was requested'
                )
            )
        super(QInferModelQMLA, self).__init__(self._oplist)

        try:
            self.probe_dict = probe_dict
            self.sim_probe_dict = sim_probe_dict
            self.probe_number = num_probes
        except:
            raise ValueError(
                "Probe dictionaries not passed to Qinfer model"
            )

    def log_print(
        self, 
        to_print_list, 
        log_identifier=None
    ):
        if log_identifier is None: 
            log_identifier = 'QInfer interface'

        qmla.logging.print_to_log(
            to_print_list = to_print_list, 
            log_file = self.log_file, 
            log_identifier = log_identifier
        )

    def log_print_debug(
        self, 
        to_print_list
    ):
        r"""
        Log print if global debug_log_print set to True. 
        """
        if debug_log_print:
            self.log_print(
                to_print_list = to_print_list,
                log_identifier = 'QInfer interface debug'
            )

    ## PROPERTIES ##
    @property
    def n_modelparams(self):
        r"""
        Number of parameters in the specific model 
        typically, in QMLA, we have one parameter per model.
        """

        return len(self._oplist)

    @property
    def modelparam_names(self):
        r"""
        Inherited from Qinfer:
        Returns the names of the various model parameters admitted by this
        model, formatted as LaTeX strings.
        """
        modnames = ['w0']
        for modpar in range(self.n_modelparams - 1):
            modnames.append('w' + str(modpar + 1))
        return modnames

    # expparams are the {t, w1, w2, ...} guessed parameters, i.e. each 
    # particle has a specific sampled value of the corresponding
    # parameter
    # 

    @property
    def expparams_dtype(self):
        r"""
        Modified from Qinfer:
        Returns the dtype of an experiment parameter array. For a
        model with single-parameter control, this will likely be a scalar dtype,
        such as ``"float64"``. More generally, this can be an example of a
        record type, such as ``[('time', py.'float64'), ('axis', 'uint8')]``.
        This property is assumed by inference engines to be constant for
        the lifetime of a Model instance.
        In the context of QMLA the expparams_dtype are assumed to be a list of tuple where
        the first element of the tuple identifies the parameters (including type) while the second element is
        the actual type of of the parameter, typicaly a float.

        """
        expnames = [('t', 'float')]
        for exppar in range(self.n_modelparams):
            expnames.append(('w_' + str(exppar + 1), 'float'))
        return expnames

    ## METHODS ##

    def are_models_valid(self, modelparams):
        # Before setting new distribution after resampling,
        # checks that all parameters have same sign as the
        # initial given parameter for that term.
        # Otherwise, redraws the distribution.
        same_sign_as_initial = False
        if same_sign_as_initial == True:
            new_signs = np.sign(modelparams)
            validity_by_signs = np.all(
                np.sign(modelparams) == self.signs_of_inital_params,
                axis=1
            )
            return validity_by_signs
        else:
            validity = np.all(np.abs(modelparams) > self._min_freq, axis=1)
            return validity

    def n_outcomes(self, expparams):
        r"""
        Returns an array of dtype ``uint`` describing the number of outcomes
        for each experiment specified by ``expparams``.

        :param numpy.ndarray expparams: Array of experimental parameters. This
            array must be of dtype agreeing with the ``expparams_dtype``
            property.
        """
        return 2

    def likelihood(
        self,
        outcomes,
        modelparams,
        expparams
    ):
        r"""
            Inherited from Qinfer:
            Function to calculate likelihoods for all the particles
            
            Longish description:
            Calculates the probability of each given outcome, conditioned on each
            given model parameter vector and each given experimental control setting.

            :param np.ndarray outcomes: outcomes of the experiments

            :param np.ndarray modelparams: 
                values of the model parameters particles 
                A shape ``(n_particles, n_modelparams)``
                array of model parameter vectors describing the hypotheses for
                which the likelihood function is to be calculated.
            
            :param np.ndarray expparams: 
                experimental parameters, 
                A shape ``(n_experiments, )`` array of
                experimental control settings, with ``dtype`` given by 
                :attr:`~qinfer.Simulatable.expparams_dtype`, describing the
                experiments from which the given outcomes were drawn.
                
            :rtype: np.ndarray
            :return: A three-index tensor ``L[i, j, k]``, where ``i`` is the outcome
                being considered, ``j`` indexes which vector of model parameters was used,
                and where ``k`` indexes which experimental parameters where used.
                Each element ``L[i, j, k]`` then corresponds to the likelihood
                :math:`\Pr(d_i | \vec{x}_j; e_k)`.
            """

        
        super(QInferModelQMLA, self).likelihood(
            outcomes, modelparams, expparams
        )  # just adds to self._call_count (Qinfer abstact model class)
        times = expparams['t'] # times to compute likelihood for. typicall only per experiment. 
        num_particles = modelparams.shape[0]
        num_parameters = modelparams.shape[1]
        # assumption is that calls to likelihood are paired: 
        # one for system, one for simulator
        # therefore the same probe should be assumed for consecutive calls
        # probe id is tracked with _a and _b.
        # i.e. increments each 2nd call, loops back when probe dict exhausted
        self._a += 1
        if self._a % 2 == 1:
            self._b += 1
        self.probe_counter = (self._b % int(self.probe_number)) 


        if num_particles == 1:
            # TODO better mechanism to determine if true_evo, 
            # rather than assuming 1 particle => system
            # call the system, use the true paramaters as a single particle, 
            # to get the true evolution
            true_evo = True
            params = [copy.deepcopy(self._trueparams)]
        else:
            true_evo = False
            params = modelparams

        # if (
        #     true_evo == True
        #     and
        #     self.use_experimental_data == True
        # ):
        #     # TODO move true experimental_data case to growth rule specific get_system_pr0 fnc
        #     time = expparams['t']
        #     self.log_print_debug(
        #         [
        #             'Getting system outcome',
        #             'time:\n', time
        #         ],
        #     )
        #     try:
        #         # If time already exists in experimental data
        #         experimental_expec_value = self.experimental_measurements[time]
        #     except BaseException:
        #         experimental_expec_value = qmla.experimental_data_processing.nearest_experimental_expect_val_available(
        #             times=self.experimental_measurement_times,
        #             experimental_data=self.experimental_measurements,
        #             t=time
        #         )
        #     self.log_print_debug(
        #         [
        #             "Using experimental time", time,
        #             "\texp val:", experimental_expec_value
        #         ],
        #     )
        #     pr0 = np.array([[experimental_expec_value]])

        # else:
        try:
            if true_evo:
                pr0 = self.get_system_pr0_array(
                    times=times,
                    particles=params,
                    # oplist=operators,
                )
            else:
                pr0 = self.get_simulator_pr0_array(
                    times=times,
                    particles=params,
                    # oplist=operators,
                ) 
        except:
            self.log_print(
                [
                    "Failed to compute pr0.",
                ]
            )
            sys.exit()

        likelihood_array = (
            qi.FiniteOutcomeModel.pr0_to_likelihood_array(
                outcomes, pr0
            )
        )
        self.log_print_debug(
            [
                'Simulating experiment.',
                'times:', times,
                'true_evo:', true_evo,
                'len(outcomes):', len(outcomes),
                '_a = {}, _b={}'.format(self._a, self._b),
                'probe counter:', self.probe_counter,
                '\nexp:', expparams,
                '\nOutcomes:', outcomes,
                '\nmodelparams:', params,
            ]
        )
        self.log_print_debug(
            [
                "Outcomes: ", outcomes, 
                "\nPr0: ", pr0, 
                "\nLikelihood: ", likelihood_array
            ]
        )

        return likelihood_array

    def get_system_pr0_array(
        self, 
        times,
        particles, 
        # **kwargs
    ):
        operator_list = self._true_oplist
        ham_num_qubits = self._true_dim
        # format of probe dict keys: (probe_id, qubit_number)
        probe = self.probe_dict[
            self.probe_counter,
            ham_num_qubits
        ]
        # TODO: could just work with true_hamiltonian, worked out on __init__
        return self.default_pr0_from_modelparams_times(
            t_list = times,
            particles = particles, 
            oplist = operator_list, 
            probe = probe, 
            # **kwargs
        )

    def get_simulator_pr0_array(
        self, 
        particles, 
        times,
        # **kwargs
    ):
        ham_num_qubits = self.model_dimension
        # format of probe dict keys: (probe_id, qubit_number)
        probe = self.sim_probe_dict[
            self.probe_counter,
            ham_num_qubits 
        ]
        operator_list = self._oplist
        return self.default_pr0_from_modelparams_times(
            t_list = times, 
            particles = particles, 
            oplist = operator_list, 
            probe = probe, 
            # **kwargs
        )

    def default_pr0_from_modelparams_times(
        self,
        t_list,
        particles,
        oplist,
        probe,
        **kwargs
    ):
        r"""
            Compute probabilities of available outputs as an array.

            :param np.ndarray t_list: 
                List of times on which to perform experiments
            :param np.ndarray modelparams: 
                values of the model parameters particles 
                A shape ``(n_particles, n_modelparams)``
                array of model parameter vectors describing the hypotheses for
                which the likelihood function is to be calculated.
            :param list oplist:
                list of the operators defining the model
            :param np.ndarray probe: quantum state to evolve
            :param GrowthRule growth_class: 
        """

        from rq import timeouts
        self.log_print_debug(
            [
                "Probe[0] (dimension {}): \n {}".format(
                    np.shape(probe),
                    probe[0],
                ),
                "Times: ", t_list
            ]
        )

        num_particles = len(particles)
        num_times = len(t_list)
        output = np.empty([num_particles, num_times])

        for evoId in range(num_particles):  
            try:
                ham = np.tensordot(
                    particles[evoId], oplist, axes=1
                )
            except BaseException:
                self.log_print(
                    [
                        "Failed to build Hamiltonian.",
                        "\nparticles:", particles[evoId],
                        "\noplist:", oplist
                    ],
                )
                raise

            for tId in range(len(t_list)):
                t = t_list[tId]
                if t > 1e6:  # Try limiting times to use to 1 million
                    import random
                    # random large number but still computable without error
                    t = random.randint(1e6, 3e6)
                try:
                    likel = self.growth_class.expectation_value(
                        ham=ham,
                        t=t,
                        state=probe,
                        log_file=self.log_file,
                        log_identifier='get pr0 call exp val'
                    )
                    output[evoId][tId] = likel

                except NameError:
                    self.log_print(
                        [
                            "Error raised; unphysical expecation value.",
                            "\nHam:\n", ham,
                            "\nt=", t,
                            "\nState=", probe,
                        ],
                    )
                    sys.exit()
                except timeouts.JobTimeoutException:
                    self.log_print(
                        [
                            "RQ Time exception. \nprobe=",
                            probe,
                            "\nt=", t, "\nHam=",
                            ham
                        ],
                    )
                    sys.exit()

                if output[evoId][tId] < 0:
                    print("NEGATIVE PROB")
                    self.log_print(
                        [
                            "[QLE] Negative probability : \
                            \t \t probability = ",
                            output[evoId][tId]
                        ],
                    )
                elif output[evoId][tId] > 1.001:
                    self.log_print(
                        [
                            "[QLE] Probability > 1: \
                            \t \t probability = ",
                            output[evoId][tId]
                        ]
                    )
        return output



class QInferNVCentreExperiment(QInferModelQMLA):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_system_pr0_array(
        self, 
        times,
        particles, 
        **kwargs
    ):
        # time = expparams['t']
        if len(times) > 1:
            self.log_print("Multiple times given to experimental true evoluation:", times)
            sys.exit()

        time = times[0]
        self.log_print(
            [
                'Getting system outcome',
                'time:\n', time
            ]
        )
        
        try:
            # If time already exists in experimental data
            experimental_expec_value = self.experimental_measurements[time]
            self.log_print_debug(
                [
                    "Try has worked."
                ]
            )
        except BaseException:
            # map to nearest experimental time
            self.log_print_debug(
                [
                    "In except.",
                    # "exp times: \n{} \n exp meas: {}".format(
                    #     self.experimental_measurement_times, 
                    #     self.experimental_measurements
                    # )
                ]
            )
            try:
                experimental_expec_value = qmla.experimental_data_processing.nearest_experimental_expect_val_available(
                    times=self.experimental_measurement_times,
                    experimental_data=self.experimental_measurements,
                    t=time
                )
            except:
                self.log_print_debug(
                    [
                        "Failed to get experimental data point"
                    ]
                )
                raise
            self.log_print_debug(
                [
                    "experimental value for t={}: {}".format(
                        time, 
                        experimental_expec_value
                    )
                ]
            )
        self.log_print_debug(
            [
                "Using experimental time", time,
                "\texp val:", experimental_expec_value
            ],
        )
        pr0 = np.array([[experimental_expec_value]])
        self.log_print_debug(
            [
                "pr0 for system:", pr0
            ]
        )
        return pr0

    # def get_simulator_pr0_array(
    #     self, 
    #     particles, 
    #     times,
    #     # **kwargs
    # ):
    # TODO map times to times available in the experimental dataset

