#!/usr/bin/env python3
import simcal as sc
from groundtruth import ground_truth
from sklearn.metrics import mean_squared_error as sklearn_mean_squared_error


class ExampleSimulator(sc.Simulator):

    def __init__(self, time=0):
        super().__init__()
        self.time = time

    def run(self, env, args):
        cmdargs = args[0] + args[1]
        std_out, std_err, exit_code = sc.bash("python3 simple_simulator.py", cmdargs, self.time)
        return float(std_out.split("\n")[-1])


class Scenario:
    def __init__(self, simulator, evaluation_scenarios):
        self.simulator = simulator
        self.evaluation_scenarios = evaluation_scenarios

    def __call__(self, calibration):
        calibration = (calibration["a"], calibration["b"], calibration["c"], calibration["d"])
        res = []
        # Run simulator for all known ground truth points
        for x in self.evaluation_scenarios:
            res += simulator((x, calibration))
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
calibrator.add_param("a",sc.parameter.LinearParam(0,20).format("%.2f"))
calibrator.add_param("b",sc.parameter.LinearParam(0,8).format("%.2f"))
calibrator.add_param("c",sc.parameter.LinearParam(0,10).format("%.2f"))
calibrator.add_param("d",sc.parameter.LinearParam(0,6).format("%.2f"))

calibrator.calibrate(scenario1, loss, data)
