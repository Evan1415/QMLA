import qinfer as qi
import numpy as np
import scipy as sp
import random 
import math

from inspect import currentframe, getframeinfo
import qmla.logging


frameinfo = getframeinfo(currentframe())

__all__ = [
    'MultiParticleGuessHeuristic',
    'TimeHeurstic',
    'TimeFromListHeuristic',
    'MixedMultiParticleLinspaceHeuristic',
    'InverseEigenvalueHeuristic'
]

def identity(arg): return arg

def log_print(
    to_print_list, 
    log_file, 
):
    qmla.logging.print_to_log(
        to_print_list = to_print_list, 
        log_file = log_file, 
        log_identifier = 'Heuristic'
    )

class MultiParticleGuessHeuristic(qi.Heuristic):
    def __init__(
        self,
        updater,
        oplist=None,
        norm='Frobenius',
        inv_field='x_',
        t_field='t',
        inv_func=identity,
        t_func=identity,
        pgh_exponent=1,
        increase_time=False,
        maxiters=10,
        other_fields=None,
        **kwargs
    ):
        super(MultiParticleGuessHeuristic, self).__init__(updater)
        self._oplist = oplist
        self._norm = norm
        self._x_ = inv_field
        self._t = t_field
        self._inv_func = inv_func
        self._t_func = t_func
        self._maxiters = maxiters
        self._other_fields = other_fields if other_fields is not None else {}
        self._pgh_exponent = pgh_exponent
        self._increase_time = increase_time

    def __call__(
        self,
        epoch_id=0,
        **kwargs
    ):

        idx_iter = 0
        while idx_iter < self._maxiters:

            x, xp = self._updater.sample(n=2)[:, np.newaxis, :]
            if self._updater.model.distance(x, xp) > 0:
                break
            else:
                idx_iter += 1

        if self._updater.model.distance(x, xp) == 0:
            raise RuntimeError(
                "PGH did not find distinct particles in \
                {} iterations.".format(self._maxiters)
            )

        eps = np.empty(
            (1,),
            dtype=self._updater.model.expparams_dtype
        )

        idx_iter = 0  # modified in order to cycle through particle parameters with different names
        for field_i in self._x_:
            eps[field_i] = self._inv_func(x)[0][idx_iter]
            idx_iter += 1

        sigma = self._updater.model.distance(x, xp)
        new_time = self._t_func(
            1 / sigma**self._pgh_exponent
        )
        eps[self._t] = new_time
        for field, value in self._other_fields.items():
            eps[field] = value**self._pgh_exponent

        return eps


class TimeHeurstic(qi.Heuristic):

    def identity(arg): return arg

    def __init__(self, updater, t_field='t',
                 t_func=identity,
                 maxiters=10
                 ):
        super(TimeHeurstic, self).__init__(updater)
        self._t = t_field
        self._t_func = t_func
        self._maxiters = maxiters

    def __call__(self, **kwargs):
        idx_iter = 0
        while idx_iter < self._maxiters:

            x, xp = self._updater.sample(n=2)[:, np.newaxis, :]
            if self._updater.model.distance(x, xp) > 0:
                break
            else:
                idx_iter += 1

        if self._updater.model.distance(x, xp) == 0:
            raise RuntimeError("PGH did not find distinct particles in {} \
                iterations.".format(self._maxiters)
                               )

        eps = np.empty((1,), dtype=self._updater.model.expparams_dtype)
        eps[self._t] = self._t_func(1 / self._updater.model.distance(x, xp))

        return eps


class TimeFromListHeuristic(qi.Heuristic):

    def __init__(
        self,
        updater,
        oplist=None,
        pgh_exponent=1,
        increase_time=False,
        norm='Frobenius',
        inv_field='x_',
        t_field='t',
        inv_func=identity,
        t_func=identity,
        maxiters=10,
        other_fields=None,
        time_list=None,
        **kwargs
    ):
        super(TimeFromListHeuristic, self).__init__(updater)
        self._oplist = oplist
        self._norm = norm
        self._x_ = inv_field
        self._t = t_field
        self._inv_func = inv_func
        self._t_func = t_func
        self._maxiters = maxiters
        self._other_fields = other_fields if other_fields is not None else {}
        self._pgh_exponent = pgh_exponent
        self._increase_time = increase_time
        # self._time_list = kwargs['time_list']
        self._time_list = time_list
        self._len_time_list = len(self._time_list)

        try:
            self._num_experiments = kwargs.get('num_experiments')
            print("self.num_experiments:", self._num_experiments)
        except BaseException:
            print("Can't find num_experiments in kwargs")

    def __call__(
        self,
        epoch_id=0,
        **kwargs
    ):

        idx_iter = 0
        while idx_iter < self._maxiters:

            x, xp = self._updater.sample(n=2)[:, np.newaxis, :]
            if self._updater.model.distance(x, xp) > 0:
                break
            else:
                idx_iter += 1

        if self._updater.model.distance(x, xp) == 0:
            raise RuntimeError(
                "PGH did not find distinct particles in \
                {} iterations.".format(self._maxiters)
            )
        eps = np.empty(
            (1,),
            dtype=self._updater.model.expparams_dtype
        )
        idx_iter = 0  # modified in order to cycle through particle parameters with different names
        for field_i in self._x_:
            eps[field_i] = self._inv_func(x)[0][idx_iter]
            idx_iter += 1

        time_id = epoch_id % self._len_time_list
        new_time = self._time_list[time_id]
        eps[self._t] = new_time

        return eps


