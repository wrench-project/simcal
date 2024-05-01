import random
from itertools import count
from time import time
import simcal.exceptions as exception

from simcal.calibrators.base import Base


def _eval(evaluate_point, calibration, stop_time):
    return calibration, evaluate_point(calibration, stop_time)


class Random(Base):
    def __init__(self, seed=None):
        super().__init__()
        if seed:
            random.seed(seed)
        self._eval = _eval

    def calibrate(self, evaluate_point, early_stopping_loss=None, iterations=None,
                  timelimit=None, coordinator=None):
        # TODO handle iteration and steps_override modes
        from simcal.coordinators import Base as Coordinator
        if coordinator is None:
            coordinator = Coordinator()
        best = None
        best_loss = None
        if timelimit is None:
            stop_time = float('inf')
        else:
            stop_time = time() + timelimit
        if iterations is None:
            itr = count(start=0, step=1)
        else:
            itr = range(0, iterations)
        try:
            for i in itr:
                if time() > stop_time:
                    break

                calibration = {}
                for key in self._ordered_params:
                    param = self._ordered_params[key]
                    calibration[key] = param.from_normalized(random.uniform(param.range_start, param.range_end))

                for key in self._categorical_params:
                    calibration[key] = random.choice(self._categorical_params[key].get_categories())

                coordinator.allocate(self._eval, (evaluate_point, calibration, stop_time))
                results = coordinator.collect()
                for current, loss in results:
                    if loss is None:
                        continue
                    #print(best_loss,loss,current)
                    if best is None or loss < best_loss:
                        best = current
                        best_loss = loss
        except exception.Timeout:
            return best, best_loss
        except exception.EarlyTermination as e:
            ebest, eloss = e.result
            if eloss is None or (best_loss is not None and eloss > best_loss):
                e.result = (best, best_loss)
            raise e
        except BaseException as e:
            raise exception.EarlyTermination((best, best_loss), e)
        return best, best_loss
