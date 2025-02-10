import sys
from time import time
from typing import TextIO

import simcal.coordinators.base as Coordinator
import simcal.simulator as Simulator
from simcal.calibrators.base import Base as BaseCalibrator
from simcal.parameters import Value


def _eval(simulator, calibration):
    return simulator(calibration), calibration


class Debug(BaseCalibrator):
    def __init__(self, logger: TextIO = sys.stdout):
        super().__init__()
        self.logger = logger

    def log(self, *args, **kwargs):
        print(*args, file=self.logger, **kwargs)

    def calibrate(self, simulator: Simulator, early_stopping_loss: float | int | None = None,
                  iterations: int | None = None, timelimit: float | int | None = None,
                  coordinator: Coordinator.Base | None = None) -> tuple[dict[str, Value | float | int], float]:
        self.log("Calibrate", (simulator, early_stopping_loss, iterations, timelimit, coordinator))
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
        coordinator.allocate(_eval, (simulator, calibration))
        results = coordinator.await_result()
        t1 = time()
        self.log("Finished, Time taken:", t1 - t0, "results:")
        self.log(results[0])

        return results[0]
