from itertools import count
from time import time

import skopt.optimizer as skopt
import skopt.space as sks

import simcal.coordinators.base as Coordinator
import simcal.exceptions as exception
from simcal.simulator import Simulator
from simcal.calibrators.base import Base as BaseCalibrator
from simcal.parameters import *


def _eval(simulator: Simulator, params, calibration, stoptime):
    try:
        return calibration, simulator(calibration, stoptime), params
    except exception.Timeout:
        raise
    except Exception as e:
        raise exception.SimulationFail(params, e)


# Base estimators can be
# "GP" for Gradient Process Regressor
# "RF" for Random Forrest Regresor
# "ET" for Extra Trees Regressor or
# "GBRT" for Gradient Boosting Quantile Regressor trees
class ScikitOptimizer(BaseCalibrator):
    def __init__(self, starts, base_estimator="GP", seed=None):
        super().__init__()
        self.seed = seed
        self.base_estimator = base_estimator
        self.starts = starts

    @BaseCalibrator.standard_exceptions
    def calibrate(self, simulator: Simulator, early_stopping_loss: float | int | None = None,
                  iterations: int | None = None, timelimit: float | int | None = None,
                  coordinator: Coordinator.Base | None = None) -> tuple[dict[str, Value | float | int], float]:
        from simcal.coordinators import Base as Coordinator

        # self._categorical_params = {}

        parameters = []
        for (key, param) in self._parameter_list.ordered_params.items():
            if isinstance(param, Exponential):
                if param.integer:
                    parameters.append(sks.Integer(int(param.from_normalized(param.range_start)),
                                                  int(param.from_normalized(param.range_end)), 'log-uniform', 2,
                                                  name=key))
                else:
                    parameters.append(sks.Real(float(param.from_normalized(param.range_start)),
                                               float(param.from_normalized(param.range_end)), 'log-uniform', 2,
                                               name=key))

            elif isinstance(param, Linear):
                if param.integer:
                    parameters.append(sks.Integer(param.start, param.end, 'uniform', 2, name=key))
                else:
                    parameters.append(sks.Real(param.start, param.end, 'uniform', 2, name=key))
            elif isinstance(param, Ordinal):
                parameters.append(sks.Integer(0, len(param.options) - 1, 'uniform', 2, name=key))
            elif isinstance(param, Ordered):
                if param.integer:
                    parameters.append(sks.Integer(param.range_start, param.range_end, 'uniform', 2, name=key))
                else:
                    parameters.append(sks.Real(param.range_start, param.range_end, 'uniform', 2, name=key))
        for (key, param) in self._parameter_list.categorical_params.items():
            parameters.append(sks.Categorical(param.categories, name=key))

        opt = skopt.Optimizer(
            dimensions=parameters,
            base_estimator=self.base_estimator,
            n_initial_points=self.starts,
            random_state=self.seed
        )

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
                params = opt.ask()
                calibration = self.to_regular_params(parameters, params)
                coordinator.allocate(_eval, (simulator, params, calibration, stoptime))
                self.best_result(coordinator.collect(), opt, parameters)
            self.best_result(coordinator.await_all(), opt, parameters)

        finally:
            results = opt.get_result()
            results.x = self.to_regular_params(parameters, results.x)
            self.mark_calibration((results.x, results.fun))
        return self.current_best

    def to_regular_params(self, parameters, params):
        calibration = {}
        for param, value in zip(parameters, params):
            coreParam = self.get_param(param.name)
            # if isinstance(coreParam,scp.Categorical):
            #    calibration[param.name] = coreParam.apply_format(value)
            if isinstance(coreParam, Ordinal):
                calibration[param.name] = coreParam.from_index(value)
            else:
                calibration[param.name] = coreParam.apply_format(value)
        return calibration

    def best_result(self, results, opt, parameters):
        best = None
        best_loss = None
        if self.current_best:
            best, best_loss = self.current_best
        for current, loss, tell in results:
            if loss is None:
                continue
            # print(best_loss,loss,current)
            opt.tell(tell, loss)
            if best_loss is None or loss < best_loss:
                best_loss = loss
                results = opt.get_result()
                self.mark_calibration((self.to_regular_params(parameters, results.x), best_loss))
