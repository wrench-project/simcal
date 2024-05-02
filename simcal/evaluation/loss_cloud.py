import time
from enum import Enum
from logging import warning

import numpy

from simcal.calibrators import Base as BaseCalibrator


class LossCloud(BaseCalibrator):
    def __init__(self):
        super().__init__()

    def calibrate(self, evaluate_point, parameter_vector, target_loss, hypercube_loss, loss_tolerance,
                  initial_epsilon, early_stopping_loss=None,
                  max_points=None, iterations=None, timelimit=None, coordinator=None):
        warning(f"{self.__class__.__name__} is not actually a calibrator, "
                f"your call to calibrate has been forward to find_cloud."
                + (f"  early_stopping_loss has been ignored." if early_stopping_loss else ""))
        return self.find_cloud(evaluate_point, parameter_vector, target_loss, hypercube_loss, loss_tolerance,
                               initial_epsilon, iterations=iterations, timelimit=timelimit, coordinator=coordinator)

    def find_cloud(self, evaluate_point, parameter_vector, target_loss, hypercube_loss, loss_tolerance, initial_epsilon,
                   max_points=None,
                   iterations=None, timelimit=None, coordinator=None):
        from simcal.coordinators import Base as Coordinator
        if coordinator is None:
            coordinator = Coordinator()
        for key in self._ordered_params.keys():
            parameter_vector[key] = self._ordered_params[key].to_normalized(parameter_vector[key])
        if timelimit is not None:
            stoptime = time.time() + timelimit
        if iterations is not None:
            warning("Iteration limit not yet supported")
        if timelimit is None:
            raise ValueError("No stopping condition was given")
        cloud_points = set()
        iterations_remaining = iterations
        upper_bound, iterations_remaining, recommended_epsilon, incidental_points \
            = self.find_cube_bound(_Direction.UPPER, evaluate_point, parameter_vector,
                                   target_loss, hypercube_loss, loss_tolerance, initial_epsilon, iterations=iterations,
                                   stoptime=stoptime, coordinator=coordinator)
        cloud_points += incidental_points

        lower_bound, iterations_remaining, recommended_epsilon, incidental_points \
            = self.find_cube_bound(_Direction.LOWER, evaluate_point, parameter_vector,
                                   target_loss, hypercube_loss, loss_tolerance, recommended_epsilon,
                                   iterations=iterations,
                                   stoptime=stoptime, coordinator=coordinator)
        cloud_points += incidental_points

        cloud_points += self.search_cube(evaluate_point, lower_bound, upper_bound, target_loss, max_points=max_points,
                                         iterations=iterations, coordinator=coordinator)
        return cloud_points

    def find_cube_bound(self, direction, evaluate_point, center, target_loss, hypercube_loss, loss_tolerance,
                        initial_epsilon,
                        iterations, stoptime, coordinator):
        cube_vector = center.copy()
        iterations_remaining = iterations
        cloud_points = set()
        recommended_epsilon = initial_epsilon
        recommended_epsilons = []
        for param in self._ordered_params.keys():
            coordinator.allocate(self.binary_search, (
                direction, param, evaluate_point, center, target_loss, hypercube_loss, loss_tolerance,
                recommended_epsilon,
                iterations, stoptime))
            results = coordinator.collect()
            for param_value, param_key, recommended_epsilon, incidental_points, iterations_used in results:
                cloud_points += incidental_points
                recommended_epsilons.append(recommended_epsilon)
                cube_vector[param_key] = param_value
            iterations_remaining -= iterations_used
        results = coordinator.await_all()
        for param_value, param_key, recommended_epsilon, incidental_points, iterations_used in results:
            cloud_points += incidental_points
            recommended_epsilons.append(recommended_epsilon)
            cube_vector[param_key] = param_value
            iterations_remaining -= iterations_used
        return cube_vector, iterations_remaining, numpy.average(recommended_epsilons), cloud_points

    def binary_search(self, direction, param_key, evaluate_point, initial_point, target_loss, hypercube_loss,
                      loss_tolerance,
                      initial_epsilon,
                      iterations_limit, stoptime):

        param_value = initial_point.copy()
        min_value = param_value[param_key]
        max_value = param_value[param_key] + initial_epsilon * direction
        current = max_value
        cloud_points = set()
        iterations = 0

        recomended_epsilon = None
        while True:
            param_value[param_key] = current

            ret = self._eval(evaluate_point, param_value, stoptime)
            iterations += 1
            if ret < target_loss:
                cloud_points.add(param_value.copy)
            if abs(ret - hypercube_loss) < loss_tolerance:
                break
            if ret < hypercube_loss:
                if recomended_epsilon is None:  # expanding search
                    max_value += (min_value - max_value)
                    current = max_value
                else:
                    min_value = current
                    current = (min_value + max_value) / 2
            if not self._ordered_params[param_key].is_valid_normalized(current):
                current = sorted((self._ordered_params[param_key].range_start, current, self._ordered_params[param_key].range_end))[1]
                break
            if ret > hypercube_loss:
                if recomended_epsilon is None:
                    recomended_epsilon = abs(initial_point[param_key] - current)
                max_value = current
                current = (min_value + max_value) / 2
            if iterations_limit is not None and iterations > iterations_limit:
                break

        if recomended_epsilon is None:
            recomended_epsilon = initial_epsilon

        return current, param_key, recomended_epsilon, cloud_points, iterations

    def search_cube(self, evaluate_point, lower_bound, upper_bound, target_loss,
                    max_points=None, iterations=None, stoptime=None, coordinator=None):
        cloud_points = set()
        return cloud_points

    def _eval(self, evaluate_point, args, stoptime):
        parameter_vector = args.copy()
        for key in self._ordered_params.keys():
            parameter_vector[key] = self._ordered_params[key].to_normalized(parameter_vector[key])
        evaluate_point(parameter_vector, stoptime)


class _Direction(Enum):
    UPPER = +1
    LOWER = -1
