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
