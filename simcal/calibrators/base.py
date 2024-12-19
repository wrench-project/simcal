from datetime import datetime
from typing import Self

import simcal.coordinators.base as Coordinator
import simcal.simulator as Simulator
from simcal.parameters import Categorical, Value
from simcal.parameters import Ordered


class Base(object):
    def __init__(self):
        self._ordered_params = {}
        self._categorical_params = {}
        self.timeline=[] # all best calibrations in order (up to _max_timeline to prevent memory issues)
        self._max_timeline=100000
        self.current_best=None

    def mark_calibration(self,calibration):
        time = datetime.now()
        if len(self.timeline) > self._max_timeline:
            self.timeline.pop(0)
        self.timeline.append((time,calibration))
        self.current_best(calibration)

    def calibrate(self, simulator: Simulator, early_stopping_loss: float | int | None = None,
                  iterations: int | None = None, timelimit: float | int | None = None,
                  coordinator: Coordinator.Base | None = None) -> tuple[dict[str, Value | float | int],float]:

        raise NotImplementedError(f"{self.__class__.__name__} does not define calibrate(self, simulator, "
                                  f"compute_loss, reference_data, iterations=None, timeout=None)")

    def add_param(self, name: str, parameter: Ordered | Categorical) -> Self:
        """
        Method to add a to-be-calibrated parameter
        :param name: a user-defined parameter name
        :param parameter: the parameter
        :return: the calibrator
        :rtype simcal.calibrator.Base
        """
        if name in self._ordered_params or name in self._categorical_params:
            raise ValueError(f"Parameter {name} already exists")  # TODO: pick the correct error class
        if isinstance(parameter, Ordered):
            self._ordered_params[name] = parameter
        else:
            self._categorical_params[name] = parameter
        return self

    def get_param(self, name: str) -> Ordered | Categorical | None:
        """
        Method to retrieve a parameter by  name
        :param name: a user-defined parameter name
        :return: the parameter
        :rtype simcal.calibrator.Base
        """
        if name in self._ordered_params:
            return self._ordered_params[name]
        elif name in self._categorical_params:
            return self._categorical_params[name]
        else:
            return None
