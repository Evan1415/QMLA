import argparse
import os
import sys
import pickle

import qmla.get_growth_rule
import qmla.database_framework as database_framework
import qmla.logging

__all__ = [
    'ControlsQMLA',
    'parse_cmd_line_args'
]

"""
This file provides functionality to parse command line arguments 
passed via the QMLA launch scripts. 
These are gathered into a single class instance which can be probed by 
the QMLA instance to implement user specifications. 
"""

class ControlsQMLA():
    r"""
    Storage for configuration of a QMLA instance. 

    Command line arguments specify details about the QMLA instance,
    such as number of experiments/particles etc, required to implement
    the QMLA instance.
    The command line arguments are stored together in this class. 
    The class is then given to the :class:`qmla.QuantumModelLearningAgent` instance, 
    which uses those details into the implementation.
    In particular, the :class:`~qmla.growth_rules.GrowthRule` of the true model 
    is instantiated by calling :meth:`~qmla.get_growth_generator_class`. 
    This growth rule instance is the master growth rule for the QMLA instance: the true 
    model is defined as the true model of that instance. 
    Likewise instances are generated for all of the growth rules specified by the user:
    these instances are associated with the growth rule :class:`~qmla.GrowthRuleTree` objects. 

    :param dict arguments: command line arguments, parsed into a dict.
    """

    def __init__(
        self,
        arguments,
        **kwargs
    ):
        self.log_file = arguments.log_file

        # Get growth rule instances for true and alternative growth rules
        self.growth_generation_rule = arguments.growth_generation_rule
        try:
            self.growth_class = qmla.get_growth_rule.get_growth_generator_class(
                growth_generation_rule=self.growth_generation_rule,
                true_params_path = arguments.true_params_pickle_file,
                plot_probes_path = arguments.probes_plot_file, 
                log_file=self.log_file
            )
        except BaseException:
            raise
            self.growth_class = None

        self.alternative_growth_rules = arguments.alternative_growth_rules
        self.generator_list = [self.growth_generation_rule]
        self.generator_list.extend(self.alternative_growth_rules)
        self.generator_list = list(set(self.generator_list))
        self.unique_growth_rule_instances = {
            gen : qmla.get_growth_rule.get_growth_generator_class(
                    growth_generation_rule = gen, 
                    log_file = self.log_file
                )
            for gen in self.alternative_growth_rules
        }
        self.unique_growth_rule_instances[self.growth_generation_rule] = self.growth_class

        # self.probe_max_num_qubits_all_growth_rules = max( 
        #     [
        #         gr.max_num_probe_qubits for gr in 
        #         list(self.unique_growth_rule_instances.values())
        #     ]
        # )

        self.qhl_mode_multiple_models = bool(arguments.qhl_mode_multiple_models)

        # Get (or set) true parameters from parameter files shared among instances within the same run. 
        if arguments.true_params_pickle_file is None: 
            try:
                true_params_info = qmla.set_shared_parameters(
                    growth_class = self.growth_class,  
                )
            except:
                self.log_print(["Failed to set shared parameters"])
                raise
        else:
            true_params_info = pickle.load(
                open(
                    arguments.true_params_pickle_file, 
                    'rb'
                )
            )
        self.true_model = true_params_info['true_model']
        self.true_model_name = database_framework.alph(self.true_model)
        self.true_model_class = database_framework.Operator(
            self.true_model_name
        )
        self.true_model_terms_matrices = self.true_model_class.constituents_operators
        self.true_model_terms_params = true_params_info['params_list']
        self.true_params_pickle_file = arguments.true_params_pickle_file
        self.log_print([ "Shared true params set for this instance."])

        # # Get essentials out of growth_rule class
        # self.dataset = self.growth_class.experimental_dataset
        # self.data_max_time = self.growth_class.max_time_to_consider  # arguments.data_max_time
        # self.num_probes = self.growth_class.num_probes

        # Store parameters which were passed as arguments to implement_qmla.py
        self.prior_pickle_file = arguments.prior_pickle_file
        self.qhl_mode = bool(arguments.qhl_mode)
        self.further_qhl = bool(arguments.further_qhl)
        self.use_rq = bool(arguments.use_rq)
        self.num_experiments = arguments.num_experiments
        self.num_particles = arguments.num_particles
        self.num_times_bayes = arguments.num_times_bayes
        self.bayes_lower = arguments.bayes_lower # TODO put inside growth rule
        self.bayes_upper = arguments.bayes_upper
        self.save_plots = bool(arguments.save_plots)
        self.store_particles_weights = bool(arguments.store_particles_weights)
        self.resample_threshold = arguments.resample_threshold  # TODO put inside growth rule
        self.resample_a = arguments.resample_a
        self.pgh_factor = arguments.pgh_factor
        self.pgh_exponent = arguments.pgh_exponent
        self.increase_pgh_time = bool(arguments.increase_pgh_time)
        self.pickle_qmd_class = bool(arguments.pickle_qmd_class)
        self.qmla_id = arguments.qmla_id
        self.host_name = arguments.host_name
        self.port_number = arguments.port_number
        self.results_directory = arguments.results_directory
        if not self.results_directory.endswith('/'):
            self.results_directory += '/'
        self.rq_timeout = arguments.rq_timeout
        self.cumulative_csv = arguments.cumulative_csv
        self.true_expec_path = arguments.true_expec_path
        self.probes_plot_file = arguments.probes_plot_file
        self.reallocate_resources = bool(arguments.reallocate_resources)
        self.probe_noise_level = arguments.probe_noise_level # TODO put in growth rule

        # Create some new paths/parameters for storing results
        self.long_id = '{0:03d}'.format(self.qmla_id)
        self.plots_directory = self.results_directory + 'plots/'
        if not os.path.exists(self.results_directory):
            try:
                os.makedirs(self.results_directory)
            except FileExistsError:
                pass

        if not os.path.exists(self.plots_directory):
            try:
                os.makedirs(self.plots_directory)
            except FileExistsError:
                pass
        
        self.latex_mapping_file = arguments.latex_mapping_file
        if self.latex_mapping_file is None: 
            self.latex_name_map_file_path = os.path.join(
                self.results_directory, 
                'LatexMapping.txt'
            )

        if self.further_qhl:
            # further qhl model uses different results file names to distinguish
            self.results_file = self.results_directory + 'further_qhl_results_' + \
                str(self.long_id) + '.p' 
            self.class_pickle_file = self.results_directory + \
                'further_qhl_qml_class_' + str(self.long_id) + '.p'
        else:
            self.results_file = self.results_directory + 'results_' + \
                str(self.long_id) + '.p' 
            self.class_pickle_file = self.results_directory + \
                'qmla_class_' + str(self.long_id) + '.p'

    def log_print(self, to_print_list):
        r"""Wrapper for :func:`~qmla.print_to_log`"""
        qmla.logging.print_to_log(
            to_print_list=to_print_list,
            log_file=self.log_file,
            log_identifier='Setting QMLA controls'
        )


