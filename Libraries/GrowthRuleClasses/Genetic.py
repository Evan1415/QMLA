import numpy as np
import itertools
import sys, os
import random
sys.path.append(os.path.abspath('..'))
import DataBase
import ProbeGeneration
import ModelNames
import ModelGeneration
import SystemTopology
import Heuristics
import GeneticAlgorithm

import SuperClassGrowthRule

flatten = lambda l: [item for sublist in l for item in sublist]  # flatten list of lists


class genetic_algorithm(
    SuperClassGrowthRule.growth_rule_super_class    
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

        self.num_sites = 4
        self.base_terms = [
            'x', 'y', 'z'
        ]
        self.mutation_probability = 0.1

        self.genetic_algorithm = GeneticAlgorithm.GeneticAlgorithmQMLA(
            num_sites = self.num_sites, 
            base_terms = self.base_terms, 
            mutation_probability = self.mutation_probability
        )

        self.true_operator = 'pauliSet_xJx_1J2_d4+pauliSet_yJy_1J2_d4+pauliSet_yJy_2J3_d4+pauliSet_zJz_1J3_d4+pauliSet_yJy_1J4_d4'
        # self.true_operator = 'pauliSet_xJx_1J2_d3+pauliSet_yJy_1J2_d3'
        self.max_num_probe_qubits = self.num_sites
        self.initial_num_models = 10
        self.initial_models = self.genetic_algorithm.random_initial_models(
            num_models = self.initial_num_models
        )
        self.max_spawn_depth = 4
        self.tree_completed_initially = False
        self.max_num_models_by_shape = {
            4 : self.initial_num_models * self.max_spawn_depth, 
            'other' : 0
        }


    def generate_models(
        self, 
        model_list, 
        **kwargs
    ):
        # print("[Genetic] Calling generate_models")
        model_points = kwargs['branch_model_points']
        # print("Model points:", model_points)
        # print("kwargs: ", kwargs)
        model_fitnesses = {}
        for m in list(model_points.keys()):
            mod = kwargs['model_names_ids'][m]
            model_fitnesses[mod] = model_points[m]

        # print("Model fitnesses:", model_fitnesses)
        new_models = self.genetic_algorithm.genetic_algorithm_step(
            model_fitnesses = model_fitnesses,
            num_pairs_to_sample = self.initial_num_models
        )

        return new_models

    def latex_name(
        self, 
        name, 
        **kwargs
    ):
        # print("[latex name fnc] name:", name)
        core_operators = list(sorted(DataBase.core_operator_dict.keys()))
        num_sites = DataBase.get_num_qubits(name)
        p_str = 'P'*num_sites
        p_str = '+'
        separate_terms = name.split(p_str)

        site_connections = {}
        for c in list(itertools.combinations(list(range(num_sites+1)), 2)):
            site_connections[c] = []

        term_type_markers = ['pauliSet', 'transverse']
        transverse_axis = None
        for term in separate_terms:
            components = term.split('_')
            if 'pauliSet' in components:
                components.remove('pauliSet')

                for l in components:
                    if l[0] == 'd':
                        dim = int(l.replace('d', ''))
                    elif l[0] in core_operators:
                        operators = l.split('J')
                    else:
                        sites = l.split('J')
                sites = tuple([int(a) for a in sites])
                op = operators[0] # assumes like-like pauli terms like xx, yy, zz
                site_connections[sites].append(op)
            elif 'transverse' in components:
                components.remove('transverse')
                for l in components:
                    if l[0] == 'd':
                        transverse_dim = int(l.replace('d', ''))
                    elif l in core_operators:
                        transverse_axis = l


        ordered_connections = list(sorted(site_connections.keys()))
        latex_term = ""

        for c in ordered_connections:
            if len(site_connections[c]) > 0:
                this_term = "\sigma_{"
                this_term += str(c)
                this_term += "}"
                this_term += "^{"
                for t in site_connections[c]:
                    this_term += "{}".format(t)
                this_term += "}"
                latex_term += this_term
        if transverse_axis is not None:
            latex_term += 'T^{}_{}'.format(transverse_axis, transverse_dim)
        latex_term = "${}$".format(latex_term)
        return latex_term




