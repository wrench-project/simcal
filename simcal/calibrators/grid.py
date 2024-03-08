from fractions import Fraction
from itertools import product
from math import ceil
from time import time

from numpy import linspace

from simcal.calibrators.base import Base


def _eval(evaluate_point, calibration):
    # print(evaluate_point)
    return evaluate_point(calibration), calibration


class Grid(Base):
    def __init__(self):
        super().__init__()

    def calibrate(self, evaluate_point, compute_loss, reference_data, step_override=None, iterations=None,
                  timeout=None, coordinator=None):
        # TODO handle iteration and steps_override modes
        from simcal.coordinators import Base as Coordinator
        if coordinator is None:
            coordinator = Coordinator()
        best = None
        best_loss = None
        if timeout is not None:
            end = time() + timeout
            for calibration in _RectangularIterator(self._ordered_params, self._categorical_params):
                if time() > end:
                    break
                coordinator.allocate(_eval, (evaluate_point, calibration))
                results = coordinator.collect()
                for result, current in results:
                    loss = compute_loss(reference_data, result)
                    if best is None or loss < best_loss:
                        best = current
                        best_loss = loss
        return best


def _grid_key(a):
    at = 0
    for i in a:
        at += _smallest_denominator(i)
    return at


def _smallest_denominator(decimal):
    fraction = Fraction(decimal).limit_denominator()
    return fraction.denominator


class _RectangularIterator(object):
    def __init__(self, ordered_params, categorical_params):
        self._ordered_params_conversion = []
        self._ordered_params = []
        for key in ordered_params:
            self._ordered_params_conversion.append(key)
            self._ordered_params.append(ordered_params[key])
        categorical_params_list = []
        # print(categorical_params)
        if not categorical_params:
            self._categorical_params = [None]
        else:
            for key in categorical_params:
                categories = []
                for option in categorical_params[key].get_categories():
                    categories.append((key, option))
                categorical_params_list.append(categories)
            self._categorical_params = product(*categorical_params_list)

    def __iter__(self):
        denominator = 1
        cores = []  # [[0, 1]...]
        current_sets = []  # [{0, 1}...]
        if not self._ordered_params:
            for c in self._categorical_params:  # send off each combination of categorical paramiters for this grid point
                ret = {}
                if c is not None:
                    for param in c:  # repackage categorical params for calibrator
                        ret[param[0]] = param[1]  # param is a touple (name,value)
                yield ret
            return

        for param in self._ordered_params:
            range_size = abs(ceil(param.range_end - param.range_start)) + 1
            seed = linspace(param.range_start, param.range_end, num=range_size)
            cores.append(list(seed))
            current_sets.append(set(seed))

        while True:
            for i in sorted(product(*cores), reverse=True, key=_grid_key):
                for j, cs in zip(i, current_sets):
                    if j in cs:  # prevent repeats by requiring atleast 1 element of the touple to be from the current set of numbers
                        for c in self._categorical_params:  # send off each combination of categorical paramiters for this grid point
                            ret = {}
                            for index, param in enumerate(i):  # repackcage ordered params for calibrator
                                name = self._ordered_params_conversion[index]
                                ret[name] = param
                            if c is not None:
                                for param in c:  # repackage categorical params for calibrator
                                    ret[param[0]] = param[1]  # param is a touple (name,value)
                            yield ret
                        break
            denominator *= 2
            for i in range(len(cores)):
                update = [j + 1 / denominator for j in cores[i][:-1]]
                current_sets[i] = set(update)
                cores[i] += update
