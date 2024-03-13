import random
from itertools import count
from time import time

from simcal.calibrators.base import Base


def _eval(evaluate_point, calibration):
    return evaluate_point(calibration), calibration


class Random(Base):
    def __init__(self,seed=None):
        super().__init__()
        if seed:
            random.seed(seed)
    def calibrate(self, evaluate_point, early_stopping_loss=None, iterations=None,
                  timeout=None, coordinator=None):
        # TODO handle iteration and steps_override modes
        from simcal.coordinators import Base as Coordinator
        if coordinator is None:
            coordinator = Coordinator()
        best = None
        best_loss = None
        if timeout is None:
            end = float('inf')
        else:
            end = time() + timeout
        if iterations is None:
            itr = count(start=0, step=1)
        else:
            itr = range(0, iterations)

        for i in itr:
            if time() > end:
                break

            calibration = {}
            for key in self._ordered_params:
                param = self._ordered_params[key]
                calibration[key] = param.from_normalized(random.uniform(param.range_start, param.range_end))

            for key in self._categorical_params:
                calibration[key] = random.choice(self._categorical_params[key].get_categories)

            coordinator.allocate(_eval, (evaluate_point, calibration))
            results = coordinator.collect()
            for loss, current in results:
                if best is None or loss < best_loss:
                    best = current
                    best_loss = loss

        return best
