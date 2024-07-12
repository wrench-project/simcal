#!/usr/bin/env python3
import os
from pathlib import Path
from time import time, sleep

import simcal as sc

simple_sim = Path(os.path.dirname(os.path.realpath(__file__)))  # Get path to THIS folder where the simulator lives


class ExampleSimulator(sc.Simulator):

    def __init__(self, time):
        super().__init__()
        self.time = time

    def run(self, args, env = {}):
        # Here args is a deephyper.evaluator._job.RunningJob
        # Cf https://deephyper.readthedocs.io/en/latest/_modules/deephyper/evaluator/_job.html#RunningJob
        print(args.parameters)
        sleep(self.time)
        ret = pow(args.parameters["a"] - 10, 2) + pow(args.parameters["b"] - 4, 2) + pow(args.parameters["c"] - 5, 2) + pow(args.parameters["d"] - 3, 2)
        # print(ret)
        # DeepHyper always maximize the objective function
        return -ret

simulator = ExampleSimulator(2)

# prepare the calibrator and setup the arguments to calibrate with their ranges
calibrator = sc.calibrators.BayesianOptimization(seed=0)

calibrator.add_param("a", sc.parameter.Linear(0, 20).format("%.2f"))
calibrator.add_param("b", sc.parameter.Linear(0, 8).format("%.2f"))
calibrator.add_param("c", sc.parameter.Linear(0, 10).format("%.2f"))
calibrator.add_param("d", sc.parameter.Linear(0, 6).format("%.2f"))
calibrator.add_param("e", sc.parameter.Exponential(1, 6).format("%.2f"))

# wish to run multiple simulations at once, possibly using multiple cpu cores or multiple compute nodes
start = time()
calibration, loss = calibrator.calibrate(simulator, iterations=50, early_stopping_loss=25, timelimit=None)
print("final calibration")
print(f"best parameters = {calibration}")
print(f"loss = {loss}")
print(f"Execution time: {time() - start} seconds")
# Ideal A=10, B=4, C=5, D=3
