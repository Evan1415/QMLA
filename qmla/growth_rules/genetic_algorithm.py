import numpy as np
import itertools
import sys
import os
import random
import copy
import scipy
import time
import pandas as pd
import sklearn

import qmla.database_framework

class GeneticAlgorithmQMLA():
    def __init__(
        self,
        num_sites,
        true_model,
        base_terms=['x', 'y', 'z'],
        mutation_probability=0.1,
        log_file=None, 
    ):
        self.num_sites = num_sites
        self.base_terms = base_terms
        self.get_base_chromosome()
#         self.addition_str = 'P'*self.num_sites
        self.true_model = true_model
        self.true_chromosome = self.map_model_to_chromosome(self.true_model)
        self.true_chromosome_string = self.chromosome_string(
            self.true_chromosome
        )
        self.all_zero_chromosome_string = '0'*self.num_terms
        self.addition_str = '+'
        self.mutation_probability = mutation_probability
        self.previously_considered_chromosomes = []
        self.log_file = log_file
        self.chromosomes_at_generation = {}
        self.delta_f_by_generation = {}
        self.genetic_generation = 0
        self.f_score_change_by_generation = {}
        self.most_elite_models_by_generation = {}
        self.best_model_unchanged = False
        self.unchanged_elite_num_generations_cutoff = 5
        


    def get_base_chromosome(self):
        """
        get empty chromosome with binary
        position for each possible term
        within this model type

        Basic: all pairs can be connected operator o on sites i,j:
        e.g. i=4,j=7,N=9: IIIoIIoII
        """

        basic_chromosome = []
        chromosome_description = []
        for i in range(1, 1 + self.num_sites):
            for j in range(i + 1, 1 + self.num_sites):
                for t in self.base_terms:
                    pair = (int(i), int(j), t)
                    pair = tuple(pair)
                    basic_chromosome.append(0)
                    chromosome_description.append(pair)

        self.chromosome_description = chromosome_description
        self.chromosome_description_array = np.array(
            self.chromosome_description)
        self.basic_chromosome = np.array(basic_chromosome)
        self.num_terms = len(self.basic_chromosome)
        # print("Chromosome definition:", self.chromosome_description_array)
