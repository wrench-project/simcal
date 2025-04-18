#!/usr/bin/env python3
from time import time, sleep

import simcal as sc

#refString = "The Only Thing We Have to Fear is ValueError".split(" ")
refString = "Who's on first?".split(" ")

class ExampleSimulator(sc.Simulator):

    def __init__(self, time):
        super().__init__()
        self.time = time

    def run(self, env, args):
        #print(args)
        sleep(self.time)
        ret = 0
        log = "Sentence: "

        for i, _ in enumerate(refString):
            word = args["word" + str(i + 1)]
            log += word + " "
            ret += abs(refString.index(word) - i)
        log += ", answer:" + str(args["answer"])
        log += ", x:" + str(args["x"])
        answer = int(args["answer"])
        ret += abs(answer - 42)
        x = float(args["x"])
        ret += abs(x * x - 9)
        log += ", loss:" + str(ret)
        print(log)
        return ret


simulator = ExampleSimulator(0)
coordinator = None#sc.coordinators.ThreadPool(pool_size=1)  # Making a coordinator is optional, and only needed if you

# scenario1({'a': 10, 'b': 4, 'c': 5, 'd': 3}, 0)
for calibrator in [
    sc.calibrators.Grid(),
    #sc.calibrators.Random(),
    #sc.calibrators.ScikitOptimizer(1000),
    #sc.calibrators.GradientDescent(1, 1)
]:
    for i, _ in enumerate(refString):
        calibrator.add_param("word" + str(i + 1), sc.parameter.Categorical(list(set(refString))))
    calibrator.add_param("answer", sc.parameter.Ordinal([0, 1, 13, 21, 39, 42, 69, 72, 9000]).format("%d"))
    calibrator.add_param("x", sc.parameter.Linear(0, 10).format("%.2f"))
    calibration, loss = calibrator.calibrate(simulator, timelimit=1200, coordinator=coordinator)
    print("final calibration")
    print(calibration)
    print(loss)
