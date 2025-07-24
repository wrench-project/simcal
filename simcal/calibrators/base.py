import time
from typing import Self

import simcal.coordinators.base as Coordinator
from simcal.simulator import Simulator
from simcal.parameters import Categorical, Value
from simcal.parameters import Ordered
from simcal.parameters import ParameterList
from functools import wraps
import simcal.exceptions as exception


class Base(object):
    def __init__(self):
        self._parameter_list = ParameterList()
        self.timeline = []  # all best calibrations in order (up to _max_timeline to prevent memory issues)
        self._max_timeline = 100000
        self.current_best = None

    def mark_calibration(self, calibration):
        timestamp = int(time.time())
        if len(self.timeline) > self._max_timeline:
            self.timeline.pop(0)
        self.timeline.append((timestamp, calibration))
        self.current_best = calibration

    def calibrate(self, simulator: Simulator, early_stopping_loss: float | int | None = None,
                  iterations: int | None = None, timelimit: float | int | None = None,
                  coordinator: Coordinator.Base | None = None) -> tuple[dict[str, Value | float | int], float]:

        raise NotImplementedError(f"{self.__class__.__name__} does not define calibrate(self, simulator, "
                                  f"compute_loss, reference_data, iterations=None, timeout=None)")

    def add_param(self, name: str, parameter: Ordered | Categorical) -> Self:
        self._parameter_list.add_param(name, parameter)
        return self

    def get_param(self, name: str) -> Ordered | Categorical | None:
        return self._parameter_list.get_param(name)

    def best_result(self, results):
        best = None
        best_loss = None
        if self.current_best:
            best, best_loss = self.current_best
        for current, loss in results:
            if loss is None:
                continue
            if best is None or loss < best_loss:
                best = current
                best_loss = loss
                self.mark_calibration((best, best_loss))

        self.current_best = best, best_loss
        return best, best_loss

    @staticmethod
    def standard_exceptions(func):
        @wraps(func)
        def wrapper(self,*args, **kwargs):
            try:
                return func(self,*args, **kwargs)
            except exception.Timeout:
                return self.current_best
            except exception.EarlyTermination as e:
                ebest, eloss = e.result
                if eloss is None or (self.current_best is not None and eloss > self.current_best[1]):
                    e.result = self.current_best
                raise e
            except BaseException as e:
                raise exception.EarlyTermination(self.current_best, e)
        return wrapper
