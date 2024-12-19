import time

import numpy as np
from sklearn.preprocessing import normalize

import simcal.calibrators as sc
import simcal.coordinators.base as Coordinator
import simcal.exceptions as exception
import simcal.simulator as Simulator
from simcal.parameters import Base as parameter
from simcal.parameters import Value


class GradientDescent(sc.Base):
    def __init__(self, delta: float | int, epsilon: float | int, seed: int | None = None,
                 early_reject_loss: float | int | None = None):
        super().__init__()
        self.seed = seed
        self.epsilon = epsilon  # minimum change in loss to continue
        self.delta = delta  # initial change in parameters
        self.early_reject_loss = early_reject_loss

    def _populate(self, param_vector: list[float], vector_mapping: list[str], categoricals: dict[str, parameter]) -> \
            dict[str, parameter]:
        args = categoricals.copy()
        param_vector = param_vector.copy()
        self._clamp_vector(param_vector, vector_mapping)
        for i, key in enumerate(vector_mapping):
            args[key] = self._ordered_params[key].from_normalized(param_vector[i])
        return args

    def _evaluate_vector(self, simulator: Simulator, param_vector, vector_mapping, categoricals, stoptime):
        try:
            args = self._populate(param_vector, vector_mapping, categoricals, )
            self._timeout_shortout(stoptime)
            return simulator(args, stoptime)
        except exception.Timeout:
            raise
        except Exception as e:
            raise exception.SimulationFail(param_vector, e)

    def _clamp_vector(self, param_vector, vector_mapping):
        for i in range(len(param_vector)):
            param = self._get_raw_param(i, vector_mapping)
            param_vector[i] = sorted((param.range_start, param_vector[i], param.range_end))[1]  #
        return param_vector

    def _get_raw_param(self, index, vector_mapping):
        return self._ordered_params[vector_mapping[index]]

    def descend(self, simulator: Simulator, initial_point, stoptime):
        # TODO (later) gracefully handle early stops

        if not self._categorical_params:
            categorical_params = [None]
        else:
            categorical_params = self._categorical_params
        learning_rate = self.delta
        best_loss = None
        best = initial_point
        previous_loss = None
        vector_mapping = list(self._ordered_params.keys())
        dimensions = len(vector_mapping)
        param_vector = np.empty(dimensions)

        try:
            while True:
                for i, key in enumerate(vector_mapping):
                    param_vector[i] = self._ordered_params[key].to_normalized(best[key])
                # Get current loss and best categoricals
                best_categorical = None
                best_c_loss = None
                for c in categorical_params:
                    categoricals = {}
                    if c is not None:  # determin best categoricals at this point
                        for param in c:  # repackage categorical params for calibrator
                            categoricals[param[0]] = param[1]
                            loss = self._evaluate_vector(simulator, param_vector, vector_mapping, categoricals,
                                                         stoptime)
                            # print("checking categoricals", loss)
                            if best_c_loss is None or loss < best_c_loss:
                                best_categorical = categoricals.copy()
                                best_c_loss = loss
                    else:
                        best_categorical = {}
                        best_c_loss = self._evaluate_vector(simulator, param_vector, vector_mapping,
                                                            best_categorical, stoptime)

                if best_loss is None or best_c_loss < best_loss:
                    best_loss = best_c_loss
                    best = self._populate(param_vector, vector_mapping, best_categorical)
                if self.early_reject_loss is not None and best_loss >= self.early_reject_loss:
                    break
                # print("finding gradient")
                loss_at_param = best_c_loss
                # print("after categoricals, best loss is ", loss_at_param)
                # find gradient
                gradient = np.empty(dimensions)
                for i in range(dimensions):
                    tmp_vector = param_vector.copy()
                    # if we need to calculate a gradient where this goes outise the search space, flip sides and check the other way
                    # but you have to account for the flipped vector when calculating the gradient
                    if self._get_raw_param(i, vector_mapping).range_end < tmp_vector[i] + self.delta:
                        multiplier = 1
                    else:
                        multiplier = -1

                    tmp_vector[i] += self.delta * multiplier
                    direction_loss = self._evaluate_vector(simulator, tmp_vector, vector_mapping, best_categorical,
                                                           stoptime)
                    gradient[i] = (direction_loss - loss_at_param) / self.delta * multiplier
                    # print("loss while finding gradient", direction_loss)
                    if direction_loss < best_loss:
                        best_loss = direction_loss
                        best = self._populate(tmp_vector, vector_mapping, best_categorical)
                # print("Best loss before backtracking", best_loss)
                # [xi+1]=xi+norm_gradient*scale
                # h(xi)=f(xi)+gradient(dot)(xi-[xi+1])
                # h(xi)=f(xi)+gradient(dot)norm_gradient*scale

                # backtracking line search
                # print("backtracking Line search")
                grad_norm = normalize([gradient], norm="l2")[0]
                # why is scikit normalize so werid?  just take a 1d vector and return a scaler!
                backtrack = learning_rate * 10
                last_check = False
                in_minima = False
                while True:
                    gradient_step = grad_norm * backtrack
                    backtrack_test = param_vector + gradient_step
                    self._clamp_vector(backtrack_test, vector_mapping)
                    # expected = loss_at_param + gradient.dot(gradient_step)
                    # this simplifies out since we only check if we are going uphill to decide to backtrack

                    actual = self._evaluate_vector(simulator, backtrack_test, vector_mapping, best_categorical,
                                                   stoptime)
                    # print("backtracking", actual)
                    if actual < best_loss:
                        best_loss = actual
                        best = self._populate(backtrack_test, vector_mapping, best_categorical)
                        self.mark_calibration(self, (best, best_loss))
                        in_minima = True
                    if last_check:
                        break
                    if in_minima and actual > best_loss:  # in a minima And Going up the other side
                        last_check = True
                    if actual - loss_at_param < self.epsilon:  # we arent making any progress at all
                        last_check = True
                        # print("Just 1 more check")
                    backtrack /= 2
                # update learning rate
                learning_rate = backtrack
                # stop on a plateau
                if previous_loss is not None:
                    if previous_loss - best_loss < self.epsilon:
                        break
                previous_loss = best_loss
        except exception.EarlyTermination as e:
            ebest, eloss = e.result
            if eloss is None or (best_loss is not None and eloss > best_loss):
                e.result = (best, best_loss)
            raise e
        except exception.Timeout:

            # print("best loss, Timed out", best_loss)
            return best, best_loss
        except BaseException as e:
            # ("best loss, EXCEPTION!", best_loss)
            raise exception.EarlyTermination((best, best_loss), e)
        # print("best loss", best_loss)
        return best, best_loss

    def calibrate(self, simulator: Simulator, early_stopping_loss: float | int | None = None,
                  iterations: int | None = None, timelimit: float | int | None = None,
                  coordinator: Coordinator.Base | None = None) -> tuple[dict[str, Value | float | int], float]:
        if len(self._ordered_params) <= 0:
            internal = sc.Grid()
        else:
            internal = sc.Random(self.seed)
        # print("starting new gradient")
        internal._ordered_params = self._ordered_params
        internal._categorical_params = self._categorical_params
        if len(self._ordered_params) <= 0:  # of there are no ordered parameters, we are no different from a grid search, so let grid handle it
            return internal.calibrate(simulator, early_stopping_loss, iterations, timelimit, coordinator)
        else:  # we already have a good calibrator for random points, let it figure out the starts, then route back through us for the descending
            if timelimit is None:
                stoptime = None
            else:
                stoptime = time.time() + timelimit
            internal._eval = self.descend
            return internal.calibrate(simulator, early_stopping_loss, iterations, timelimit, coordinator)

    def _timeout_shortout(self, stoptime):
        if stoptime is not None:
            if time.time() > stoptime:
                raise exception.Timeout()
            return stoptime - time.time()
        return None

# class _GradientFunctor(object):
#    # this lets use use random search.  we make a functor with access the gradient descent, then we let random call the functor, which calls the descent function in gradient descent, which in turn calls the actual functor given to us
#    def __init__(self, grad, simulator):
#        self.grad = grad
#        self.simulator = simulator
#
#    def __call__(self, calibration):
#        return self.grad.descend(self.simulator, calibration)
