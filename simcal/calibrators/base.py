from simcal.parameters import Ordered
from simcal.parameters import Categorical
import simcal.simulator as Simulator


class Base(object):
    def __init__(self):
        self._ordered_params = {}
        self._categorical_params = {}

    def calibrate(self, simulator: Simulator, early_stopping_loss=None, iterations=None, timelimit=None, coordinator=None):
        raise NotImplementedError(f"{self.__class__.__name__} does not define calibrate(self, simulator, "
                                  f"compute_loss, reference_data, iterations=None, timeout=None)")

    def add_param(self, name: str, parameter: Ordered | Categorical):
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

    def get_param(self, name: str):
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
