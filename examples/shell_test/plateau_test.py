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
        a = args['a']
        b = args['b']
        c = args['c']
        # args['d'] is intentionaly not used

        ret = 5
        if (a < 12):
            ret += (a - 10) * (a - 10)
        else:
            ret += 4

        if (b > 4):
            ret += (b - 4) * (b - 4)
        else:
            ret += 0

        if (c > 5):
            ret += (c - 5) * (c - 5)
        else:
            ret += 5-c

        return ret


simulator = ExampleSimulator(0)

coordinator = sc.coordinators.ThreadPool(pool_size=1)  # Making a coordinator is optional, and only needed if you

evaluator = sc.evaluation.LossCloud()
evaluator.add_param("a", sc.parameter.Linear(0, 20).format("%.2f"))
evaluator.add_param("b", sc.parameter.Linear(0, 8).format("%.2f"))
evaluator.add_param("c", sc.parameter.Linear(0, 10).format("%.2f"))
evaluator.add_param("d", sc.parameter.Linear(0, 6).format("%.2f"))
# scenario1({'a': 10, 'b': 4, 'c': 5, 'd': 3}, 0)
print(evaluator.find_cloud(simulator, {'a': 13, 'b': 4, 'c': 5, 'd': 3},
                           7, 10, .1, 0.3,
                           timelimit=60, output_dir=""))  # ,output_dir="./output"))  # , coordinator=coordinator))
# def find_cloud(self, evaluate_point, parameter_vector, target_loss, hypercube_loss, loss_tolerance, initial_epsilon,
#                   max_points=None,
#                   iterations=None, timelimit=None, coordinator=None):
print("finished")