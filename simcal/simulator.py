from typing import Any

from simcal._environment import Environment


# from _handler import Handler


class Simulator(object):

    def __init__(self, coordinator=None):
        self.coordinator = coordinator

    def run(self, env, args) -> Any:
        raise NotImplementedError("Simulator.run(self,env,args) must be user defined")

    def __call__(self, args, env: Environment | None = None):  # handle async stuff
        if env is None:
            environment = Environment()
        else:
            environment = env
        # self.setup(env)
        ret = self.run(environment, args)
        # handler = Handler(self, env)
        # ret=self.extract(env)
        # self.cleanup(env)
        if env is None:
            environment.cleanup()
        return ret
