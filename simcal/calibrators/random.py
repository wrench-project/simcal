import random
from itertools import count
from time import time
import simcal.exceptions as exception
import simcal.simulator as Simulator

from simcal.calibrators.base import Base as BaseCalibrator
import simcal.coordinators.base as Coordinator
from simcal.parameters import Value


def _eval(simulator: Simulator, calibration, stoptime):
    return calibration, simulator(calibration, stoptime)


class Random(BaseCalibrator):
    def __init__(self, seed=None):
        super().__init__()
        if seed:
            random.seed(seed)
        self._eval = _eval

    @BaseCalibrator.standard_exceptions
    def calibrate(self, simulator: Simulator, early_stopping_loss: float | int | None = None,
                  iterations: int | None = None, timelimit: float | int | None = None,
                  coordinator: Coordinator.Base | None = None) -> tuple[dict[str, Value | float | int], float]:
        # TODO handle iteration and steps_override modes
        from simcal.coordinators import Base as Coordinator
        if coordinator is None:
            coordinator = Coordinator()
        if timelimit is None:
            stoptime = float('inf')
        else:
            stoptime = time() + timelimit
        if iterations is None:
            itr = count(start=0, step=1)
        else:
            itr = range(0, iterations)

        for i in itr:
            if time() > stoptime:
                break

            calibration = {}
            for key in self._parameter_list.ordered_params:
                param = self._parameter_list.ordered_params[key]
                calibration[key] = param.from_normalized(random.uniform(param.range_start, param.range_end))

            for key in self._parameter_list.categorical_params:
                calibration[key] = random.choice(self._parameter_list.categorical_params[key].get_categories())

            coordinator.allocate(self._eval, (simulator, calibration, stoptime))
            self.best_result(coordinator.collect())
        self.best_result(coordinator.await_all())
        return self.current_best
