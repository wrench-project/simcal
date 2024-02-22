#!/usr/bin/env python3
import simcal as sc
from groundtruth import ground_truth
from sklearn.metrics import mean_squared_error as sklearn_mean_squared_error
import json


class ExampleSimulator(sc.Simulator):
    def __init__(self, template, time=0):
        self.time = time
        self.template = template

    def run(self, env, args):
        env.tmp_dir(dir=".")
        json_file = env.tmp_file(dir=env.getCWD())
        json_file.write(json.JSONEncoder().encode(args[1]))
        json_file.flush()

        sc.bash("python3 simple_simulator.py", (args[0]) + (json_file.name, self.time))
        with open("results.txt", "r") as file:
            results = file.read()
        return float(results)


class Scenario:
    def __init__(self, simulator, evaluation_scenarios):
        super().__init__()
        self.simulator = simulator
        self.evaluation_scenarios = evaluation_scenarios

    def __call__(self, calibration):
        calibration = (calibration["a"], calibration["b"], calibration["c"], calibration["d"])
        res = []
        # Run simulator for all known ground truth points
        for trial in self.evaluation_scenarios:
            res += simulator((trial, calibration))
        return res


# make some fake evaluation scenarios for the example
evaluation_scenarios = []
for x in (1.39904, 254441, 5.05656):
    for y in (1.1558, 3.384, 40395, 7.36):
        for z in (0.637, 2.281, 3.876, 5.459, 7.038):
            for w in (0.448, 1.527, 2.587, 3.641, 4.693, 5.743):
                evaluation_scenarios += (x, y, z, w)

# get ground truth data the fake scenarios
data = []
for x in evaluation_scenarios:
    data += ground_truth(*x)

loss = sklearn_mean_squared_error

simulator = ExampleSimulator()
scenario1 = Scenario(simulator, evaluation_scenarios)

# prepare the calibrator and setup the arguments to calibrate with their ranges
calibrator = sc.GridCalibrator()  # tbd
calibrator.add_param("a").format("%.2f").linear_range(0, 20)
calibrator.add_param("b").format("%.2f").linear_range(0, 8)
calibrator.add_param("c").format("%.2f").linear_range(0, 10)
calibrator.add_param("d").format("%.2f").linear_range(0, 6)

calibrator.calibrate(scenario1, loss, data)
