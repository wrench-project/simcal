import random
from itertools import count
from time import time
import simcal.exceptions as exception
import simcal.simulator as Simulator

from simcal.calibrators.base import Base
import simcal.coordinators.base as Coordinator
from simcal.parameters import Value


def _eval(simulator: Simulator, calibration, stoptime):
    return calibration, simulator(calibration, stoptime)


class Random(Base):
    def __init__(self, seed=None):
        super().__init__()
        if seed:
            random.seed(seed)
        self._eval = _eval

    def calibrate(self, simulator: Simulator, early_stopping_loss: float | int | None = None,
                  iterations: int | None = None, timelimit: float | int | None = None,
                  coordinator: Coordinator.Base | None = None) -> tuple[dict[str, Value | float | int], float]:
        # TODO handle iteration and steps_override modes
        from simcal.coordinators import Base as Coordinator
        if coordinator is None:
            coordinator = Coordinator()
        best = None
        best_loss = None
        if timelimit is None:
            stoptime = float('inf')
        else:
            stoptime = time() + timelimit
        if iterations is None:
            itr = count(start=0, step=1)
        else:
            itr = range(0, iterations)
        try:
            for i in itr:
                if time() > stoptime:
                    break

                calibration = {}
                for key in self._ordered_params:
                    param = self._ordered_params[key]
                    calibration[key] = param.from_normalized(random.uniform(param.range_start, param.range_end))

                for key in self._categorical_params:
                    calibration[key] = random.choice(self._categorical_params[key].get_categories())

                coordinator.allocate(self._eval, (simulator, calibration, stoptime))
                results = coordinator.collect()
                for current, loss in results:
                    if loss is None:
                        continue
                    #print(best_loss,loss,current)
                    if best is None or loss < best_loss:
                        best = current
                        best_loss = loss
                        self.mark_calibration(self, (best, best_loss))
            results = coordinator.await_all()
            for current, loss in results:
                if loss is None:
                    continue
                # print(best_loss,loss,current)
                if best is None or loss < best_loss:
                    best = current
                    best_loss = loss
                    self.mark_calibration(self, (best, best_loss))
        except exception.Timeout:
            #print("Random had to catch a timeout")
            return best, best_loss
        except exception.EarlyTermination as e:
            ebest, eloss = e.result
            if eloss is None or (best_loss is not None and eloss > best_loss):
                e.result = (best, best_loss)
            raise e
        except BaseException as e:
            raise exception.EarlyTermination((best, best_loss), e)
        return best, best_loss
