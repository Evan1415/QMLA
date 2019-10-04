import sys
import os

this_dir = str(os.path.dirname(os.path.realpath(__file__)))
# sys.path.append((os.path.join(this_dir, "GrowthRuleClasses")))
sys.path.append(os.path.join(".."))
sys.path.append(os.path.join(this_dir, "..", "GrowthRuleClasses"))

import SuperClassGrowthRule
import NVCentreExperimentGrowthRules
import NVExperimentVaryTrueModel
import NVCentreFullAccess
import NVCentreLargeSpinBath
import NVCentreExperimentWithoutTransverseTerms
import NVCentreRevivals
import NVCentreAlternativeTrueModel
import NVGrowByFitness
import NVProbabilistic
import ReducedNVExperiment
import SpinProbabilistic
import IsingChain
import Hubbard
import Heisenberg
import Hopping
import IsingMultiAxis
import Ising2D 
import PauliPairwiseProbabilisticNearestNeighbour
import ConnectedLattice
import HoppingProbabilistic
import IsingProbabilistic
import HeisenbergXYZProbabilistic
import BasicLindbladian
import ExampleGrowthRule

growth_classes = {
    # 'test_growth_class' : 
    #     SuperClassGrowthRule.default_growth, 
    # 'two_qubit_ising_rotation_hyperfine_transverse' : 
    #     SuperClassGrowthRule.default_growth, 
    'two_qubit_ising_rotation_hyperfine_transverse' : 
        NVCentreExperimentGrowthRules.nv_centre_spin_experimental_method,
    'two_qubit_ising_rotation_hyperfine' : 
        NVCentreExperimentWithoutTransverseTerms.nv_centre_spin_experimental_method_without_transvere_terms,
    'NV_alternative_model' : 
        NVCentreAlternativeTrueModel.nv_centre_spin_experimental_method_alternative_true_model,
    'NV_alternative_model_2' : 
        NVCentreAlternativeTrueModel.nv_centre_spin_experimental_method_alternative_true_model_second,
    'nv_experiment_vary_model' : 
        NVExperimentVaryTrueModel.nv_centre_spin_experimental_method_varying_true_model,
    'nv_experiment_vary_model_3_params' : 
        NVExperimentVaryTrueModel.nv_centre_spin_experimental_method_varying_true_model_3_params,
    'nv_experiment_vary_model_5_params' : 
        NVExperimentVaryTrueModel.nv_centre_spin_experimental_method_varying_true_model_5_params,
    'nv_experiment_vary_model_6_params' : 
        NVExperimentVaryTrueModel.nv_centre_spin_experimental_method_varying_true_model_6_params,
    'nv_experiment_vary_model_7_params' : 
        NVExperimentVaryTrueModel.nv_centre_spin_experimental_method_varying_true_model_7_params,
    'NV_fitness_growth' : 
        NVGrowByFitness.nv_fitness_growth, 
    'NV_centre_revivals' : 
        NVCentreRevivals.nv_centre_revival_data,
    'NV_spin_full_access' : 
        NVCentreFullAccess.nv_centre_spin_full_access,
    'NV_centre_spin_large_bath' : 
        NVCentreLargeSpinBath.nv_centre_large_spin_bath,
    'reduced_nv_experiment' : 
        ReducedNVExperiment.reduced_nv_experiment,
    'probabilistic_spin' :
        SpinProbabilistic.spin_probabilistic,
    'ising_1d_chain' : 
        IsingChain.ising_chain,
    'ising_multi_axis' : 
        IsingMultiAxis.ising_chain_multi_axis, 
    'ising_2d' : 
        Ising2D.ising_2D,
    'ising_predetermined' : 
        IsingProbabilistic.ising_chain_predetermined,
    'hubbard_square_lattice_generalised' : 
        Hubbard.hubbard_square,
    'heisenberg_xyz' : 
        Heisenberg.heisenberg_XYZ, 
    'pairwise_pauli_probabilistic_nearest_neighbour' : 
        PauliPairwiseProbabilisticNearestNeighbour.pauli_pairwise_nearest_neighbour_probabilistic,
    'nearest_neighbour_pauli_2D' : 
        ConnectedLattice.connected_lattice,
    'hopping_topology' : 
        Hopping.hopping,
    'hopping_probabilistic' : 
        HoppingProbabilistic.hopping_probabilistic,
    'hopping_predetermined' : 
        HoppingProbabilistic.hopping_predetermined,
    'ising_probabilistic' : 
        IsingProbabilistic.ising_chain_probabilistic,
    'heisenberg_xyz_probabilistic' :
        HeisenbergXYZProbabilistic.heisenberg_xyz_probabilistic,
    'heisenberg_xyz_predetermined' : 
        HeisenbergXYZProbabilistic.heisenberg_xyz_predetermined,
    'basic_lindbladian' :
        BasicLindbladian.basic_lindbladian,
    'example' : 
        ExampleGrowthRule.example_growth
}


def get_growth_generator_class(
    growth_generation_rule,
    **kwargs
):
    # TODO: note that in most places, this is called with use_experimental_data.
    # in some plotting functions this is not known, but it should not matter unless
    # called to get probes etc. 

    # print("Trying to find growth class for ", growth_generation_rule)
    # print("kwargs:", kwargs)
    try:
        gr = growth_classes[growth_generation_rule](
            growth_generation_rule = growth_generation_rule, 
            **kwargs
        )
    except:
        raise
        # print("{} growth class not found.".format(growth_generation_rule))
        gr = None

    return gr

    