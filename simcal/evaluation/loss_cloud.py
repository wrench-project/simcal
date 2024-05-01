import time
from enum import Enum
from logging import warning

import numpy


def LossCloud(BaseCalibrator):
    def __init__(self):
        super().__init__(self)

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
        if timelimit is not None:
            stoptime=time.time()+timelimit
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
                                   target_loss, hypercube_loss, loss_tolerance, recommended_epsilon, iterations=iterations,
                                   stoptime=stoptime, coordinator=coordinator)
        cloud_points += incidental_points

        cloud_points += search_cube(evaluate_point, lower_bound, upper_bound, target_loss, max_points=max_points,
                                    iterations=iterations, coordinator=coordinator)
        return cloud_points

    def find_cube_bound(self, direction, evaluate_point, center, target_loss, hypercube_loss, initial_epsilon,
                        iterations, stoptime, coordinator):
        cube_vector = center.copy()
        iterations_remaining = iterations
        cloud_points = set()
        recommended_epsilons=[]
        for param in self._ordered_params.keys():
            coordinator.allocate(self.binary_search, (direction,evaluate_point,center,target_loss,hypercube_loss,recommended_epsilon,iterations,stoptime))
            results = coordinator.collect()
            for param_value,param_key,recommended_epsilon,incidental_points in results:
                cloud_points+=incidental_points
                recommended_epsilons.append(recommended_epsilon)
                cube_vector[param_key]=param_value
        coordinator.allocate(self.binary_search, (direction,evaluate_point,center,target_loss,hypercube_loss,recommended_epsilon,iterations,stoptime))
        results = coordinator.await_all()
        for param_value,param_key,recommended_epsilon,incidental_points in results:
            cloud_points+=incidental_points
            recommended_epsilons.append(recommended_epsilon)
            cube_vector[param_key]=param_value

        return cube_vector, iterations_remaining, numpy.average(recommended_epsilons), cloud_points

    def binary_search(self, direction, param_key, initial_point, target_loss, hypercube_loss, initial_epsilon,
                      iterations, stoptime):
        param_value=initial_point[param_key]
        cloud_points=set()
        recomended_epsilon=initial_epsilon
        param_value,param_key,recomended_epsilon,cloud_points

    def search_cube(self, evaluate_point, lower_bound, upper_bound, target_loss,
                    max_points=None, iterations=None, stoptime=None, coordinator=None):
        cloud_points = set()
        return cloud_points


class _Direction(Enum):
    UPPER = +1
    LOWER = -1
