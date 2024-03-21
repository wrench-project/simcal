import random
import sys
from time import time

from simcal.calibrators.base import Base


def _eval(evaluate_point, calibration):
    return evaluate_point(calibration), calibration


class Debug(Base):
    def __init__(self, logger=sys.stdout):
        super().__init__()
        self.logger = logger

    def log(self, *args, **kwargs):
        print(*args, file=self.logger, **kwargs)

    def calibrate(self, evaluate_point, early_stopping_loss=None, iterations=None,
                  timelimit=None, coordinator=None):
        self.log("Calibrate", (evaluate_point, early_stopping_loss, iterations, timelimit, coordinator))
        # TODO handle iteration and steps_override modes
        from simcal.coordinators import Base as Coordinator
        if coordinator is None:
            coordinator = Coordinator()
        self.log("Using Coordinator", coordinator)

        calibration = {}
        for key in self._ordered_params:
            param = self._ordered_params[key]
            calibration[key] = param.from_normalized(0.5)

        for key in self._categorical_params:
            calibration[key] = self._categorical_params[key].get_categories()[0]

        self.log("Attempting execution", calibration)
        t0 = time()
        coordinator.allocate(_eval, (evaluate_point, calibration))
        results = coordinator.await_result()
        t1 = time()
        self.log("Finished, Time taken:", t1 - t0, "results:")
        self.log(results[0])

        return results[0]
