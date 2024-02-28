from simcal.calibrator_param import OrderedParam


class Calibrator(object):
    def __init__(self):
        self._ordered_params = {}
        self._categorical_params = {}

    def calibrate(self, evaluate_point, compute_loss, reference_data, iterations=None, timeout=None):
        raise NotImplementedError(f"{self.__class__.__name__} does not define calibrate(self, evaluate_point, "
                                  f"compute_loss, reference_data, iterations=None, timeout=None)")
        # result=evaluate_point(calibration)
        # compute_loss(reference_data,result)

    def add_param(self, name, parameter):
        if isinstance(parameter, OrderedParam):
            self._ordered_params[name] = parameter
        else:
            self._categorical_params[name] = parameter
        return self
