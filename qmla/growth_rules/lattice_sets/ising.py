import numpy as np
import itertools
import sys
import os

from qmla.growth_rules import connected_lattice, growth_rule
from qmla.growth_rules.lattice_sets import fixed_lattice_set
import qmla.shared_functionality.probe_set_generation
from qmla.shared_functionality import topology_predefined
from qmla import construct_models

class IsingLatticeSet(
    fixed_lattice_set.LatticeSet
):
    def __init__(
        self,
        growth_generation_rule,
        **kwargs
    ):

        self.base_terms = ['z']
        self.transverse_field = 'x'
        super().__init__(
            growth_generation_rule=growth_generation_rule,
            **kwargs
        )


        self.timing_insurance_factor = 4
        self.true_model_terms_params = {
            'pauliLikewise_lz_1J2_2J3_3J4_d4' : 0.78,
            'pauliLikewise_lx_1_2_3_4_d4' : 0.12,
        }
        self.timing_insurance_factor = 0.4
        
