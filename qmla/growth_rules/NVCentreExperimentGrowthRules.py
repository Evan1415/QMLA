import random
import sys
import os

from qmla.growth_rules import NVCentreFullAccess
from  qmla import probe_set_generation
from qmla import expectation_values
from qmla import database_framework


__all__ = [
    'nv_centre_spin_experimental_method'
]

class nv_centre_spin_experimental_method(
    NVCentreFullAccess.nv_centre_spin_full_access  # inherit from this
    # growth_rule_super_class # inherit from this
):
    # Uses all the same functionality, growth etc as
    # default NV centre spin experiments/simulations
    # but uses an expectation value which traces out

    def __init__(
        self,
        growth_generation_rule,
        **kwargs
    ):
        from qmla import experiment_design_heuristics
        # print("[Growth Rules] init nv_spin_experiment_full_tree")
        super().__init__(
            growth_generation_rule=growth_generation_rule,
            **kwargs
        )
        if self.use_experimental_data == True:
            self.expectation_value_function = expectation_values.hahn_evolution
        else:
            self.expectation_value_function = expectation_values.n_qubit_hahn_evolution

        # self.true_operator = 'xTiPPyTy'
        self.heuristic_function = experiment_design_heuristics.MixedMultiParticleLinspaceHeuristic
        self.measurement_type = 'hahn'

        self.true_operator = 'xTiPPyTiPPzTiPPzTz'
        # self.true_operator = 'xTiPPxTxPPyTiPPyTyPPzTiPPzTz'

        self.initial_models = ['xTi', 'yTi', 'zTi']
        # self.initial_models = [
        #     'xTiPPyTiPPzTiPPzTz',
        #     'xTiPPyTiPPyTyPPzTiPPzTz',
        # ]
        self.tree_completed_initially = False
        self.qhl_models = [
            # 'xTiPPxTxPPxTyPPxTzPPyTiPPyTyPPyTzPPzTiPPzTz',
            # 'xTiPPxTxPPyTiPPyTyPPzTiPPzTz',
            'xTiPPyTiPPzTiPPzTz',
            'xTiPPyTiPPyTyPPzTiPPzTz',
            # 'yTi'
        ]
        self.max_num_parameter_estimate = 9
        self.max_spawn_depth = 8
        self.max_num_qubits = 3
        self.experimental_dataset = 'NVB_rescale_dataset.p'
        self.fixed_axis_generator = False
        self.fixed_axis = 'z'  # e.g. transverse axis

        # self.probe_generation_function = probe_set_generation.NV_centre_ising_probes_plus
        # self.probe_generation_function = probe_set_generation.NV_centre_ising_probes_plus
        self.probe_generation_function = probe_set_generation.plus_plus_with_phase_difference
        self.simulator_probe_generation_function = self.probe_generation_function
        self.shared_probes = False
        self.max_time_to_consider = 5

        # self.probe_generation_function = probe_set_generation.separable_probe_dict

        # params for testing p value calculation
        self.max_num_probe_qubits = 2
        self.gaussian_prior_means_and_widths = {
        }

        # self.true_params = {
        #     'xTi' : 0.602,
        #     'yTy' : 0.799

        # }
        if self.true_operator == 'xTiPPyTiPPzTiPPzTz':
            self.true_params = {  # from Jul_05/16_40
                'xTi': 0.92450565,
                'yTi': 6.00664336,
                'zTi': 1.65998543,
                'zTz': 0.76546868,
            }
        if self.use_experimental_data == True:
            # probes, prior etc specific to using experimental data
            # print(
            #     "[{}] Experimental data = true".format(
            #     os.path.basename(__file__))
            # )
            # self.probe_generation_function = probe_set_generation.restore_dec_13_probe_generation
            # self.probe_generation_function = probe_set_generation.NV_centre_ising_probes_plus

            # self.probe_generation_function = probe_set_generation.plus_probes_dict
            self.gaussian_prior_means_and_widths = {
                'xTi': [4.0, 1.5],
                'yTi': [4.0, 1.5],
                'zTi': [4.0, 1.5],
                'xTx': [4.0, 1.5],
                'yTy': [4.0, 1.5],
                'zTz': [4.0, 1.5],
                'xTy': [4.0, 1.5],
                'xTz': [4.0, 1.5],
                'yTz': [4.0, 1.5],
            }

        self.max_num_models_by_shape = {
            1: 0,
            2: 18,
            'other': 1
        }
