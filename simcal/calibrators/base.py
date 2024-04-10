from simcal.parameters import Ordered


class Base(object):
    def __init__(self):
        self._ordered_params = {}
        self._categorical_params = {}

    def calibrate(self, evaluate_point, early_stopping_loss=None, iterations=None, timelimit=None, coordinator=None):
        raise NotImplementedError(f"{self.__class__.__name__} does not define calibrate(self, evaluate_point, "
                                  f"compute_loss, reference_data, iterations=None, timeout=None)")
        # result=evaluate_point(calibration)
        # compute_loss(reference_data,result)

    def add_param(self, name, parameter):
        if name in self._ordered_params or name in self._categorical_params:
            raise ValueError(f"Parameter {name} already exists")  # TODO: pick the correct error class
        if isinstance(parameter, Ordered):
            self._ordered_params[name] = parameter
        else:
            self._categorical_params[name] = parameter
        return self

    def get_param(self, name):
        if name in self._ordered_params:
            return self._ordered_params[name]
        elif name in self._categorical_params:
            return self._categorical_params[name]
        else:
            return None
