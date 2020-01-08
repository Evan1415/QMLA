import numpy as np
import itertools
import sys, os
sys.path.append(os.path.abspath('..'))
import DataBase
import ProbeGeneration
import ModelNames
import ModelGeneration
import SystemTopology
import Heuristics


import SuperClassGrowthRule
import ConnectedLattice


class heisenberg_xyz_probabilistic(
    ConnectedLattice.connected_lattice
):
    
    def __init__(
        self, 
        growth_generation_rule, 
        **kwargs
    ):
        # print("[Growth Rules] init nv_spin_experiment_full_tree")
        super().__init__(
            growth_generation_rule = growth_generation_rule,
            **kwargs
        )

        self.min_param = 0
        self.max_param = 10
        
        self.lattice_dimension = 2
        self.initial_num_sites = 2
        self.lattice_connectivity_max_distance = 1
        self.lattice_connectivity_linear_only = True
        self.lattice_full_connectivity = False

        self.true_operator_partially_connected ='pauliSet_xJx_1J2_d4PPPPpauliSet_yJy_1J2_d4PPPPpauliSet_xJx_2J3_d4PPPPpauliSet_yJy_3J4_d4PPPPpauliSet_zJz_3J4_d4PPPPpauliSet_yJy_1J4_d4'
        # self.true_operator_partially_connected ='pauliSet_xJx_1J2_d4+pauliSet_yJy_1J2_d4+pauliSet_xJx_2J3_d4+pauliSet_yJy_3J4_d4+pauliSet_zJz_3J4_d4+pauliSet_yJy_1J4_d4'
        self.true_operator_fully_connected_square = 'pauliSet_xJx_1J2_d4PPPPpauliSet_yJy_1J2_d4PPPPpauliSet_zJz_1J2_d4PPPPpauliSet_xJx_1J3_d4PPPPpauliSet_yJy_1J3_d4PPPPpauliSet_zJz_1J3_d4PPPPpauliSet_xJx_2J4_d4PPPPpauliSet_yJy_2J4_d4PPPPpauliSet_zJz_2J4_d4PPPPpauliSet_xJx_3J4_d4PPPPpauliSet_yJy_3J4_d4PPPPpauliSet_zJz_3J4_d4'
        
        self.true_operator = self.true_operator_partially_connected
        self.true_operator = DataBase.alph(self.true_operator)
        self.qhl_models = [self.true_operator]
        self.base_terms = [
            'x', 
            'y', 
            'z'
        ]
        # fitness calculation parameters. fitness calculation inherited.
        self.num_top_models_to_build_on = 1 # 'all' # at each generation Badassness parameter
        self.model_generation_strictness = 0 #1 #-1 
        self.fitness_win_ratio_exponent = 3

        self.generation_DAG = 1
        self.max_num_sites = 4
        self.tree_completed_initially = False
        self.num_processes_to_parallelise_over = 10
        self.max_num_models_by_shape = {
            'other' : 2
        }
        self.setup_growth_class()

class heisenberg_xyz_predetermined(
    heisenberg_xyz_probabilistic
):
    
    def __init__(
        self, 
        growth_generation_rule, 
        **kwargs
    ):
        # print("[Growth Rules] init nv_spin_experiment_full_tree")
        super().__init__(
            growth_generation_rule = growth_generation_rule,
            **kwargs
        )
        self.num_processes_to_parallelise_over = 10
        self.max_num_models_by_shape = {
            # Note dN here requires 2N qubits so d3 counts as shape 6
            1 : 0,
            2 : 1,
            4 : 3, 
            5 : 2,
            6 : 2,
            'other' : 0
        }
        self.max_num_sites = 6
        self.setup_growth_class()
        self.max_num_models_by_shape = {
            'other' : 3
        }
        self.min_param = 0
        self.max_param = 1

        if self.tree_completed_initially == True:
            # to manually fix the models to be considered
            models = []
            list_connections = [
                [(1,2)], # pair of sites
                [(1,2), (2,3)],  # chain length 3
                [(1,2), (1,3), (3, 4), (2,4)], # square, 
                [(1,2), (2,3), (3,4)], # chain,
                [(1,2), (2,3), (3,4), (4,5)], # chain,
                [(1,2), (2,3), (3,4), (4,5), (5,6)], # chain,
                [(1,2), (1,4), (2,3), (2,5), (3,6), (4,5), (5,6)] #3x2 grid     
            ]
            for connected_sites in list_connections:
                
                system_size = max(max(connected_sites))
                terms = ConnectedLattice.pauli_like_like_terms_connected_sites(
                    connected_sites = connected_sites, 
                    base_terms = ['x', 'y','z'],
                    num_sites = system_size
                )
                
                p_str = 'P'*system_size
                models.append(p_str.join(terms))
                
            self.initial_models = models

            if self.true_operator not in self.initial_models:
                self.log_print("Adding true operator to initial model list")
                self.initial_models.append(self.true_operator)
