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

sys.path.append("/home/bf16951/QMD")
import qmla

import qmla.construct_models

class GeneticAlgorithmQMLA():
    def __init__(
        self,
        genes,
        num_sites,
        true_model=None,
        base_terms=['x', 'y', 'z'],
        mutation_probability=0.1,
        selection_method = 'roulette', 
        mutation_method = 'element_wise', 
        crossover_method = 'one_point',
        num_protected_elite_models = 2, 
        unchanged_elite_num_generations_cutoff = 4,
        log_file=None, 
    ):
        self.num_sites = num_sites
        self.base_terms = base_terms
        self.genes = list(sorted(genes))
        self.get_base_chromosome()
       
        if true_model is None: 
        
            r = random.randint(1, 2**self.num_terms-1)
            r = format(r, '0{}b'.format(self.num_terms))
            self.true_model = self.map_chromosome_to_model(r)
        else:
            self.true_model = true_model



        self.true_chromosome = self.map_model_to_chromosome(self.true_model)
        self.true_chromosome_string = self.chromosome_string(
            self.true_chromosome
        )
        self.all_zero_chromosome_string = '0'*self.num_terms
        self.addition_str = '+'
        self.mutation_probability = mutation_probability
        self.mutation_count = 0
        self.previously_considered_chromosomes = []
        self.chromosomes_at_generation = {}
        self.delta_f_by_generation = {}
        self.genetic_generation = 0
        self.log_file = log_file
        self.log_print([
            "Genes: {} \n Base chromosome: {}".format(self.genes, self.basic_chromosome)
        ])
        self.f_score_change_by_generation = {}
        self.fitness_at_generation = {}
        self.models_ranked_by_fitness = {}
        self.most_elite_models_by_generation = {}
        self.num_protected_elite_models = num_protected_elite_models
        self.terminate_early_if_top_model_unchanged = True
        self.best_model_unchanged = False
        self.unchanged_elite_num_generations_cutoff = unchanged_elite_num_generations_cutoff
        self.birth_register = pd.DataFrame(
            columns=[
                'child', 'chromosome_child', 
                'parent_a', 'parent_b', 
                'chromosome_parent_a', 'chromosome_parent_b', 
                'generation'
            ]
        )
        self.gene_pool = pd.DataFrame(columns=[
            'model', 'chromosome', 'f_score', 'probability', 'generation'
        ])

        # specifying which functionality to use
        self.selection_method = self.select_from_pair_df_remove_selected
        self.mutation_method = self.element_wise_mutation
        self.crossover_method = self.one_point_crossover
        
        available_selection_methods = {
            'roulette' : self.select_from_pair_df_remove_selected,
        }
        available_mutation_methods = {
            'element_wise' : self.element_wise_mutation
        }
        available_crossover_methods = {
            'one_point' : self.one_point_crossover
        }

        self.selection_method = available_selection_methods[selection_method]
        self.mutation_method = available_mutation_methods[mutation_method]
        self.crossover_method = available_crossover_methods[crossover_method]


        
    def get_base_chromosome(self):
        
        self.num_terms = len(self.genes)
        self.basic_chromosome = np.array([0]  * self.num_terms)        
        self.chromosome_description = self.genes
        self.chromosome_description_array = np.array(self.genes)

    def map_chromosome_to_model(
        self,
        chromosome,
    ):
        if isinstance(chromosome, str):
            chromosome = list(chromosome)
            chromosome = np.array([int(i) for i in chromosome])
        assert \
            len(chromosome) == self.num_terms, \
            "Chromosome must be of length {}".format(self.num_terms)
            
        nonzero_postions = chromosome.nonzero()
        present_terms = list(
            self.chromosome_description_array[nonzero_postions]
        )

        model_string = '+'.join(present_terms)
        return model_string
        
    def map_model_to_chromosome(
        self,
        model
    ):
        terms = qmla.construct_models.get_constituent_names_from_name(model)
        assert \
            np.all([ t in self.chromosome_description for t in terms]), \
            "Cannot map some term(s) to any available gene. Terms: {}".format(terms)
            
        locs = [ self.chromosome_description.index(t) for t in terms]
        new_chromosome = copy.copy(self.basic_chromosome)
        new_chromosome[np.array(locs)] = 1
        return new_chromosome
           
    def model_f_score(
        self, 
        model_name
    ):
        model_as_chromosome = self.map_model_to_chromosome(model_name)
        return self.chromosome_f_score(model_as_chromosome)

    def chromosome_string(
        self,
        c
    ):
        b = [str(i) for i in c]
        s = ''.join(b)
        if s == '1000000000':
            # TODO generaalise
            # 1 followed by num_terms 0's can be generated and is not permitted
            self.log_print([
                "Unallowed chromosome string {} for {}".format(b, c)
            ])
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
        if num_models > 2**self.num_terms:
            self.log_print([
                "Number of models requested > number of possible models ({})".format(
                    2**self.num_terms
                ),
                "Reducing by half until < half available"
            ])

            while num_models > (2**self.num_terms)/2:
                num_models = int(num_models/2)
        new_models = []
        self.initial_number_models = num_models
        self.chromosomes_at_generation[0] = []
        self.previously_considered_chromosomes = []

        while len(new_models) < num_models:
            # generate random number and 
            # format as binary string, i.e. chromosome
            r = random.randint(1, 2**self.num_terms-1)
            r = format(r, '0{}b'.format(self.num_terms)) 

            if (
                self.chromosome_string(r)
                not in self.previously_considered_chromosomes
            ):
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
        **kwargs
    ):
        r"""
        Wrapper for user's selected selection method. 

        Whatever method is called must return
            * prescribed_chromosomes
            * chromosomes_for_crossover - pairs
        """

        return self.selection_method(**kwargs)

    def select_from_pair_df_remove_selected(
        self,
        **kwargs
    ):
        # normalise so pairs' probabilities sum to 1
        self.chrom_pair_df.probability = self.chrom_pair_df.probability.astype(float)
        self.chrom_pair_df.probability = self.chrom_pair_df.probability / self.chrom_pair_df.probability.sum()
        pair_ids = list(self.chrom_pair_df.index)
        pair_probs = [ self.chrom_pair_df.loc[i].probability for i in pair_ids]
        # self.log_print( ["Number available pairs:", len(pair_ids)] )

        # randomly select a pair from list of pairs
        selected_id = np.random.choice(
            a = pair_ids, 
            p = pair_probs
        )
        selected_entry = self.chrom_pair_df.loc[selected_id]
        # Drop so it can't be chosen again
        self.chrom_pair_df = self.chrom_pair_df.drop(selected_id)
        selection = {
            'chromosome_1' : selected_entry['c1'], 
            'chromosome_2' : selected_entry['c2'],
            'other_data' : { 
                'cut' : int(selected_entry['cut1']),
                'force_mutation' : bool(selected_entry['force_mutation'])
            }
        }
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
        # selection, 
        **kwargs
    ):
        """
        This fnc assumes only 2 chromosomes to crossover
        and does so in the most basic method of splitting
        down the middle and swapping
        """
        return self.crossover_method(**kwargs)


    def one_point_crossover(
        self, 
        **kwargs
    ):
        selection = kwargs['selection']
        c1 = np.array(list(selection['chromosome_1']))
        c2 = np.array(list(selection['chromosome_2']))
        x = selection['other_data']['cut']
        tmp = c2[:x].copy()
        c2[:x], c1[:x] = c1[:x], tmp

        return c1, c2

    ######################
    # Mutation functions
    ######################

    def mutation(
        self, 
        **kwargs
    ):
        return self.mutation_method(**kwargs)

    def element_wise_mutation(
        self,
        **kwargs
    ):
        chromosomes = kwargs['chromosomes']
        force_mutation = kwargs['force_mutation']

        copy_chromosomes = copy.copy(chromosomes)
        mutated_chromosomes = []
        for c in copy_chromosomes:
            try:
                if np.all(c == 0):
                    self.log_print([
                        "Input chomosome {} has no interactions -- forcing mutation".format(c)
                    ])
                    mutation_probability = 1.0
                else:
                    mutation_probability = self.mutation_probability
            except:
                self.log_print(["Can't compare all w/ 0 :", c])
                mutation_probability = self.mutation_probability

            if (
                np.random.rand() < mutation_probability
                or 
                force_mutation 
            ):
                num_mutations_to_perform = max(1, force_mutation)
                self.mutation_count += 1
                idx = np.random.choice(range(len(c)))
                # print("Flipping idx {}".format(idx))
                if int(c[idx]) == 0:
                    c[idx] = '1'
                elif int(c[idx]) == 1:
                    c[idx] = '0'
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

        # return []
        return self.elite_ranking_top_n_models(
            **kwargs
        )


    def elite_ranking_top_n_models(
        self, 
        model_fitnesses,
        **kwargs
    ):
        # try:
        #     ranked_models = sorted(
        #         model_fitnesses,
        #         key=model_fitnesses.get,
        #         reverse=True
        #     )
        # except:
        #     self.log_print([
        #         "Could not get ranked models. model fitnesses:", model_fitnesses
        #     ])
        # elite_models = ranked_models[:self.num_protected_elite_models]
        # self.most_elite_models_by_generation[self.genetic_generation] = ranked_models[0]
        
        elite_models = self.models_ranked_by_fitness[self.genetic_generation][:self.num_protected_elite_models]
        self.most_elite_models_by_generation[self.genetic_generation] = self.models_ranked_by_fitness[self.genetic_generation][0]
        # num_protected_elite_models_for_termination = 2

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
                np.array(recent_elite_models) 
                == self.most_elite_models_by_generation[gen]
            )
            if unchanged and self.terminate_early_if_top_model_unchanged:
                self.best_model_unchanged = True
                self.log_print([
                    "Setting best_model_unchanged to {}".format(self.best_model_unchanged)
                ])
            self.log_print([
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
            ])
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
        self.log_print([
            "Considering truncation for {} models".format(num_models),
            "ranked models:", ranked_models
        ])
        truncation_rate = 0.5
        truncation_cutoff = max( int(num_models*truncation_rate), 4) # either consider top half, or top 4 if too small
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
        self.log_print([
                "Chromosome Selection probabilities:\n", model_probabilities
        ])
        return model_probabilities


    def prepare_chromosome_pair_dataframe(
        self, 
        chromosome_probabilities,
        force_mutation=False,
    ):
        self.log_print([
            "Setting up chromosome pair dataframe with initial probabilities", 
            chromosome_probabilities
        ])

        # Register gene pool
        for c in chromosome_probabilities:
            model = self.map_chromosome_to_model(c)
            gene_probability = pd.Series({
                'model' : model, 
                'chromosome' : c, 
                'f_score' : self.model_f_score(model), 
                'probability' : chromosome_probabilities[c],
                'generation' : self.genetic_generation
            })
            self.gene_pool.loc[len(self.gene_pool)] = gene_probability

        # Construct df of pairs of chromosomes from the gene pool, where the probability of that 
        # pair being selected is the product of their individual fitnesses
        self.chrom_pair_df = pd.DataFrame(
            columns = ['c1', 'c2', 'probability', 'cut1', 'c1_prob', 'c2_prob', 'force_mutation'] 
        )
        chromosome_combinations = list(
            itertools.combinations(list(chromosome_probabilities.keys()), 2)
        )
        for c1,c2 in chromosome_combinations:
            pair_prob = chromosome_probabilities[c1] * chromosome_probabilities[c2] # TODO better way to get pair prob?
            for cut1 in range(1, len(c1)-2):
                # every possible cut down these two chromosomes is equally probable of being selected
                # therefore the same pair can be selected twice with different cuts
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
        self.genetic_generation += 1
        self.fitness_at_generation[self.genetic_generation] = model_fitnesses
        self.models_ranked_by_fitness[self.genetic_generation] = sorted(
            model_fitnesses,
            key=model_fitnesses.get,
            reverse=True
        )
        self.log_print([
            "GA step. model ranked by fitness:", self.models_ranked_by_fitness[self.genetic_generation]
        ])
        input_models = list(model_fitnesses.keys())
        num_models_for_next_generation = len(input_models)
        self.log_print([
            "Num models reqd for generation:", num_models_for_next_generation
        ])

        elite_models = self.get_elite_models(
            model_fitnesses = model_fitnesses,
            num_protected_elite_models = 2
        )
        proposed_chromosomes = [
            self.chromosome_string(
                self.map_model_to_chromosome(mod)
            ) for mod in elite_models
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
        num_genes_to_force_mutate = 0
        
        while len(proposed_chromosomes) < num_models_for_next_generation:
            selection = self.selection()
            suggested_chromosomes = self.crossover(
                selection = selection
            )
            suggested_chromosomes = self.mutation(
                chromosomes = suggested_chromosomes,
                force_mutation=selection['other_data']['force_mutation']
            )
            c0_str = self.chromosome_string( suggested_chromosomes[0] )
            c1_str = self.chromosome_string( suggested_chromosomes[1] )

            for c in [c0_str, c1_str]:
                if (c not in proposed_chromosomes and c != self.all_zero_chromosome_string):
                    proposed_chromosomes.append(c)
                    self.log_print([
                        "num proposed chromosome now: {} of {}".format(
                            len(proposed_chromosomes),
                            num_models_for_next_generation
                        ),
                        "Selection:", selection
                    ])
                    birth = pd.Series({
                        'child' : self.map_chromosome_to_model(c), 
                        'chromosome_child' : c, 
                        'chromosome_parent_a' : selection['chromosome_1'], 
                        'chromosome_parent_b' : selection['chromosome_2'], 
                        'parent_a' : self.map_chromosome_to_model( selection['chromosome_1']),
                        'parent_b' : self.map_chromosome_to_model( selection['chromosome_2']),
                        'generation' : self.genetic_generation,
                    })
                    self.birth_register.loc[len(self.birth_register)] = birth

            if len(self.chrom_pair_df) == 0 :
                # already tried every available pair 
                num_genes_to_force_mutate += 1 # TODO increase number of genes to flip to diversify population when repetitive
                self.log_print([
                    "Redrawing chromosome pair selection dataframe, enforcing mutation on {} genes".format(num_genes_to_force_mutate)
                ])
                self.prepare_chromosome_pair_dataframe(
                    chromosome_probabilities=chromosome_selection_probabilities,
                    force_mutation=True
                    # force_mutation=num_genes_to_force_mutate
                )

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


class GeneticAlgorithmFullyConnectedLikewisePauliTerms(GeneticAlgorithmQMLA):
    def __init__(self, num_sites, base_terms=['x', 'y', 'z'], **kwargs):
                
        terms = []
        for i in range(1, 1 + num_sites):
            for j in range(i + 1, 1 + num_sites):
                for t in base_terms:
                    new_term = 'pauliSet_{i}J{j}_{o}J{o}_d{N}'.format(
                        i= i, j=j, o=t, N=num_sites, 
                    )
                    terms.append(new_term)


        super().__init__(
            genes = terms, 
            num_sites = num_sites, 
            **kwargs
        )
        
