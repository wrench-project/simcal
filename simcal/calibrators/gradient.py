import numpy as np
from sklearn.preprocessing import normalize

from simcal.calibrators import Random, Grid
from simcal.calibrators.base import Base


class GradientDescent(Base):
    def __init__(self, delta=None, epsilon=None, seed=None, early_stopping_loss=None):
        super().__init__()
        self.seed = seed
        self.epsilon = epsilon
        self.delta = delta
        self.early_stopping_loss = early_stopping_loss

    def _populate(self, param_vector, vector_mapping, categoricals):
        args = categoricals.copy()
        for i, key in enumerate(param_vector):
            args[key] = self._ordered_params[key].from_normalized(param_vector[key])
        return args

    def _evaluate_vector(self, evaluate_point, param_vector, vector_mapping, categoricals):
        args = self._populate(param_vector, vector_mapping, categoricals)
        return evaluate_point(args)

    def descend(self, evaluate_point, initial_point):
        # TODO (later) gracefully handle early stops
        if not self._categorical_params:
            categorical_params = [None]
        else:
            categorical_params = self._categorical_params
        delta = self.delta
        best_loss = None
        best = None
        previous_loss = None
        vector_mapping = list(self._ordered_params.keys())
        dimensions = len(vector_mapping)
        param_vector = np.empty(dimensions)

        for i, key in vector_mapping:
            param_vector[i] = self._ordered_params.keys[key].to_normalized(initial_point[key])

        while True:
            # Get current loss and best categoricals
            best_categorical = None
            best_c_loss = None
            for c in self._categorical_params:
                categoricals = {}
                if c is not None:  # determin best categoricals at this point
                    for param in c:  # repackage categorical params for calibrator
                        categoricals[param[0]] = param[1]
                        loss = self._evaluate_vector(evaluate_point, param_vector, vector_mapping, categoricals)
                        if best_c_loss is None or best_c_loss > loss:
                            best_categorical = categoricals.copy()
                            best_c_loss = loss
                else:
                    best_categorical = {}
                    best_c_loss = self._evaluate_vector(evaluate_point, param_vector, vector_mapping, best_categorical)

            if best_loss is None or best_loss < best_c_loss:
                best_loss = best_c_loss
                best = self._populate(param_vector, vector_mapping, best_categorical)
            if best_loss >= self.early_stopping_loss:
                break
            loss_at_param = best_c_loss
            # find gradient
            gradient = np.empty(dimensions)
            for i in range(dimensions):
                tmp_vector = param_vector.copy()
                tmp_vector[i] += delta
                direction_loss = self._evaluate_vector(evaluate_point, tmp_vector, vector_mapping, best_categorical)
                gradient[i] = (direction_loss - loss_at_param) / delta
                if direction_loss < best_loss:
                    best_loss = direction_loss
                    best = self._populate(param_vector, vector_mapping, best_categorical)

            # [xi+1]=xi+norm_gradient*scale
            # h(xi)=f(xi)+gradient(dot)(xi-[xi+1])
            # h(xi)=f(xi)+gradient(dot)norm_gradient*scale

            # backtracking line search
            grad_norm = normalize(gradient, norm="l2")
            backtrack = delta * 10
            last_check = False
            while True:
                gradient_step = grad_norm * backtrack
                backtrack_test = param_vector + gradient_step
                # expected = loss_at_param + gradient.dot(gradient_step)
                # this simplifies out since we only check if we are going uphill to decide to backtrack
                actual = self._evaluate_vector(evaluate_point, backtrack_test, vector_mapping, best_categorical)
                if actual < best_loss:
                    best_loss = actual
                    best = backtrack_test
                if last_check:
                    break
                if loss_at_param - actual < self.epsilon:  # we arent making any progress at all
                    last_check = True

                backtrack /= 2
            # update learning rate
            delta = backtrack
            # stop on a plataeu
            if previous_loss is not None:
                if previous_loss - best_loss < self.epsilon:
                    break
            previous_loss = best_loss
        return best, best_loss

    def calibrate(self, evaluate_point, early_stopping_loss=None, iterations=None,
                  timelimit=None, coordinator=None):
        if self._ordered_params.empty():
            internal = Grid()
        else:
            internal = Random(self.seed)
        internal._ordered_params = self._ordered_params
        internal._categorical_params = self._categorical_params

        if self._ordered_params.empty():  # of there are no ordered parameters, we are no different from a grid search, so let grid handle it
            return internal.calibrate(evaluate_point, early_stopping_loss, iterations, timelimit, coordinator)
        else:  # we already have a good calibrator for random points, let it figure out the starts, then route back through us for the descending
            functor = _GradientFunctor(self, evaluate_point)
            return internal.calibrate(functor, early_stopping_loss, iterations, timelimit, coordinator)


class _GradientFunctor(object):
    # this lets use use random search.  we make a functor with access the gradient descent, then we let random call the functor, which calls the descent function in gradient descent, which in turn calls the actual functor given to us
    def __init__(self, grad, evaluate_point):
        self.grad = grad
        self.evaluate_point = evaluate_point

    def __call__(self, calibration):
        return self.grad.descend(self.evaluate_point, calibration)


def sampleHyperplane(sample_at, relative_to, slope, vector, stepSize):
    s = slope
    for i in range(len(sample_at)):
        # print(x[i],ref[i],x[i]-ref[i],vector[i]/stepSize,(x[i]-ref[i])*vector[i]/stepSize)
        s += (sample_at[i] - relative_to[i]) * vector[i] / stepSize
    return s
