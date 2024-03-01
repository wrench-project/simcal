from math import ceil

from simcal.calibrators.calibrator import Calibrator
from fractions import Fraction
from itertools import product
from numpy import linspace
from time import time


def _eval(evaluate_point, calibration):
    return evaluate_point(calibration), calibration


class GridCalibrator(Calibrator):
    def __init__(self):
        super().__init__()

    def calibrate(self, evaluate_point, compute_loss, reference_data, step_override=None, iterations=None,
                  timeout=None, coordinator=None):
        # TODO handle iteration and steps_override modes
        from simcal import Coordinator
        if coordinator is None:
            coordinator = Coordinator()
        best = None
        best_loss = None
        if timeout is not None:
            end = time() + timeout
            for calibration in _RectangularIterator(self._ordered_params, self._categorical_params):
                if time() > end:
                    break
                coordinator.allocate(_eval, evaluate_point, calibration)
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
        self._ordered_params_conversion = ordered_params.keys()
        self._ordered_params = ordered_params.values()
        categorical_params_list = []
        # TODO handle empty params cases
        for key in categorical_params:
            categories = []
            for option in categorical_params[key].get_categories():
                categories.append((key, option))
            categorical_params_list.append(categories)
        self._categorical_params = product(*categorical_params_list)

    def __iter__(self):
        return self

    def __next__(self):
        denominator = 1
        cores = []  # [[0, 1]...]
        current_sets = []  # [{0, 1}...]
        for param in self._ordered_params:
            range_size = abs(ceil(param.range_end - param.range_start))
            seed = linspace(param.range_start, param.range_end, num=range_size)
            cores.append(seed)
            current_sets.append(set(seed))

        while True:
            for i in sorted(product(*cores), reverse=True, key=_grid_key):
                for j, cs in zip(i, current_sets):
                    if j in cs:  # prevent repeats by requiring atleast 1 element of the touple to be from the current set of numbers
                        # print(i)
                        for c in self._categorical_params:  # send off each combination of categorical paramiters for this grid point
                            ret = {}
                            for index, param in enumerate(i):  # repackcage ordered params for calibrator
                                name = self._ordered_params_conversion[index]
                                ret[name] = param
                            for param in c:  # repackage categorical params for calibrator
                                ret[param[0]] = param[1]  # param is a touple (name,value)
                            yield ret
                        break
            denominator *= 2
            for i in range(len(cores)):
                update = [j + 1 / denominator for j in cores[i][:-1]]
                current_sets[i] = set(update)
                cores[i] += update
