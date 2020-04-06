import numpy as np
import itertools
import sys
import os
from qmla.growth_rules import connected_lattice
import qmla.shared_functionality.probe_set_generation
from qmla import database_framework



class IsingProbabilistic(
    connected_lattice.ConnectedLattice
):

    def __init__(
        self,
        growth_generation_rule,
        **kwargs
    ):
        super().__init__(
            growth_generation_rule=growth_generation_rule,
            **kwargs
        )

        self.lattice_dimension = 1
        self.initial_num_sites = 2
        self.lattice_connectivity_max_distance = 1
        self.lattice_connectivity_linear_only = True
        self.lattice_full_connectivity = False
        self.max_num_probe_qubits = 10

        # self.true_model = 'pauliSet_zJz_1J2_d3PPPpauliSet_xJx_1J3_d3PPPpauliSet_zJz_2J3_d3PPPpauliSet_yJy_1J2_d3'
        self.true_model = 'pauliSet_zJz_1J2_d4PPPPpauliSet_zJz_2J3_d4PPPPpauliSet_zJz_3J4_d4'
        self.true_model = database_framework.alph(self.true_model)
        self.qhl_models = [self.true_model, 'pauliSet_zJz_1J2_d4']
        self.base_terms = [
            # 'x',
            # 'y',
            'z'
        ]
        # self.model_heuristic_function = qmla.shared_functionality.experiment_design_heuristics.MixedMultiParticleLinspaceHeuristic
        self.max_time_to_consider = 50
        # fitness calculation parameters. fitness calculation inherited.
        # 'all' # at each generation Badassness parameter
        self.num_top_models_to_build_on = 'all'
        self.model_generation_strictness = -1 #0  # 1 #-1
        self.fitness_win_ratio_exponent = 1
        # self.max_time_to_consider = 20

        self.generation_DAG = 1
        self.tree_completed_initially = False
        self.num_processes_to_parallelise_over = 10
        
        self.true_model_terms_params = {
            'pauliSet_zJz_1J2_d4': 0.61427723297770065, 
            'pauliSet_zJz_2J3_d4': 0.12996320356092372, 
            'pauliSet_zJz_3J4_d4': 0.18011186731750234
        }
        self.max_num_models_by_shape = {
            'other': 3
        }
        self.max_num_sites = 5
        
        self.gaussian_prior_means_and_widths = {
            # 'pauliSet_zJz_1J2_d3' : (2, 0.01),
            # 'pauliSet_zJz_2J3_d3' : (8, 0.1)
            'pauliSet_zJz_4J5_d5' : (0, 0.01)
        }

        self.tree_completed_initially = False
        self.setup_growth_class()  # from ConnectedLattice, using updated params


class IsingPredetermined(
    IsingProbabilistic
):
    def __init__(
        self,
        growth_generation_rule,
        **kwargs
    ):
        super().__init__(
            growth_generation_rule=growth_generation_rule,
            **kwargs
        )
        # keep these fixed to enforce 1d Ising chain up to 7 sites
        self.num_probes = 100
        self.lattice_dimension = 1
        self.initial_num_sites = 2
        self.lattice_connectivity_max_distance = 1
        self.max_num_sites = 8 
        self.lattice_connectivity_linear_only = True
        self.lattice_full_connectivity = False
        # test heuristic -- force all times to be considered
        # self.model_heuristic_function = qmla.shared_functionality.experiment_design_heuristics.MixedMultiParticleLinspaceHeuristic 
        # self.true_model = 'pauliSet_zJz_1J2_d2'
        # self.true_model = 'pauliSet_zJz_1J2_d4PPPPpauliSet_zJz_2J3_d4PPPPpauliSet_zJz_3J4_d4'
        # self.true_model = 'pauliSet_zJz_1J2_d6PPPPPPpauliSet_zJz_2J3_d6PPPPPPpauliSet_zJz_3J4_d6PPPPPPpauliSet_zJz_4J5_d6PPPPPPpauliSet_zJz_5J6_d6'
        # self.true_model = 'pauliSet_zJz_1J2_d3PPPpauliSet_zJz_2J3_d3'
        self.true_model = database_framework.alph(self.true_model)
        self.qhl_models = [
            self.true_model,
            'pauliSet_zJz_1J2_d2'
        ]
        self.base_terms = [
            'z'
        ]


        self.setup_growth_class()
        self.tree_completed_initially = True
        if self.tree_completed_initially == True:
            # to manually fix the models to be considered
            self.num_processes_to_parallelise_over = 5
            self.initial_models = [
                # 'pauliSet_zJz_1J2_d6PPPPPPpauliSet_zJz_2J3_d6PPPPPPpauliSet_zJz_3J4_d6PPPPPPpauliSet_zJz_4J5_d6PPPPPPpauliSet_zJz_5J6_d6',
                'pauliSet_zJz_1J2_d5PPPPPpauliSet_zJz_2J3_d5PPPPPpauliSet_zJz_3J4_d5PPPPPpauliSet_zJz_4J5_d5',
                'pauliSet_zJz_1J2_d4PPPPpauliSet_zJz_2J3_d4PPPPpauliSet_zJz_3J4_d4',
                # 'pauliSet_zJz_1J2_d3PPPpauliSet_zJz_2J3_d3',
                # 'pauliSet_zJz_1J2_d2',
                # 'pauliSet_zJz_1J2_d7PPPPPPPpauliSet_zJz_2J3_d7PPPPPPPpauliSet_zJz_3J4_d7PPPPPPPpauliSet_zJz_4J5_d7PPPPPPPpauliSet_zJz_5J6_d7PPPPPPPpauliSet_zJz_6J7_d7',
            ]
            self.qhl_models = self.initial_models

            if self.true_model not in self.initial_models:
                self.initial_models.append(self.true_model)

            self.max_num_models_by_shape = {
                4 : 1, 
                5 : 1,
                'other': 0
            }
            self.num_processes_to_parallelise_over = 2


class TestReducedParticlesBayesFactors(
    IsingPredetermined
):
    def __init__(
        self,
        growth_generation_rule,
        **kwargs
    ):
        super().__init__(
            growth_generation_rule=growth_generation_rule,
            **kwargs
        )
        self.max_num_qubits = 5
        self.max_num_sites = 6
        self.fraction_particles_for_bf = 1e-4 # to ensure only ~5 particles used
        self.num_processes_to_parallelise_over = 2
        self.initial_models = [
            'pauliSet_zJz_1J2_d5PPPPPpauliSet_zJz_2J3_d5PPPPPpauliSet_zJz_3J4_d5PPPPPpauliSet_zJz_4J5_d5',
            'pauliSet_zJz_1J2_d5PPPPPpauliSet_zJz_4J5_d5',
        ]
        self.true_model = database_framework.alph(
            self.initial_models[0]
        )
        self.max_num_models_by_shape = {
            5 : 2,
            'other': 0
        }

class TestAllParticlesBayesFactors(
    TestReducedParticlesBayesFactors
):
    def __init__(
        self,
        growth_generation_rule,
        **kwargs
    ):
        super().__init__(
            growth_generation_rule=growth_generation_rule,
            **kwargs
        )
        self.fraction_particles_for_bf = 1.0
        self.num_processes_to_parallelise_over = 2
