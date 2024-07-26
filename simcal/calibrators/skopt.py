import random
from itertools import count
from time import time

import skopt.optimizer as skopt

import simcal.calibrators as sc
import simcal.exceptions as exception
import simcal.simulator as Simulator


class ScikitOptimizer(sc.Base):
    def __init__(self, optimizer, epsilon, seed=None, early_reject_loss=None):
        super().__init__()
        self.seed = seed

    def calibrate(self, simulator: Simulator, early_stopping_loss=None, iterations=None,
                  timelimit=None, coordinator=None):
        from simcal.coordinators import Base as Coordinator
        #TODO rebuild param list
        opt = skopt.Optimizer()  # TODO params

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
        try:
            for i in itr:
                if time() > stoptime:
                    break

                calibration = {}
                # for key in self._ordered_params:
                #     param = self._ordered_params[key]
                #     calibration[key] = param.from_normalized(random.uniform(param.range_start, param.range_end))
                #
                # for key in self._categorical_params:
                #     calibration[key] = random.choice(self._categorical_params[key].get_categories())
                #TODO invoke ask
                #TODO reformat values
                coordinator.allocate(self._eval, (simulator, calibration, stoptime))
                results = coordinator.collect()
                for current, loss in results:
                    if loss is None:
                        continue
                    # print(best_loss,loss,current)
                    #TODO invoke tell
            results = coordinator.await_all()
            for current, loss in results:
                if loss is None:
                    continue
                # TODO invoke tell
        except exception.Timeout:
            # print("Random had to catch a timeout")
            results = opt.get_result()
            return results.x, results.fun
        except exception.EarlyTermination as e:
            ebest, eloss = e.result
            if eloss is None:
                results = opt.get_result()
                e.result = (results.x, results.fun)
            raise e
        except BaseException as e:
            results = opt.get_result()
            raise exception.EarlyTermination((results.x, results.fun), e)

        results = opt.get_result()
        return results.x, results.fun
