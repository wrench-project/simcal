import random
from itertools import count
from time import time

import simcal.calibrators as sc
import simcal.exceptions as exception
import simcal.simulator as Simulator
from simcal.parameters import *
import simcal.coordinators.base as Coordinator

def _eval(simulator: Simulator, calibration, stoptime):
    try:
        return calibration, simulator(calibration, stoptime)
    except exception.Timeout:
        raise
    except Exception as e:
        raise exception.SimulationFail(calibration, e)


# Base estimators can be
# "GP" for Gradient Process Regressor
# "RF" for Random Forrest Regresor
# "ET" for Extra Trees Regressor or
# "GBRT" for Gradient Boosting Quantile Regressor trees
class ScikitOptimizer(sc.Base):
    def __init__(self,
                 generation_size,
                 breeders,
                 crossover_rate,
                 mutation_rate,
                 fitness_noise=0,
                 annealing=None,
                 seed=None, elites=0):
        super().__init__()
        self.generation_size=max(generation_size,elites,breeders)
        self.elites=elites
        self.mutation=mutation_rate
        self.crossover=crossover_rate
        self.breeders=breeders
        self.seed = seed
        if fitness_noise == 0:
            self.fitness_noise = lambda x:x
        elif isinstance(fitness_noise,float):
            self.fitness_noise = lambda x: x*(1-random()*fitness_noise)
        if annealing is None:
            self.annealing=lambda x : 1
        elif annealing is True:
            self.annealing = lambda x : 1.01-x

    def breed(self,x,y):
        return x
    def mutate(self,x):
        return x
    def calibrate(self, simulator: Simulator, early_stopping_loss: float | int | None = None,
                  iterations: int | None = None, timelimit: float | int | None = None,
                  coordinator: Coordinator.Base | None = None) -> tuple[dict[str, Value | float | int], float]:
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
        generation=[]
        breeders=[]
        current_ret=None
        try:
            start_time = time()
            for itteration in itr:
                if time() > stoptime:
                    break

                progress_t=1
                progress_i=1
                if timelimit:
                    progress_t=(stoptime-start_time)/timelimit
                if iterations:
                    progress_i=itteration/iterations
                progress=self.annealing(max(0,min(progress_t,progress_i)))
                if not generation:
                    calibration = {}
                    for key in self._ordered_params:
                        param = self._ordered_params[key]
                        calibration[key] = param.from_normalized(random.uniform(param.range_start, param.range_end))

                    for key in self._categorical_params:
                        calibration[key] = random.choice(self._categorical_params[key].get_categories())
                    generation.append(calibration)
                else:
                    generation=[]
                    #TODO breed

                # for key in self._ordered_params:
                #     param = self._ordered_params[key]
                #     calibration[key] = param.from_normalized(random.uniform(param.range_start, param.range_end))
                #
                # for key in self._categorical_params:
                #     calibration[key] = random.choice(self._categorical_params[key].get_categories())
                for pop in generation:
                    coordinator.allocate(_eval, (simulator, pop, stoptime))
                results = coordinator.await_all()
                new_gen=[]
                for current, loss in results:
                    if loss is None:
                        continue
                    if loss<current_ret[1]:
                        current_ret=(current,loss)
                    new_gen.append((current,loss,self.fitness_noise(loss)))
                breeders = sorted(new_gen,key=lambda x: x[2])[:max(self.breeders,self.elites)]


            results = coordinator.await_all()
            for current, loss, tell in results:
                if loss is None:
                    continue
                if loss < current_ret[1]:
                    current_ret = (current, loss)
        #TODO Everything bellow here
        except exception.Timeout:
            # print("Random had to catch a timeout")
            results = opt.get_result()
            results.x = self.to_regular_params(parameters, results.x)
            return current_ret
        except exception.EarlyTermination as e:
            ebest, eloss = e.result
            if eloss is None:
                results = opt.get_result()
                results.x = self.to_regular_params(parameters, results.x)
                if results.fun < eloss:
                    e.result = (results.x, results.fun)
            raise e
        except BaseException as e:
            results = opt.get_result()
            results.x = self.to_regular_params(parameters, results.x)
            raise exception.EarlyTermination((results.x, results.fun), e)

        results = opt.get_result()
        results.x = self.to_regular_params(parameters, results.x)
        return results.x, results.fun