#         binary_combinations = list(itertools.product([0,1], repeat=self.num_terms))
#         binary_combinations = [list(b) for b in binary_combinations]
#         self.possible_chromosomes = np.array(binary_combinations)

    def map_chromosome_to_model(
        self,
        chromosome,
    ):
        if isinstance(chromosome, str):
            chromosome = list(chromosome)
            chromosome = np.array([int(i) for i in chromosome])

        nonzero_postions = chromosome.nonzero()
        present_terms = list(
            self.chromosome_description_array[nonzero_postions]
        )
        term_list = []
        for t in present_terms:
            i = t[0]
            j = t[1]
            o = t[2]

            term = 'pauliSet_{i}J{j}_{o}J{o}_d{N}'.format(
                i=i,
                j=j,
                o=o,
                N=self.num_sites
            )
            term_list.append(term)

        model_string = self.addition_str.join(term_list)
        return model_string

    def map_model_to_chromosome(
        self,
        model
    ):
        terms = qmla.database_framework.get_constituent_names_from_name(model)
        chromosome_locations = []
        for term in terms:
            components = term.split('_')
            try:
                components.remove('pauliSet')
            except BaseException:
                print(
                    "[GA - map model to chromosome] \
                    \nCannot remove pauliSet from components:",
                    components,
                    "\nModel:", model
                )
                raise
            core_operators = list(sorted(qmla.database_framework.core_operator_dict.keys()))
            for l in components:
                if l[0] == 'd':
                    dim = int(l.replace('d', ''))
                elif l[0] in core_operators:
                    operators = l.split('J')
                else:
                    sites = l.split('J')
            # get strings when splitting the list elements
            sites = [int(s) for s in sites]
            sites = sorted(sites)

            term_desc = [sites[0], sites[1], operators[0]]
            term_desc = tuple(term_desc)
            term_chromosome_location = self.chromosome_description.index(
                term_desc)
            chromosome_locations.append(term_chromosome_location)
        new_chromosome = copy.copy(self.basic_chromosome)
        new_chromosome[chromosome_locations] = 1
        return new_chromosome

    def chromosome_string(
        self,
        c
    ):
        b = [str(i) for i in c]
        s = ''.join(b)
        if s == '1000000000':
            self.log_print(
                [
                    "Unallowed chromosome string {} for {}".format(b, c)
                ]
            )
        return s

    def chromosome_f_score(
        self, 
        chromosome, 
    ):
        if not isinstance(chromosome, np.ndarray):            
            chromosome = np.array([int(a) for a in list(chromosome)])
        
        return sklearn.metrics.f1_score(
            chromosome, 
            self.true_chromosome
        )

    def log_print(self, to_print_list):
        qmla.logging.print_to_log(
            to_print_list = to_print_list,
            log_file = self.log_file,
            log_identifier = 'GA gen {}'.format(self.genetic_generation)
        )


    def random_initial_models(
        self,
        num_models=5
    ):
        new_models = []
        self.initial_number_models = num_models
        self.chromosomes_at_generation[0] = []

        while len(new_models) < num_models:
            r = random.randint(1, 2**self.num_terms-1)
            r = format(r, '0{}b'.format(self.num_terms))

            if self.chromosome_string(
                    r) not in self.previously_considered_chromosomes:
                r = list(r)
                r = np.array([int(i) for i in r])
                mod = self.map_chromosome_to_model(r)

                self.previously_considered_chromosomes.append(
                    self.chromosome_string(r)
                )
                self.chromosomes_at_generation[0].append(
                    self.chromosome_string(r)
                )

                new_models.append(mod)
        return new_models

    ######################
    # Selection functions
    ######################

    def selection(
        self,
        # chromosome_selection_probabilities,
        **kwargs
    ):
        r"""
        Wrapper for user's selected selection method. 

        Whatever method is called must return
            * prescribed_chromosomes
            * chromosomes_for_crossover - pairs
        """
        # return self.basic_pair_selection(
        #     chromosome_selection_probabilities,
        #     **kwargs
        # )
        return self.select_from_pair_df_remove_selected()

    def select_from_pair_df_remove_selected(
        self,
        **kwargs
    ):
        # normalise so pairs' probabilities sum to 1
        self.chrom_pair_df.probability = self.chrom_pair_df.probability.astype(float)
        self.chrom_pair_df.probability = self.chrom_pair_df.probability / self.chrom_pair_df.probability.sum()
        pair_ids = list(self.chrom_pair_df.index)
        pair_probs = [ self.chrom_pair_df.loc[i].probability for i in pair_ids]
        
        selected_id = np.random.choice(
            a = pair_ids, 
            p = pair_probs
        )
        selected_entry = self.chrom_pair_df.loc[selected_id]
        self.chrom_pair_df = self.chrom_pair_df.drop(selected_id)
        selection = {
            'chromosome_1' : selected_entry['c1'], 
            'chromosome_2' : selected_entry['c2'], 
            'other_data' : { 
                'cut' : int(selected_entry['cut1']),
                'force_mutation' : bool(selected_entry['force_mutation'])
            }
        }
        # self.log_print(
        #     [
        #         "Selection id {}: {}".format(selected_id, selection)
        #     ]
        # )
        return selection


    def basic_pair_selection(
        self,
        chromosome_selection_probabilities,
        **kwargs
    ):
        chromosomes = list(chromosome_selection_probabilities.keys())
        probabilities = [chromosome_selection_probabilities[c] for c in chromosomes]
        selected_chromosomes = np.random.choice(
            chromosomes,
            size=2,
            p=probabilities,
            replace=False
        )

        return selected_chromosomes

    ######################
    # Crossover functions
    ######################

    def crossover(
        self,
        selection, 
        **kwargs
    ):
        """
        This fnc assumes only 2 chromosomes to crossover
        and does so in the most basic method of splitting
        down the middle and swapping
        """
        suggested_chromosomes =  self.one_point_crossover(selection)
        return suggested_chromosomes


    def one_point_crossover(
        self, 
        selection,
        **kwargs
    ):
        c1 = np.array(list(selection['chromosome_1']))
        c2 = np.array(list(selection['chromosome_2']))
        x = selection['other_data']['cut']
        # self.log_print(
        #     [
        #         "[Crossover Input] x={}\n {} / {}".format(x, repr(c1), repr(c2))
        #     ]
        # )
        tmp = c2[:x].copy()
        c2[:x], c1[:x] = c1[:x], tmp
        # self.log_print(
        #     [
        #         "[Crossover Result] (x={})\n {} / {}".format(x,repr(c1), repr(c2))
        #     ]
        # )

        return c1, c2

    ######################
    # Mutation functions
    ######################

    def mutation(
        self,
        chromosomes,
        force_mutation = False, 
    ):
        copy_chromosomes = copy.copy(chromosomes)
        mutated_chromosomes = []
        for c in copy_chromosomes:
            if np.all(c == 0):
                self.log_print(
                    [
                        "Input chomosome {} has no interactions -- forcing mutation".format(
                       c)
                    ]
                )
                mutation_probability = 1.0
            else:
                mutation_probability = self.mutation_probability

            if (
                np.random.rand() < mutation_probability
                or 
                force_mutation
            ):
                idx = np.random.choice(range(len(c)))
                # print("Flipping idx {}".format(idx))
                if c[idx] == 0:
                    c[idx] = 1
                elif c[idx] == 1:
                    c[idx] = 0
            mutated_chromosomes.append(c)
        return mutated_chromosomes

    ######################
    # Elitism functions
    ######################

    def get_elite_models(
        self, 
        **kwargs
    ):
        r"""
        Wrapper for user-defined elite model selection.

        
        """

        return self.elite_ranking_top_two(
            **kwargs
        )

    def elite_ranking_top_two(
        self, 
        model_fitnesses,
        num_elites = 2,
        **kwargs
    ):
        ranked_models = sorted(
            model_fitnesses,
            key=model_fitnesses.get,
            reverse=True
        )
        elite_models = ranked_models[:num_elites]
        self.most_elite_models_by_generation[self.genetic_generation] = elite_models[0]
        num_elites_for_termination = 4

        if self.genetic_generation > self.unchanged_elite_num_generations_cutoff + 2:
            gen = self.genetic_generation
            recent_generations = list(
                range(
                    max(
                        0, 
                        gen - self.unchanged_elite_num_generations_cutoff
                    ), 
                    gen+1
                )
            )
            recent_elite_models = [
                self.most_elite_models_by_generation[g] for g in recent_generations
            ]
            unchanged = np.all( 
                np.array(recent_elite_models) == self.most_elite_models_by_generation[gen]
            )
            if unchanged:
                self.best_model_unchanged = True
                self.log_print(
                    [
                        "Setting best_model_unchanged to {}".format(self.best_model_unchanged)
                    ]
                )
            self.log_print(
                [
                    "Elite model unchanged in last {} generations: {}. \nCurrently: {} with f-score {}".format(
                        self.unchanged_elite_num_generations_cutoff, 
                        self.best_model_unchanged,
                        self.most_elite_models_by_generation[gen],
                        self.chromosome_f_score(
                            self.map_model_to_chromosome(
                                self.most_elite_models_by_generation[gen]
                            )
                        )
                    )
                ]
            )
        self.log_print(
            [
                "1st Elite model:", elite_models[0],
                "\n2nd Elite model", elite_models[1],
            ]
        )
        return elite_models

    ######################
    # Processing given fitness to 
    # selection probabilities
    ######################

    def get_selection_probabilities(
        self, 
        **kwargs
    ):
        r""" 
        Wrapper for user-defined probability processing function.

        Current iteration truncates and includes only top half of models
        """
        return self.truncate_to_top_half(**kwargs)


    def truncate_to_top_half(
        self, 
        model_fitnesses, 
        **kwargs
    ):
        ranked_models = sorted(
            model_fitnesses,
            key=model_fitnesses.get,
            reverse=True
        )
        num_models = len(ranked_models)
        self.log_print(
            [
                "Considering truncation for {} models".format(num_models),
                "ranked models:", ranked_models
            ]
        )
        truncation_cutoff = max( int(num_models*0.75), 4)#  either consider top half, or top 4 if too small
        truncation_cutoff = min( truncation_cutoff, num_models )
        truncated_model_list = ranked_models[:truncation_cutoff]

        truncated_model_fitnesses = {
            mod : model_fitnesses[mod] 
            for mod in truncated_model_list
        }

        sum_fitnesses = np.sum(list(truncated_model_fitnesses.values()))
        self.log_print(
            [
                "Truncated model list:\n", truncated_model_list, 
                "\nTruncated model fitnesses:\n", truncated_model_fitnesses, 
                "\nsum fitnesses:", sum_fitnesses
            ]    
        )
        model_probabilities = {
            self.chromosome_string(self.map_model_to_chromosome(mod)) : (truncated_model_fitnesses[mod] / sum_fitnesses)
            for mod in truncated_model_list
        }
        self.log_print(
            [
                "Chromosome Selection probabilities:\n", model_probabilities
            ]
        )
        return model_probabilities


    def prepare_chromosome_pair_dataframe(
        self, 
        chromosome_probabilities,
        force_mutation=False,
    ):
        self.log_print(
            [
                "Setting up chromosome pair dataframe with initial probabilities", 
                chromosome_probabilities
            ]
        )
        self.chrom_pair_df = pd.DataFrame(
            columns = ['c1', 'c2', 'probability', 'cut1', 'c1_prob', 'c2_prob', 'force_mutation'] 
        )
        chromosome_combinations = list(
            itertools.combinations(list(chromosome_probabilities.keys()), 2)
        )
        for c1,c2 in chromosome_combinations:
            pair_prob = chromosome_probabilities[c1] * chromosome_probabilities[c2] # TODO better way to get pair prob?
            for cut1 in range(1, len(c1)-2):
                this_pair_df = pd.DataFrame(
                    np.array([
                        [
                            c1, c2, 
                            np.round(pair_prob, 2), 
                            cut1, 
                            chromosome_probabilities[c1], chromosome_probabilities[c2],
                            force_mutation
                        ]
                    ]),
                    columns=[
                        'c1', 'c2', 
                        'probability', 
                        'cut1', 'c1_prob', 
                        'c2_prob',
                        'force_mutation'
                    ]
                )
                self.chrom_pair_df = self.chrom_pair_df.append(
                    this_pair_df, 
                    ignore_index=True
                )

    ######################
    # Implement entire genetic algorithm iteration
    ######################

    def genetic_algorithm_step(
        self,
        model_fitnesses,
        **kwargs
    ):

        input_models = list(model_fitnesses.keys())
        num_models_for_next_generation = len(input_models)
        self.log_print(
            [
                "Num models reqd for generation:", num_models_for_next_generation
            ]
        )

        elite_models = self.get_elite_models(
            model_fitnesses = model_fitnesses,
            num_elites = 2
        )
        proposed_chromosomes = [
            self.chromosome_string(
                self.map_model_to_chromosome(
                    mod
                )
            ) 
            for mod in elite_models
        ] # list of chromosome strings to return

        chromosome_selection_probabilities = self.get_selection_probabilities(
            model_fitnesses = model_fitnesses
        )

        self.prepare_chromosome_pair_dataframe(
            chromosome_probabilities=chromosome_selection_probabilities
        )

        self.unique_pair_combinations_considered = []
        num_loops_to_find_new_chromosome = 0
        force_mutation = False
        while len(proposed_chromosomes) < num_models_for_next_generation:
            selection = self.selection()
            suggested_chromosomes = self.crossover(
                selection = selection
            )
            suggested_chromosomes = self.mutation(
                suggested_chromosomes,
                force_mutation=selection['other_data']['force_mutation']
            )
            c0_str = self.chromosome_string( suggested_chromosomes[0] )
            c1_str = self.chromosome_string( suggested_chromosomes[1] )

            if (
                c0_str not in proposed_chromosomes
                and
                c0_str != self.all_zero_chromosome_string 
            ):
                proposed_chromosomes.append(c0_str)
                self.log_print(
                    [   
                        "Adding {}; num proposed chromosome now: {} of {}".format(
                            c0_str,
                            len(proposed_chromosomes),
                            num_models_for_next_generation
                        )
                    ]
                )

            if (
                c1_str not in proposed_chromosomes
                and
                c1_str != self.all_zero_chromosome_string
            ):
                proposed_chromosomes.append(c1_str)
                self.log_print(
                    [
                        "num proposed chromosome now: {} of {}".format(
                            len(proposed_chromosomes),
                            num_models_for_next_generation
                        )
                    ]
                )
            if len(self.chrom_pair_df) == 0 :
                # already tried every available pair 
                self.log_print(
                    [
                        "Redrawing chromosome pair selection dataframe, enforcing mutation"
                    ]
                )
                self.prepare_chromosome_pair_dataframe(
                    chromosome_probabilities=chromosome_selection_probabilities,
                    force_mutation=True
                )
            # else: 
            #     num_loops_to_find_new_chromosome += 1
            #     if num_loops_to_find_new_chromosome > 15:
            #         force_mutation = True
            #         self.log_print(
            #             [
            #                 "Forcing mutation bc num loops to find new chromosome above limit"
            #             ]
            #         )
            #     self.log_print(
            #         [
            #             "{} or {} already present in {}".format(c0_str, c1_str, proposed_chromosomes)
            #         ]
            #     )

        # chop extra chromosomes if generated
        proposed_chromosomes = proposed_chromosomes[:num_models_for_next_generation]
        self.log_print(
            [
                "Proposed chromosome list now has {} elements.".format(
                    len(proposed_chromosomes)
                )
            ]
        )
        self.previously_considered_chromosomes.extend([
            self.chromosome_string(r) for r in proposed_chromosomes
            ]
        )
        self.genetic_generation += 1
        # self.delta_f_by_generation[self.genetic_generation] = delta_f_score
        self.chromosomes_at_generation[self.genetic_generation] = [
            self.chromosome_string(r) for r in proposed_chromosomes
        ]
        new_models = [
            self.map_chromosome_to_model(mod) 
            for mod in proposed_chromosomes
        ]
        self.log_print(
            [
                "Genetic alg num new models:{}".format(len(new_models)),
                "({} unique)".format(len(set(list(new_models))))
            ]
        )
        return new_models



