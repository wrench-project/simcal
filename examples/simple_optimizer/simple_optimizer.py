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
        print(args)
        sleep(self.time)
        ret = pow(args["a"] - 10, 2) + pow(args["b"] - 4, 2) + pow(args["c"] - 5, 2) + pow(args["d"] - 3, 2)
        print(ret)
        return ret


simulator = ExampleSimulator(10)

# prepare the calibrator and setup the arguments to calibrate with their ranges
# calibrator = sc.calibrators.Grid()
# calibrator = sc.calibrators.Random()
#calibrator = sc.calibrators.GradientDescent(0.1, 1)
calibrator = sc.calibrators.GradientDescent(0.1, 1)

calibrator.add_param("a", sc.parameter.Linear(0, 20).format("%.2f"))
calibrator.add_param("b", sc.parameter.Linear(0, 8).format("%.2f"))
calibrator.add_param("c", sc.parameter.Linear(0, 10).format("%.2f"))
calibrator.add_param("d", sc.parameter.Linear(0, 6).format("%.2f"))

coordinator = sc.coordinators.ThreadPool(pool_size=4)  # Making a coordinator is optional, and only needed if you
# wish to run multiple simulations at once, possibly using multiple cpu cores or multiple compute nodes
start = time()
calibration, loss = calibrator.calibrate(simulator, timelimit=60, coordinator=coordinator)
print("final calibration")
print(calibration)
print(loss)
print(time() - start)
# Ideal A=10, B=4, C=5, D=3
