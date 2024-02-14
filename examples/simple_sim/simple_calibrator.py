#!/usr/bin/env python3
import simcal as sc
from groundtruth import ground_truth
from sklearn.metrics import mean_squared_error


class DataLoader:
    def __init__(self):
        # dont mind me, just "loading" my data
        self.data = []
        for x in (1.39904, 254441, 5.05656):
            for y in (1.1558, 3.384, 40395, 7.36):
                for z in (0.637, 2.281, 3.876, 5.459, 7.038):
                    for w in (0.448, 1.527, 2.587, 3.641, 4.693, 5.743):
                        self.data += ground_truth(x, y, z, w)

    def get_data(self):
        return self.data


class Simulator(sc.Simulator):

    def __init__(self, time=0):
        self.time = time

    def run(self, env, args):
        results = sc.bash("python3 simple_simulator.py", args, self.time)
        return float(results.split("\n")[-1])


class TestCalibration:
    def __init__(self, simulator):
        self.simulator = simulator

    def __call__(self, args):
        vargs = (args["a"], args["b"], args["c"], args["d"])
        res = []
        for x in (1.39904, 254441, 5.05656):
            for y in (1.1558, 3.384, 40395, 7.36):
                for z in (0.637, 2.281, 3.876, 5.459, 7.038):
                    for w in (0.448, 1.527, 2.587, 3.641, 4.693, 5.743):
                        res += simulator((x, y, z, w) + vargs)
        return res


data = DataLoader()

loss = mean_squared_error

simulator = Simulator()

calibrator = sc.GridCalibrator()  # tbd
calibrator.add_param("a", "").linear_range(0, 20)
calibrator.add_param("b", "").linear_range(0, 8)
calibrator.add_param("c", "").linear_range(0, 10)
calibrator.add_param("d", "").linear_range(0, 6)

test = TestCalibration(simulator)
calibrator.calibrate(test, loss, data.get_data())
