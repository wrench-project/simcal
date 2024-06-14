import time
from enum import Enum
from logging import warning

import numpy
import simcal.simulator as Simulator

from simcal import parameter, exception
from simcal.calibrators import Base as BaseCalibrator
from simcal.calibrators.grid import _RectangularIterator


class LossCloud(BaseCalibrator):
    def __init__(self):
        super().__init__()

    def calibrate(self, simulator: Simulator, parameter_vector, target_loss, hypercube_loss, loss_tolerance,
                  initial_epsilon, early_stopping_loss=None,
                  max_points=None, iterations=None, timelimit=None, coordinator=None):
        warning(f"{self.__class__.__name__} is not actually a calibrator, "
                f"your call to calibrate has been forward to find_cloud."
                + (f"  early_stopping_loss has been ignored." if early_stopping_loss else ""))
        return self.find_cloud(simulator, parameter_vector, target_loss, hypercube_loss, loss_tolerance,
                               initial_epsilon, iterations=iterations, timelimit=timelimit, coordinator=coordinator)

    def find_cloud(self, simulator: Simulator, parameter_vector, target_loss, hypercube_loss, loss_tolerance, initial_epsilon,
                   max_points=None,
                   iterations=None, timelimit=None, coordinator=None):
        from simcal.coordinators import Base as Coordinator
        if coordinator is None:
            coordinator = Coordinator()
        # for key in self._ordered_params.keys():
        #    parameter_vector[key] = self._ordered_params[key].to_normalized(parameter_vector[key])
        if timelimit is not None:
            stoptime = time.time() + timelimit
        if iterations is not None:
            warning("Iteration limit not yet supported")
        if timelimit is None:
            raise ValueError("No stopping condition was given")
        cloud_points = []
        iterations_remaining = iterations
        if iterations_remaining is None:
            iterations_remaining = float('inf')
        upper_bound, iterations_remaining, recommended_epsilon, incidental_points \
            = self.find_cube_bound(_Direction.UPPER, simulator, parameter_vector,
                                   target_loss, hypercube_loss, loss_tolerance, initial_epsilon,
                                   iterations=iterations_remaining,
                                   stoptime=stoptime, coordinator=coordinator)
        cloud_points += incidental_points

        lower_bound, iterations_remaining, recommended_epsilon, incidental_points \
            = self.find_cube_bound(_Direction.LOWER, simulator, parameter_vector,
                                   target_loss, hypercube_loss, loss_tolerance, recommended_epsilon,
                                   iterations=iterations_remaining,
                                   stoptime=stoptime, coordinator=coordinator)
        cloud_points += incidental_points
        print(lower_bound)
        print(upper_bound)
        cloud_points += self.search_cube(simulator, lower_bound, upper_bound, parameter_vector, target_loss,
                                         max_points=max_points,
                                         iterations=iterations_remaining, stop_time=stoptime, coordinator=coordinator)
        return cloud_points

    def find_cube_bound(self, direction, simulator: Simulator, center, target_loss, hypercube_loss, loss_tolerance,
                        initial_epsilon,
                        iterations, stoptime, coordinator):
        cube_vector = center.copy()
        iterations_remaining = iterations
        cloud_points = []
        recommended_epsilon = initial_epsilon
        recommended_epsilons = []
        for param in self._ordered_params.keys():
            coordinator.allocate(self.binary_search, (
                direction, param, simulator, center, target_loss, hypercube_loss, loss_tolerance,
                recommended_epsilon,
                iterations_remaining, stoptime))
            results = coordinator.collect()
            for param_value, param_key, ret_epsilon, incidental_points, iterations_used in results:
                cloud_points += incidental_points
                recommended_epsilons.append(ret_epsilon)
                cube_vector[param_key] = param_value
                iterations_remaining -= iterations_used

        results = coordinator.await_all()

        for param_value, param_key, recommended_epsilon, incidental_points, iterations_used in results:
            cloud_points += incidental_points
            recommended_epsilons.append(recommended_epsilon)
            cube_vector[param_key] = param_value
            iterations_remaining -= iterations_used
        return cube_vector, iterations_remaining, numpy.average(recommended_epsilons), cloud_points

    def binary_search(self, direction, param_key, simulator, initial_point, target_loss, hypercube_loss,
                      loss_tolerance,
                      initial_epsilon,
                      iterations_limit, stoptime):

        param_value = initial_point.copy()
        initial_norm=self._ordered_params[param_key].to_normalized(param_value[param_key])
        min_value = initial_norm
        max_value = initial_norm + initial_epsilon * direction.value
        current = max_value
        cloud_points = []
        iterations = 0
        #print("About to start loop")
        recommended_epsilon = None
        out_of_range=False
        while True:
            #print("true is true")
            if not self._ordered_params[param_key].is_valid_normalized(current):
                #print(current, "We have gone out of range")
                current = sorted(
                    (self._ordered_params[param_key].range_start, current, self._ordered_params[param_key].range_end))[
                    1]
                out_of_range=True
                max_value=current
            param_value[param_key] = self._ordered_params[param_key].from_normalized(current)

            ret = simulator(param_value, stoptime)
            iterations += 1
            if ret < target_loss:
                cloud_points.append(param_value.copy)
            if abs(ret - hypercube_loss) < loss_tolerance:
                #print(ret, "good enough")
                break
            if ret < hypercube_loss:

                if recommended_epsilon is None:  # expanding search
                    if out_of_range:  # The boundry is outside of the parameter spacd
                        recommended_epsilon = abs(initial_norm - current)
                        break
                    #print(ret, "doubling")
                    #print(min_value,max_value,(max_value - min_value),max_value+(max_value - min_value))
                    max_value += (max_value - min_value)
                    current = max_value
                    #print("Currently ",current)
                else:
                    #print(ret, "inclreasing by half")
                    min_value = current
                    current = (min_value + max_value) / 2

            if ret > hypercube_loss:
                if recommended_epsilon is None:
                    #print(ret, "range max set")
                    recommended_epsilon = abs(initial_norm - current)
                #print(ret, "shrinking by half")
                max_value = current
                current = (min_value + max_value) / 2
            if iterations_limit is not None and iterations > iterations_limit:
                #print("WTF, we should not exit here")
                break

        if recommended_epsilon is None:
            recommended_epsilon = initial_epsilon
        current = self._ordered_params[param_key].from_normalized(current)
        #print("Apparently we dont with loop")
        #print(current, param_key, recommended_epsilon, cloud_points, iterations)
        return current, param_key, recommended_epsilon, cloud_points, iterations

    def search_cube(self, simulator: Simulator, lower_bound, upper_bound, center, target_loss,
                    max_points=None, iterations=None, stop_time=None, coordinator=None):
        categorical = {}

        for key in self._categorical_params:
            categorical[key] = parameter.Categorical((center[key],))
        ordered = {}
        for key, value in self._ordered_params.items():
            ordered[key] = self._ordered_params[key].constrain(lower_bound[key], upper_bound[key])
        cloud_points = []
        if stop_time is not None:
            try:
                for calibration in _RectangularIterator(ordered, categorical):
                    if time.time() > stop_time:
                        break
                    coordinator.allocate(_eval, (simulator, calibration, stop_time))
                    results = coordinator.collect()
                    print(results)
                    for current, loss in results:
                        if loss is None:
                            continue
                        if loss < target_loss:
                            cloud_points.append(current)
            except exception.Timeout:
                pass
            except exception.EarlyTermination as e:
                e.result = cloud_points
                raise e
            except BaseException as e:
                raise exception.EarlyTermination(cloud_points, e)

        return cloud_points


def _eval(simulator, calibration, stop_time):
    return calibration, simulator(calibration, stop_time)


class _Direction(Enum):
    UPPER = +1
    LOWER = -1
