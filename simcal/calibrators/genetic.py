import random
from itertools import count
from time import time
from typing import Callable

from simcal.calibrators.base import Base as BaseCalibrator
import simcal.coordinators.base as Coordinator
import simcal.exceptions as exception
import simcal.simulator as Simulator
from simcal.parameters import *


def _eval(simulator: Simulator, calibration, stoptime):
    try:
        return calibration, simulator(calibration, stoptime)
    except exception.Timeout:
        raise
    except Exception as e:
        raise exception.SimulationFail(calibration, e)


class GeneticAlgorithm(BaseCalibrator):
    def __init__(self,
                 generation_size,
                 breeders,
                 crossover_rate,
                 mutation_rate,
                 fitness_noise: int | float | Callable = 0,
                 annealing=None,
                 seed=None, elites=0):
        super().__init__()
        self.generation_size = max(generation_size, elites, breeders / 2)
        self.elites = min(elites, breeders)
        self.mutation = mutation_rate
        self.crossover = crossover_rate
        self.breeders = breeders
        self.seed = seed
        if fitness_noise == 0:
            self.fitness_noise = lambda x: x
        elif isinstance(fitness_noise, float | int):
            self.fitness_noise = lambda x: x * (1 - random.random() * fitness_noise)
        else:
            self.fitness_noise = fitness_noise

        if annealing is None:
            self.annealing = lambda x: 1
        elif annealing is True:
            self.annealing = lambda x: 1.01 - x
        else:
            self.annealing = annealing

    def breed(self, x, y):
        c = {}
        for key in x:
            if random.random() < self.crossover:
                c[key] = y[key]
            else:
                c[key] = x[key]
        return c

    def mutate(self, x):
        for key in self._categorical_params:
            if random.random() < self.mutation:
                x[key] = random.choice(self._categorical_params[key].get_categories())
        for key in self._categorical_params:
            param = self._categorical_params[key]
            intermediate = param.to_normalized(x[key])
            intermediate += (random.random() - .5) * self.mutation
            intermediate = min(param.range_end, max(param.range_start, intermediate))
            x[key] = param.from_normalized(intermediate)
        return x

    def calibrate(self, simulator: Simulator, early_stopping_loss: float | int | None = None,
                  iterations: int | None = None, timelimit: float | int | None = None,
                  coordinator: Coordinator.Base | None = None) -> tuple[dict[str, Value | float | int], float]:
        if coordinator is None:
            from simcal.coordinators import Base as Coordinator
            coordinator = Coordinator()
        if timelimit is None:
            stoptime = float('inf')
        else:
            stoptime = time() + timelimit
        if iterations is None:
            itr = count(start=0, step=1)
        else:
            itr = range(0, iterations)
        generation = []
        breeders = []
        current_ret = None
        try:
            start_time = time()
            for itteration in itr:
                if time() > stoptime:
                    break
                progress_t = 1
                progress_i = 1
                if timelimit:
                    progress_t = (stoptime - start_time) / timelimit
                if iterations:
                    progress_i = itteration / iterations
                progress = self.annealing(max(0, min(progress_t, progress_i)))
                if not generation:
                    for i in range(self.generation_size):
                        calibration = {}
                        for key in self._ordered_params:
                            param = self._ordered_params[key]
                            calibration[key] = param.from_normalized(random.uniform(param.range_start, param.range_end))

                        for key in self._categorical_params:
                            calibration[key] = random.choice(self._categorical_params[key].get_categories())
                        generation.append(calibration)
                else:
                    generation = sorted(breeders, key=lambda x: x[1])[:self.elites]
                    print(breeders)
                    for i in range(self.generation_size - len(generation)):
                        a, b = random.sample(breeders, 2)
                        c = self.breed(a[0], b[0])
                        c = self.mutate(c)
                        generation.append(c)
                # for key in self._ordered_params:
                #     param = self._ordered_params[key]
                #     calibration[key] = param.from_normalized(random.uniform(param.range_start, param.range_end))
                #
                # for key in self._categorical_params:
                #     calibration[key] = random.choice(self._categorical_params[key].get_categories())
                for pop in generation:
                    coordinator.allocate(_eval, (simulator, pop, stoptime))
                results = coordinator.await_all()
                new_gen = []
                for current, loss in results:
                    if loss is None:
                        continue
                    if current_ret is None or loss < current_ret[1]:
                        self.mark_calibration((current, loss))
                        current_ret = (current, loss)
                    new_gen.append((current, loss, self.fitness_noise(loss)))
                breeders = sorted(new_gen, key=lambda x: x[2])[:max(self.breeders, self.elites)]
            results = coordinator.await_all()
            for current, loss, tell in results:
                if loss is None:
                    continue
                if loss < current_ret[1]:
                    self.mark_calibration((current, loss))
                    current_ret = (current, loss)

        # TODO Everything bellow here

        except exception.Timeout:
            return current_ret
        except exception.EarlyTermination as e:
            ebest, eloss = e.result
            if eloss is None:
                if current_ret[1] < eloss:
                    e.result = current_ret
            raise e
        except BaseException as e:
            raise exception.EarlyTermination(current_ret, e)
        for current, loss, tell in results:
            if loss is None:
                continue
            if loss < current_ret[1]:
                self.mark_calibration((current, loss))
                current_ret = (current, loss)
        return current_ret
