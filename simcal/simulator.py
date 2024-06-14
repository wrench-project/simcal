from typing import Any

from simcal.environment import Environment


# from _handler import Handler


class Simulator(object):

    def __init__(self, coordinator=None):
        self.coordinator = coordinator

    def run(self, env: Environment, args: Any) -> float:
        raise NotImplementedError("Simulator.run(self,env,args) must be user defined")

    def __call__(self, args: Any, stoptime: int | float | None = None):  # handle async stuff

        env = Environment(stoptime=stoptime)
        with env:
            # self.setup(env)
            ret = self.run(env, args)
            # handler = Handler(self, env)
            # ret=self.extract(env)
            # self.cleanup(env)
            return ret
