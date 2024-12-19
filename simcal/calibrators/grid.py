from fractions import Fraction
from itertools import product
from math import ceil
from time import time

from numpy import linspace

import simcal.coordinators.base as Coordinator
import simcal.exceptions as exception
import simcal.simulator as Simulator
from simcal.calibrators.base import Base
from simcal.parameters import Value


def _eval(simulator: Simulator, calibration, stoptime):
    return calibration, simulator(calibration, stoptime)


class Grid(Base):
    def __init__(self):
        super().__init__()

    def calibrate(self, simulator: Simulator, early_stopping_loss: float | int | None = None,
                  iterations: int | None = None, timelimit: float | int | None = None,
                  coordinator: Coordinator.Base | None = None) -> tuple[dict[str, Value | float | int], float]:
        # TODO handle iteration and steps_override modes
        from simcal.coordinators import Base as Coordinator
        if coordinator is None:
            coordinator = Coordinator()
        best = None
        best_loss = None

        if timelimit is not None:
            try:
                stoptime = time() + timelimit
                for calibration in _RectangularIterator(self._ordered_params, self._categorical_params):
                    if time() > stoptime:
                        break
                    coordinator.allocate(_eval, (simulator, calibration, stoptime))
                    results = coordinator.collect()
                    for current, loss in results:
                        if loss is None:
                            continue
                        if best is None or loss < best_loss:
                            best = current
                            best_loss = loss
                            self.mark_calibration((best, best_loss))
                results = coordinator.await_all()
                for current, loss in results:
                    if loss is None:
                        continue
                    if best is None or loss < best_loss:
                        best = current
                        best_loss = loss
                        self.mark_calibration((best, best_loss))
            except exception.Timeout:
                return best, best_loss
            except exception.EarlyTermination as e:
                ebest, eloss = e.result
                if eloss is None or (best_loss is not None and eloss > best_loss):
                    e.result = (best, best_loss)
                raise e
            except BaseException as e:
                raise exception.EarlyTermination((best, best_loss), e)
        return best, best_loss


def _grid_key(a):
    at = 0
    for i in a:
        at += _smallest_denominator(i)
    return at


def _smallest_denominator(decimal):
    fraction = Fraction(decimal).limit_denominator()
    return fraction.denominator


class _RectangularIterator(object):
    def __init__(self, ordered_params, categorical_params, uprez=None):
        self._ordered_params_conversion = []
        self._ordered_params = []
        self._uprez = uprez
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
                            for index, value in enumerate(i):  # repackcage ordered params for calibrator
                                name = self._ordered_params_conversion[index]
                                ret[name] = self._ordered_params[index].from_normalized(value)
                            if c is not None:
                                for param in c:  # repackage categorical params for calibrator
                                    ret[param[0]] = param[1]  # param is a touple (name,value)
                            yield ret
                        break  # This break is needed, I dont remember why, but without it you sample points multiple times.  I know it looks like it skips some points, but it doesnt seem too actually do so.

            denominator *= 2
            for i in range(len(cores)):
                update = [j + 1 / denominator for j in cores[i][:-1]]
                current_sets[i] = set(update)
                cores[i] += update
                cores[i].sort()
            if self._uprez:
                self._uprez()