class MixedMultiParticleLinspaceHeuristic(qi.Heuristic):

    def __init__(
        self,
        updater,
        oplist=None,
        pgh_exponent=1,
        increase_time=False,
        norm='Frobenius',
        inv_field='x_',
        t_field='t',
        inv_func=identity,
        t_func=identity,
        maxiters=10,
        other_fields=None,
        time_list=None,
        max_time_to_enforce=10,
        num_experiments=100,
        log_file='qmla_log.log',
        **kwargs
    ):
        super().__init__(updater)
        self._oplist = oplist
        self._norm = norm
        self._x_ = inv_field
        self._t = t_field
        self._inv_func = inv_func
        self._t_func = t_func
        self._maxiters = maxiters
        self._other_fields = other_fields if other_fields is not None else {}
        self._pgh_exponent = pgh_exponent
        self._increase_time = increase_time
        # self._num_experiments = kwargs.get('num_experiments', 200)
        self.log_file = log_file
        self._num_experiments = num_experiments
        self._time_list = time_list
        self._len_time_list = len(self._time_list)
        self._max_time_to_enforce = max_time_to_enforce
        self.count_number_high_times_suggested = 0 
        self.num_epochs_for_first_phase = self._num_experiments / 2
        # generate a list of times of length Ne/2
        # evenly spaced between 0, max_time (from growth_rule)
        # then every t in that list is learned upon once. 
        # Higher Ne means finer granularity 
        # times are leared in a random order (from random.shuffle below)
        num_epochs_to_space_time_list = math.ceil(
            self._num_experiments - self.num_epochs_for_first_phase
        )
        t_list = list(np.linspace(
            0, 
            max_time_to_enforce,
            num_epochs_to_space_time_list + 1
        ))
        t_list.remove(0)  # dont want to waste an epoch on t=0
        t_list = [np.round(t, 2) for t in t_list]
        random.shuffle(t_list)
        self._time_list = iter( t_list )
        

    def __call__(
        self,
        epoch_id=0,
        **kwargs
    ):

        idx_iter = 0
        while idx_iter < self._maxiters:

            x, xp = self._updater.sample(n=2)[:, np.newaxis, :]
            if self._updater.model.distance(x, xp) > 0:
                break
            else:
                idx_iter += 1

        if self._updater.model.distance(x, xp) == 0:
            raise RuntimeError(
                "PGH did not find distinct particles in \
                {} iterations.".format(self._maxiters)
            )

        eps = np.empty(
            (1,),
            dtype=self._updater.model.expparams_dtype
        )
        idx_iter = 0  # modified in order to cycle through particle parameters with different names
        for field_i in self._x_:
            eps[field_i] = self._inv_func(x)[0][idx_iter]
            idx_iter += 1

        if epoch_id < self.num_epochs_for_first_phase:
            sigma = self._updater.model.distance(x, xp)
            new_time = self._t_func(
                1 / sigma**self._pgh_exponent
            )
        else:
            # time_id = epoch_id % self._len_time_list
            # new_time = self._time_list[time_id]
            new_time = next(self._time_list)
        
        if new_time > self._max_time_to_enforce:
            self.count_number_high_times_suggested += 1
        
        if epoch_id == self._num_experiments - 1 : 
            log_print(
                [
                    "Number of suggested t > t_max:", self.count_number_high_times_suggested 
                ],
                log_file = self.log_file
            )
        
        eps[self._t] = new_time
        return eps


