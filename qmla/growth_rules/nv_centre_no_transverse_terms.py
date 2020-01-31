from qmla.growth_rules import nv_centre_experiment

class ExperimentNVCentreNoTransvereTerms(
        nv_centre_experiment.ExperimentNVCentre
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
        self.max_num_parameter_estimate = 6
        self.max_spawn_depth = 5
        self.max_num_models_by_shape = {
            1: 0,
            2: 12,
            'other': 0
        }
