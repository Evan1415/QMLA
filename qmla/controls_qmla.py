import argparse
import os
import sys
import pickle

import qmla.get_growth_rule as get_growth_rule
import qmla.database_framework as database_framework
import qmla.logging

__all__ = [
    'ControlsQMLA',
    'parse_cmd_line_args'
]


"""
This file is callable with *kwargs from a separate QMD program.
It returns an instance of the class ControlsQMLA, which has attributes
for all the user defined parameters, and defaults if not specified by the user.

"""
def log_print(
    to_print_list, 
    log_file
):
    qmla.logging.print_to_log(
        to_print_list = to_print_list, 
        log_file = log_file, 
        log_identifier = 'Setting QMLA controls'
    )

class ControlsQMLA():
    def __init__(
        self,
        arguments,
        **kwargs
    ):
        self.use_experimental_data = bool(arguments.experimental_data)
        self.growth_generation_rule = arguments.growth_generation_rule
        self.log_file = arguments.log_file
        try:
            self.growth_class = get_growth_rule.get_growth_generator_class(
                growth_generation_rule=self.growth_generation_rule,
                use_experimental_data=self.use_experimental_data,
                log_file=self.log_file
            )
        except BaseException:
            raise
            self.growth_class = None

        # get useful stuff out of growth_rule class
        self.dataset = self.growth_class.experimental_dataset
        self.data_max_time = self.growth_class.max_time_to_consider  # arguments.data_max_time
        self.num_probes = self.growth_class.num_probes
        self.num_top_models_to_generate_from = (
            self.growth_class.num_top_models_to_build_on    
        )


        # get core arguments passed to implement_qmla script
        # and generate required parameters from those

        self.alternative_growth_rules = arguments.alternative_growth_rules
        self.unique_growth_rule_instances = {
            gen : get_growth_rule.get_growth_generator_class(
                    growth_generation_rule = gen, 
                    use_experimental_data = self.use_experimental_data, 
                    log_file = self.log_file
                )
            for gen in self.alternative_growth_rules
        }
        self.unique_growth_rule_instances[self.growth_generation_rule] = self.growth_class

        self.qhl_mode_multiple_models = bool(arguments.qhl_mode_multiple_models)
        self.true_params_pickle_file = arguments.true_params_pickle_file

        true_params_info = pickle.load(
            open(self.true_params_pickle_file, 'rb')
        )
        self.true_model = true_params_info['true_op']
        self.true_op_name = database_framework.alph(self.true_model)
        self.true_model_class = database_framework.Operator(
            self.true_op_name
        )
        self.true_model_terms_matrices = self.true_model_class.constituents_operators
        self.true_model_terms_params = true_params_info['params_list']
        
        # derive required info from data from growth rule and arguments
        if self.use_experimental_data == True:
            true_ham = None
            self.true_params_dict = None
            self.true_params_list = []
        else:
            self.true_params_dict = true_params_info['params_dict']
            self.true_params_list = [
                self.true_params_dict[p]
                for p in self.true_model_class.constituents_names
            ]
            # generate true hamiltonian for simulated case
            true_ham = None
            for k in list(self.true_params_dict.keys()):
                param = self.true_params_dict[k]
                mtx = database_framework.compute(k)
                if true_ham is not None:
                    true_ham += param * mtx
                else:
                    true_ham = param * mtx

        self.true_hamiltonian = true_ham
        
        # get parameters from arguments passed to implement_qmla.py
        self.prior_pickle_file = arguments.prior_pickle_file
        self.qhl_test = bool(arguments.qhl_test)
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
        self.qmd_id = arguments.qmd_id
        self.host_name = arguments.host_name
        self.port_number = arguments.port_number
        self.results_directory = arguments.results_directory
        self.rq_timeout = arguments.rq_timeout
        self.cumulative_csv = arguments.cumulative_csv
        self.true_expec_path = arguments.true_expec_path
        self.probes_plot_file = arguments.probes_plot_file
        self.latex_mapping_file = arguments.latex_mapping_file
        self.reallocate_resources = bool(arguments.reallocate_resources)
        self.probe_noise_level = arguments.probe_noise_level # TODO put in growth rule

        # create some new parameters
        if self.results_directory[-1] != '/':
            self.results_directory += '/'

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

        self.long_id = '{0:03d}'.format(self.qmd_id)
        path_to_store_configurations = self.results_directory + "growth_rule_configs_{}.p".format(self.long_id)
        self.all_growth_rule_configs = {
            gr : self.unique_growth_rule_instances[gr].store_growth_rule_configuration()
            for gr in self.unique_growth_rule_instances
        }
        pickle.dump(
            self.all_growth_rule_configs,
            open(path_to_store_configurations, 'wb')
        )


        if self.further_qhl == True:
            self.results_file = self.results_directory + 'further_qhl_results_' + \
                str(self.long_id) + '.p'  # for pickling results into
            self.class_pickle_file = self.results_directory + \
                'further_qhl_qmd_class_' + str(self.long_id) + '.p'
        else:
            self.results_file = self.results_directory + 'results_' + \
                str(self.long_id) + '.p'  # for pickling results into
            self.class_pickle_file = self.results_directory + \
                'qmd_class_' + str(self.long_id) + '.p'


def parse_cmd_line_args(args):

    parser = argparse.ArgumentParser(description='Pass variables for (I)QLE.')

    # Interpret command line arguments
    # These are passed through the launch script
    # and into this function as args, 
    # parsed here and then available to QMLA instances
    # which have access to the controls class returned from  this function. 

    parser.add_argument(
        '-qhl', '--qhl_test',
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
        '-qid', '--qmd_id',
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
        default=3600
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
        default='two_qubit_ising_rotation_hyperfine'
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
        default='true_'
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
        default="{}/plot_probes.p".format(os.getcwd())
    )

    parser.add_argument(
        '-latex', '--latex_mapping_file',
        help='Path to save list of terms latex/name maps to.',
        type=str,
        default='QMLA_default_results/latex_map.txt'
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

    # args_dict = vars(arguments)
    args_dict = vars(qmla_controls)

    for a in list(args_dict.keys()):
        log_print(
            [
                a,
                ':',
                args_dict[a]
            ],
            log_file=qmla_controls.log_file
        )

    return qmla_controls