class InverseEigenvalueHeuristic(qi.Heuristic):

    def __init__(
        self,
        updater,
        oplist=None,
        pgh_exponent=1,
        increase_time=False,
        norm='Frobenius',
        inv_field='x_',
        t_field='t',
        inv_func=identity,
        t_func=identity,
        maxiters=10,
        other_fields=None,
        time_list=None,
        **kwargs
    ):
        super(InverseEigenvalueHeuristic, self).__init__(updater)
        self._oplist = oplist
        self._norm = norm
        self._x_ = inv_field
        self._t = t_field
        self._inv_func = inv_func
        self._t_func = t_func
        self._maxiters = maxiters
        self._other_fields = other_fields if other_fields is not None else {}
        self._pgh_exponent = pgh_exponent
        self._increase_time = increase_time
        self._num_experiments = kwargs.get('num_experiments', 200)
        self._time_list = time_list
        self._len_time_list = len(self._time_list)
        self.num_epochs_for_first_phase = self._num_experiments / 2

    def __call__(
        self,
        epoch_id=0,
        **kwargs
    ):
        print(
            "[Heuristic - InverseEigenvalueHeuristic]",
            "kwargs:", kwargs
        )
        current_params = kwargs['current_params']
        idx_iter = 0
        while idx_iter < self._maxiters:

            x, xp = self._updater.sample(n=2)[:, np.newaxis, :]
            if self._updater.model.distance(x, xp) > 0:
                break
            else:
                idx_iter += 1

        if self._updater.model.distance(x, xp) == 0:
            raise RuntimeError(
                "PGH did not find distinct particles in \
                {} iterations.".format(self._maxiters)
            )
        eps = np.empty(
            (1,),
            dtype=self._updater.model.expparams_dtype
        )
        idx_iter = 0  # modified in order to cycle through particle parameters with different names
        for field_i in self._x_:
            eps[field_i] = self._inv_func(x)[0][idx_iter]
            idx_iter += 1

        if epoch_id < self.num_epochs_for_first_phase:
            sigma = self._updater.model.distance(x, xp)
            new_time = self._t_func(
                1 / sigma**self._pgh_exponent
            )
        else:
            new_time = new_time_based_on_eigvals(
                params=current_params,
                raw_ops=self._oplist
            )

        eps[self._t] = new_time
        return eps


def new_time_based_on_eigvals(
    params,
    raw_ops,
    time_scale=1
):
    param_ops = [
        (params[i] * raw_ops[i]) for i in range(len(params))
    ]
    max_eigvals = []
    for i in range(len(params)):
        param_eigvals = sp.linalg.eigh(param_ops[i])[0]

        max_eigval_this_op = max(np.abs(param_eigvals))
        max_eigvals.append(max_eigval_this_op)
    min_eigval = min(max_eigvals)
    new_time = time_scale * 1 / min_eigval
    return new_time


class BaseHeuristicQMLA(qi.Heuristic):
    def __init__(
        self,
        updater,
        oplist=None,
        norm='Frobenius',
        inv_field='x_',
        t_field='t',
        maxiters=10,
        other_fields=None,
        inv_func=identity,
        t_func=identity,        
        **kwargs
    ):
        super().__init__(updater)
        self._norm = norm
        self._x_ = inv_field
        self._t = t_field
        self._inv_func = inv_func
        self._t_func = t_func
        self._other_fields = other_fields if other_fields is not None else {}
        self._updater = updater
        self._maxiters = maxiters
        self._oplist = oplist
        
    def _get_exp_params_array(self):
        r"""Return an empty array with a position for every experiment design parameter."""
        experiment_params = np.empty(
            (1,),
            dtype=self._updater.model.expparams_dtype
        )
        return experiment_params

    def __call__(self):
        print("__call__ not written")


class SampleOrderMagnitude(BaseHeuristicQMLA):
    
    def __init__(
        self,
        updater,
        **kwargs
    ):
        super().__init__(updater, **kwargs)
        self.count_order_of_magnitudes =  {}
   
    
    def __call__(
        self,
        epoch_id=0,
        **kwargs
    ):
        experiment = self._get_exp_params_array() # empty experiment array
        
        # sample from updater
        idx_iter = 0
        while idx_iter < self._maxiters:

            x, xp = self._updater.sample(n=2)[:, np.newaxis, :]
            if self._updater.model.distance(x, xp) > 0:
                break
            else:
                idx_iter += 1

        cov_mtx = self._updater.est_covariance_mtx()
        orders_of_magnitude = np.log10(
            np.sqrt(np.abs(np.diag(cov_mtx)))
        ) # of the uncertainty on the individual parameters

        probs_of_orders = [
            i/sum(orders_of_magnitude) for i in orders_of_magnitude
        ] # weight of each order of magnitude
        # sample from the present orders of magnitude
        selected_order = np.random.choice(
            a = orders_of_magnitude, 
            p = probs_of_orders
        )
        try:
            self.count_order_of_magnitudes[ np.round(selected_order)] += 1
        except:
            self.count_order_of_magnitudes[ np.round(selected_order)] = 1

        idx_params_of_similar_uncertainty = np.where(
            np.isclose(orders_of_magnitude, selected_order, atol=1)
        ) # within 1 order of magnitude of the max

        # change the scaling matrix used to calculate the distance
        # to place importance only on the sampled order of magnitude
        self._updater.model._Q = np.zeros( len(orders_of_magnitude) )
        for idx in idx_params_of_similar_uncertainty:
            self._updater.model._Q[idx] = 1

        d = self._updater.model.distance(x, xp)
        new_time = 1 / d
        experiment[self._t] = new_time

        print("Available orders of magnitude:", orders_of_magnitude)
        print("Selected order = ", selected_order)    
        print("x= {}".format(x))
        print("x'={}".format(xp))
        print("Distance = ", d)
        print("Distance order mag=", np.log10(d))
        print("=> time=", new_time)
        
        return experiment

