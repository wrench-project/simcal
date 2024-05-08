import time

import numpy as np
from sklearn.preprocessing import normalize

import simcal.calibrators as sc
import simcal.exceptions as exception


class GradientDescent(sc.Base):
    def __init__(self, delta, epsilon, seed=None, early_reject_loss=None):
        super().__init__()
        self.seed = seed
        self.epsilon = epsilon
        self.delta = delta
        self.early_reject_loss = early_reject_loss

    def _populate(self, param_vector, vector_mapping, categoricals):
        args = categoricals.copy()
        param_vector = param_vector.copy()
        self._clamp_vector(param_vector, vector_mapping)
        for i, key in enumerate(vector_mapping):
            args[key] = self._ordered_params[key].from_normalized(param_vector[i])
        return args

    def _evaluate_vector(self, evaluate_point, param_vector, vector_mapping, categoricals, stop_time):
        args = self._populate(param_vector, vector_mapping, categoricals, )
        self._timeout_shortout(stop_time)
        return evaluate_point(args, stop_time)

    def _clamp_vector(self, param_vector, vector_mapping):
        for i in range(len(param_vector)):
            param = self._get_raw_param(i, vector_mapping)
            param_vector[i] = sorted((param.range_start, param_vector[i], param.range_end))[1]  #
        return param_vector

    def _get_raw_param(self, index, vector_mapping):
        return self._ordered_params[vector_mapping[index]]

    def descend(self, evaluate_point, initial_point, stop_time):
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
                            loss = self._evaluate_vector(evaluate_point, param_vector, vector_mapping, categoricals,
                                                         stop_time)
                            if best_c_loss is None or best_c_loss > loss:
                                best_categorical = categoricals.copy()
                                best_c_loss = loss
                    else:
                        best_categorical = {}
                        best_c_loss = self._evaluate_vector(evaluate_point, param_vector, vector_mapping,
                                                            best_categorical, stop_time)

                if best_loss is None or best_loss < best_c_loss:
                    best_loss = best_c_loss
                    best = self._populate(param_vector, vector_mapping, best_categorical)
                if self.early_reject_loss is not None and best_loss >= self.early_reject_loss:
                    break
                # print("finding gradient")
                loss_at_param = best_c_loss
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
                    direction_loss = self._evaluate_vector(evaluate_point, tmp_vector, vector_mapping, best_categorical,
                                                           stop_time)
                    gradient[i] = (direction_loss - loss_at_param) / self.delta * multiplier
                    if direction_loss < best_loss:
                        best_loss = direction_loss
                        best = self._populate(tmp_vector, vector_mapping, best_categorical)

                # [xi+1]=xi+norm_gradient*scale
                # h(xi)=f(xi)+gradient(dot)(xi-[xi+1])
                # h(xi)=f(xi)+gradient(dot)norm_gradient*scale

                # backtracking line search
                # print("backtracking Line search")
                grad_norm = normalize([gradient], norm="l2")[0]
                # why is scikit normalize so werid?  just take a 1d vector and return a scaler!
                backtrack = learning_rate * 10
                last_check = False
                while True:
                    gradient_step = grad_norm * backtrack
                    backtrack_test = param_vector + gradient_step
                    self._clamp_vector(backtrack_test, vector_mapping)
                    # expected = loss_at_param + gradient.dot(gradient_step)
                    # this simplifies out since we only check if we are going uphill to decide to backtrack

                    actual = self._evaluate_vector(evaluate_point, backtrack_test, vector_mapping, best_categorical,
                                                   stop_time)
                    if actual < best_loss:
                        best_loss = actual
                        best = self._populate(backtrack_test, vector_mapping, best_categorical)
                    if last_check:
                        break
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
            return best, best_loss
        except BaseException as e:
            raise exception.EarlyTermination((best, best_loss), e)
        return best, best_loss

    def calibrate(self, evaluate_point, early_stopping_loss=None, iterations=None,
                  timelimit=None, coordinator=None):
        if len(self._ordered_params) <= 0:
            internal = sc.Grid()
        else:
            internal = sc.Random(self.seed)
        # print("starting new gradient")
        internal._ordered_params = self._ordered_params
        internal._categorical_params = self._categorical_params
        if len(self._ordered_params) <= 0:  # of there are no ordered parameters, we are no different from a grid search, so let grid handle it
            return internal.calibrate(evaluate_point, early_stopping_loss, iterations, timelimit, coordinator)
        else:  # we already have a good calibrator for random points, let it figure out the starts, then route back through us for the descending
            if timelimit is None:
                stop_time = None
            else:
                stop_time = time.time() + timelimit
            internal._eval = self.descend
            return internal.calibrate(evaluate_point, early_stopping_loss, iterations, timelimit, coordinator)

    def _timeout_shortout(self, stoptime):
        if stoptime is not None:
            if time.time() > stoptime:
                raise exception.Timeout()
            return stoptime - time.time()
        return None

# class _GradientFunctor(object):
#    # this lets use use random search.  we make a functor with access the gradient descent, then we let random call the functor, which calls the descent function in gradient descent, which in turn calls the actual functor given to us
#    def __init__(self, grad, evaluate_point):
#        self.grad = grad
#        self.evaluate_point = evaluate_point
#
#    def __call__(self, calibration):
#        return self.grad.descend(self.evaluate_point, calibration)
