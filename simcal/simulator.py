from typing import Any

from simcal.environment import Environment


# from _handler import Handler


class Simulator(object):

    def __init__(self, coordinator=None):
        self.coordinator = coordinator

    def run(self, env, args) -> Any:
        raise NotImplementedError("Simulator.run(self,env,args) must be user defined")

    def __call__(self, args, env: Environment | None = None):  # handle async stuff
        if env is None:
            environment = _EnvManager(True, Environment())
        else:
            environment = _EnvManager(False, env)

        with environment:
            # self.setup(env)
            ret = self.run(environment.env, args)
            # handler = Handler(self, env)
            # ret=self.extract(env)
            # self.cleanup(env)
            return ret


class _EnvManager(object):
    def __init__(self, cleanup, env):
        self.cleanup = cleanup
        self.env = env

    def __enter__(self):
        return self.env

    def __exit__(self, exception_type, exception_value, exception_traceback):
        if (self.cleanup):
            self.env.cleanup()