class SampledUncertaintyWithConvergenceThreshold(BaseHeuristicQMLA):
    
    def __init__(
        self,
        updater,
        **kwargs
    ):
        super().__init__(updater, **kwargs)
        
        self._qinfer_model = self._updater.model
        cov_mtx = self._updater.est_covariance_mtx()
        self.initial_uncertainties = np.sqrt(np.abs(np.diag(cov_mtx)))
        self.track_param_uncertainties = np.zeros(self._qinfer_model.n_modelparams)
        self.selection_criteria = 'relative_volume_decrease'
        self.count_order_of_magnitudes =  {}
        self.counter_productive_experiments = 0 
        
    def __call__(
        self,
        epoch_id=0,
        **kwargs
    ):
        experiment = self._get_exp_params_array() # empty experiment array
        
        # sample from updater
        idx_iter = 0
        while idx_iter < self._maxiters:

            x, xp = self._updater.sample(n=2)[:, np.newaxis, :]
            if self._updater.model.distance(x, xp) > 0:
                break
            else:
                idx_iter += 1

        cov_mtx = self._updater.est_covariance_mtx()
        param_uncertainties = np.sqrt(np.abs(np.diag(cov_mtx))) # uncertainty of params individually
        orders_of_magnitude = np.log10(
            param_uncertainties
        ) # of the uncertainty on the individual parameters
        self.track_param_uncertainties = np.vstack( 
            (self.track_param_uncertainties, param_uncertainties) 
        )
        
        if self.selection_criteria == 'relative_volume_decrease':
            # probability of choosing  order of magnitude 
            # of each parameter based on the ratio
            # (change in volume)/(current estimate)
            # for that parameter
            print("Sampling by delta uncertainty/ estimate")
            change_in_uncertainty = np.diff( 
                self.track_param_uncertainties[-2:], # most recent two track-params
                axis = 0
            )[0]
            print("change in uncertainty=", change_in_uncertainty)
            if np.all( change_in_uncertainty <0):
                # TODO better way to deal with all increasing uncertainties
                print("All parameter uncertainties increased")
                self.counter_productive_experiments += 1
                change_in_uncertainty = np.abs(change_in_uncertainty)
            else:
                # disregard changes which INCREASE volume:
                change_in_uncertainty[ change_in_uncertainty < 0 ] = 0
            current_param_est = self._updater.est_mean()
            # weight = ratio of how much that change has decreased the volume 
            # over the current best estimate of the parameter
            weights = change_in_uncertainty / current_param_est
            probability_of_param = weights / sum(weights)

        elif self.selection_criteria == 'order_of_magniutde':
            # probability directly from order of magnitude
            print("Sampling by order magnitude")
            probability_of_param = np.array(orders_of_magnitude) / sum(orders_of_magnitude)

        else:
            # sample evenly
            print("Sampling evenly")
            probability_of_param = np.ones(self._qinfer_model.n_modelparams)
       

        # sample from the present orders of magnitude
        print("Prob of param=", probability_of_param)
        selected_order = np.random.choice(
            a = orders_of_magnitude, 
            p = probability_of_param
        )
        try:
            self.count_order_of_magnitudes[ np.round(selected_order)] += 1
        except:
            self.count_order_of_magnitudes[ np.round(selected_order)] = 1

        idx_params_of_similar_uncertainty = np.where(
            np.isclose(orders_of_magnitude, selected_order, atol=1)
        ) # within 1 order of magnitude of the max



        self._updater.model._Q = np.zeros( len(orders_of_magnitude) )
        for idx in idx_params_of_similar_uncertainty:
            self._qinfer_model._Q[idx] = 1

        d = self._qinfer_model.distance(x, xp)
        new_time = 1 / d
        experiment[self._t] = new_time

        print("orders_of_magnitude:", orders_of_magnitude)
        print("probability_of_param: ", probability_of_param)
        print("Selected order = ", selected_order)    
        print("x={}".format(x))
        print("xp={}".format(xp))
        print("Distance = ", d)
        print("Distance order mag=", np.log10(d))
        print("=> time=", new_time)
        
        return experiment