def parse_cmd_line_args(args):
    r"""
    Parse command line arguments, store and return in a single class instance. 
    
    Defaults and help for all useable command line arguments are specified here.
    These are parsed, then passed to a :class:`~qmla.ControlsQMLA` instance,
    which is given to the :class:`~qmla.QuantumModelLearningAgent` instance 
    for ease of access. 

    :param list args: command line arguments (i.e. sys.argv[1:]).
    :return ControlsQMLA qmla_controls: object with all required data for this 
        QMLA instance. 
    """

    parser = argparse.ArgumentParser(description='Pass variables for QMLA.')

    # Parse command line arguments

    parser.add_argument(
        '-qhl', '--qhl_mode',
        help="Bool to test QHL on given true operator only.",
        type=int,
        default=0
    )

    parser.add_argument(
        '-fq', '--further_qhl',
        help="Bool to perform further QHL on best models from previous run.",
        type=int,
        default=0
    )

    # QMD parameters -- fundamentals such as number of particles etc

    parser.add_argument(
        '-e', '--num_experiments',
        help='Number of experiments to use for the learning process',
        type=int,
        default=10
    )
    parser.add_argument(
        '-p', '--num_particles',
        help='Number of particles to use for the learning process',
        type=int,
        default=20
    )
    parser.add_argument(
        '-bt', '--num_times_bayes',
        help='Number of times to consider in Bayes function.',
        type=int,
        default=5
    )
    parser.add_argument(
        '-rq', '--use_rq',
        help='Bool whether to use RQ for parallel or not.',
        type=int,
        default=1
    )

    parser.add_argument(
        '-bu', '--bayes_upper',
        help='Higher Bayes threshold.',
        type=int,
        default=100
    )

    parser.add_argument(
        '-bl', '--bayes_lower',
        help='Lower Bayes threshold.',
        type=int,
        default=1
    )

    # Include optional plots
    parser.add_argument(
        '-pt', '--save_plots',
        help='True: save all plots for this QMD; False: do not.',
        type=int,
        default=False
    )

    parser.add_argument(
        '-prtwt', '--store_particles_weights',
        help='True: Store all particles and weights from learning.',
        type=int,
        default=0
    )

    # QInfer parameters, i.e. resampling a and resamping threshold, pgh
    # prefactor.
    parser.add_argument(
        '-rt', '--resample_threshold',
        help='Resampling threshold for QInfer.',
        type=float,
        default=0.5
    )
    parser.add_argument(
        '-ra', '--resample_a',
        help='Resampling a for QInfer.',
        type=float,
        default=0.95
    )
    parser.add_argument(
        '-pgh', '--pgh_factor',
        help='Resampling threshold for QInfer.',
        type=float,
        default=1.0
    )
    parser.add_argument(
        '-pgh_exp', '--pgh_exponent',
        help='for use in time heuristic according to 1/sigma**exponent',
        type=float,
        default=1.0
    )

    parser.add_argument(
        '-pgh_incr', '--increase_pgh_time',
        help='Boost times found by PGH heursitic. Bool.',
        type=int,
        default=0
    )

    # Redis environment
    parser.add_argument(
        '-host', '--host_name',
        help='Name of Redis host.',
        type=str,
        default='localhost'
    )
    parser.add_argument(
        '-port', '--port_number',
        help='Redis port number.',
        type=int,
        default=6379
    )

    parser.add_argument(
        '-qid', '--qmla_id',
        help='ID tag for QMD.',
        type=int,
        default=1
    )
    parser.add_argument(
        '-dir', '--results_directory',
        help='Relative directory to store results in.',
        type=str,
        default='QMLA_default_results/'
    )
    parser.add_argument(
        '-pkl', '--pickle_qmd_class',
        help='Store QMD class in pickled file at end. Large memory requirement, recommend not to.',
        type=int,
        default=0
    )

    parser.add_argument(
        '-rqt', '--rq_timeout',
        help='Time allowed before RQ job crashes.',
        type=int,
        default=-1
    )

    parser.add_argument(
        '-log', '--log_file',
        help='File to log RQ workers.',
        type=str,
        default='default_log_file.log'
    )

    parser.add_argument(
        '-cb', '--cumulative_csv',
        help='CSV to store Bayes factors of all QMDs.',
        type=str,
        default='cumulative.csv'
    )

    parser.add_argument(
        '-exp', '--experimental_data',
        help='Use experimental data if provided',
        type=int,
        default=False
    )

    parser.add_argument(
        '-dst', '--data_max_time',
        help='Maximum useful time in given data.',
        type=int,
        default=2000
    )

    parser.add_argument(
        '-ggr', '--growth_generation_rule',
        help='Rule applied for generation of new models during QMD. \
        Corresponding functions must be built into model_generation',
        type=str,
        default='GrowthRule'
    )

    parser.add_argument(
        '-agr', '--alternative_growth_rules',
        help='Growth rules to form other trees.',
        # type=str,
        action='append',
        default=[],
    )

    parser.add_argument(
        '-qhl_mods', '--models_for_qhl',
        help='Models on which to run QHL.',
        # type=str,
        action='append',
        default=[],
    )

    parser.add_argument(
        '-mqhl', '--qhl_mode_multiple_models',
        help='Run QHL test on multiple (provided) models.',
        type=int,
        default=0
    )

    parser.add_argument(
        '-prior_path', '--prior_pickle_file',
        help='Path to save prior to.',
        type=str,
        default=None
    )
    parser.add_argument(
        '-true_params_path', '--true_params_pickle_file',
        help='Path to save true params to.',
        type=str,
        default=None
    )

    parser.add_argument(
        '-true_expec_path', '--true_expec_path',
        help='Path to save true params to.',
        type=str,
        default="{}/true_model_terms_params.p".format(os.getcwd())
    )
    parser.add_argument(
        '-plot_probes', '--probes_plot_file',
        help='Path where plot probe dict is pickled to.',
        type=str,
        default=None
    )

    parser.add_argument(
        '-latex', '--latex_mapping_file',
        help='Path to save list of terms latex/name maps to.',
        type=str,
        default=None
    )

    parser.add_argument(
        '-resource', '--reallocate_resources',
        help='Bool: whether to reallocate resources scaling  \
        with num qubits/terms to be learned during QHL.',
        type=int,
        default=0
    )

    parser.add_argument(
        '-pnoise', '--probe_noise_level',
        help='Noise level to add to probe for learning',
        type=float,
        default=0.03
    )

    # Process arguments from command line
    arguments = parser.parse_args(args)

    # Use arguments to initialise global variables class.
    qmla_controls = ControlsQMLA(
        arguments,
    )

    args_dict = vars(qmla_controls)

    for a in list(args_dict.keys()):
        qmla_controls.log_print([
            a, ':', args_dict[a]        
        ])

    return qmla_controls
