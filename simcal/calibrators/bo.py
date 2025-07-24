
import time

import os

from deephyper.search.hps import CBO
from deephyper.evaluator import Evaluator
from deephyper.problem import HpProblem
import ConfigSpace as cs

import simcal.calibrators as sc
from simcal.simulator import Simulator
from simcal.parameters import Ordered, Categorical, Linear, Exponential

from deephyper.evaluator.callback import Callback
import numpy as np

class BOLoggerCallback(Callback):
    """Print information when jobs are completed by the ``Evaluator``.

    An example usage can be:

    >>> evaluator.create(method="ray", method_kwargs={..., "callbacks": [BOLoggerCallback()]})
    """

    def __init__(self):
        self._best_objective = None
        self._n_done = 0

    def on_done(self, job):
        self._n_done += 1
        # Test if multi objectives are received
        if np.ndim(job.result) > 0:
            if np.isreal(job.result).all():
                if self._best_objective is None:
                    self._best_objective = np.sum(job.result)
                else:
                    self._best_objective = max(np.sum(job.result), self._best_objective)

                print(
                    f"[{self._n_done:05d}] -- best sum(objective): {self._best_objective:.5f} -- received sum(objective): {np.sum(job.result):.5f}"
                )
            elif np.any(type(res) is str and "F" == res[0] for res in job.result):
                print(f"[{self._n_done:05d}] -- received failure: {job.result}")
        elif np.isreal(job.result):
            if self._best_objective is None:
                self._best_objective = job.result
            else:
                self._best_objective = max(job.result, self._best_objective)

            print(
                f"[{self._n_done:05d}] -- best objective: {self._best_objective:.5f} -- received objective: {job.result:.5f}"
            )
        elif type(job.result) is str and "F" == job.result[0]:
            print(f"[{self._n_done:05d}] -- received failure: {job.result}")

class BayesianOptimization(sc.Base):
    def __init__(self, seed=None):
        super().__init__()
        self.seed = seed
        self.problem = HpProblem()
        self.problem.space.seed(self.seed)
        self.results = None

    def add_param(self, name: str, parameter: Ordered | Categorical):
        """
        Method to add a to-be-calibrated parameter
        :param name: a user-defined parameter name
        :param parameter: the parameter
        :return: the calibrator
        :rtype simcal.calibrator.Base
        """
        if name in self._parameter_list.ordered_params or name in self._parameter_list.categorical_params:
            raise ValueError(f"Parameter {name} already exists")  # TODO: pick the correct error class
        if isinstance(parameter, Linear):
            # TODO: Float parameter only, add Integer?
            self._parameter_list.ordered_params[name] = cs.Float(name, (parameter.start, parameter.end), distribution=cs.Uniform(), log=False)
            # self._ordered_params[name] = cs.Integer(name, (parameter.start, parameter.end), distribution=cs.Uniform(), log=False)
        elif isinstance(parameter, Exponential):
            self._parameter_list.ordered_params[name] = cs.Integer(name, (parameter.start, parameter.end), distribution=cs.Uniform(), log=True)
        else:
            self._parameter_list.categorical_params[name] = cs.Categorical(name, parameter.get_categories(), ordered=False)
        return self

    def calibrate(self, simulator: Simulator, early_stopping_loss=None, iterations=-1, timelimit=None, coordinator=None):
        if self._parameter_list.ordered_params == [] and self._parameter_list.categorical_params == []:
            raise ValueError(f"Missing hyperparameters")

        self.problem.add_hyperparameters(list(self._parameter_list.ordered_params.values()) + list(self._parameter_list.categorical_params.values()))

        print(self.problem)

        if coordinator is None:
            from multiprocessing import cpu_count
            from deephyper.evaluator.callback import SearchEarlyStopping

            num_cpus = cpu_count()
            callbacks = []
            if early_stopping_loss is not None:
                # WARNING: early_stopping_loss is a number of iterations here
                callbacks.append(SearchEarlyStopping(patience=early_stopping_loss))

            #Use sub-process as back-end, to use ThreadPool -> "thread" 
            coordinator = Evaluator.create(
                simulator.run,
                method="thread",
                method_kwargs={
                    "num_workers": num_cpus,
                    "callbacks": callbacks
                },
            )

        cbo = CBO(
            problem=self.problem,
            evaluator=coordinator,
            random_state=self.seed,
            n_jobs=-1,
            # surrogate_model="DUMMY",
            log_dir=os.getcwd()
        )

        self.results = cbo.search(max_evals=iterations, timeout=timelimit)

        i_max = self.results.objective.argmax()
        data_best = self.results.iloc[i_max].to_dict()
        best_parameters = self.results.loc[i_max, self.results.columns.str.startswith("p:")].to_dict()
        # Deephyper add p: in front of each paramater, we remove 'p:' for compatibilty
        best_parameters = {k[2:]: v for k,v in best_parameters.items()}
        return best_parameters, abs(data_best["objective"])
