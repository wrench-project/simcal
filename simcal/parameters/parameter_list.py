from simcal.parameters.catagorical import Categorical
from simcal.parameters.ordered import Ordered
from typing import Self


class ParameterList(object):
    def __init__(self):
        self.ordered_params: dict[str, Ordered] = {}
        self.categorical_params: dict[str, Categorical] = {}

    def add_param(self, name: str, parameter: Ordered | Categorical) -> Self:
        """
        Method to add a to-be-calibrated parameter
        :param name: a user-defined parameter name
        :param parameter: the parameter
        :return: the calibrator
        :rtype simcal.calibrator.Base
        """
        if name in self.ordered_params or name in self.categorical_params:
            raise ValueError(f"Parameter {name} already exists")  # TODO: pick the correct error class
        if isinstance(parameter, Ordered):
            self.ordered_params[name] = parameter
        else:
            self.categorical_params[name] = parameter
        return self

    def get_param(self, name: str) -> Ordered | Categorical | None:
        """
                Method to retrieve a parameter by  name
                :param name: a user-defined parameter name
                :return: the parameter
                :rtype simcal.calibrator.Base
                """
        if name in self.ordered_params:
            return self.ordered_params[name]
        elif name in self.categorical_params:
            return self.categorical_params[name]
        else:
            return None