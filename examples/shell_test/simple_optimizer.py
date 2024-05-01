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

    def run(self, env, args):
        sleep(self.time)
        return pow(args[0] - 10, 2) + pow(args[1] - 4, 2) + pow(args[2] - 5, 2) + pow(args[3] - 3, 2)


class Scenario:
    def __init__(self, simulator):
        self.simulator = simulator

    def __call__(self, calibration, stoptime):
        unpacked = (calibration["a"], calibration["b"], calibration["c"], calibration["d"])

        print(calibration)
        ret = self.simulator(unpacked)
        print(ret)
        return ret


simulator = ExampleSimulator(0)
scenario1 = Scenario(simulator)

coordinator = sc.coordinators.ThreadPool(pool_size=1)  # Making a coordinator is optional, and only needed if you

evaluator = sc.evaluation.LossCloud()
evaluator.add_param("a", sc.parameter.Linear(0, 20).format("%.2f"))
evaluator.add_param("b", sc.parameter.Linear(0, 8).format("%.2f"))
evaluator.add_param("c", sc.parameter.Linear(0, 10).format("%.2f"))
evaluator.add_param("d", sc.parameter.Linear(0, 6).format("%.2f"))
#scenario1({'a': 10.5, 'b': 4, 'c': 5, 'd': 3}, 0)
print(evaluator.find_cloud(scenario1, {'a': 10, 'b': 4, 'c': 5, 'd': 3}, 0.1, 1, .001, 0.3, timelimit=60, coordinator=coordinator))
# def find_cloud(self, evaluate_point, parameter_vector, target_loss, hypercube_loss, loss_tolerance, initial_epsilon,
#                   max_points=None,
#                   iterations=None, timelimit=None, coordinator=None):
