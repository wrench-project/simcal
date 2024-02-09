from typing import Any

from _environment import Environment
# from _handler import Handler


class Simulator(object):
    # def setup(self, env):
    #    pass # maybe merge with run

    def run(self, env, args) -> Any:
        raise NotImplementedError("Simulator.run(self,env,args) must be user defined")

    # def extract(self, env): # Possibly merge with run
    #    raise NotImplementedError("Simulator.extract(self,env) must be user defined")

    # def cleanup(self, env):
    #   pass

    def __call__(self, args):  # handle async stuff
        env = Environment()
        # self.setup(env)
        ret = self.run(env, args)
        # handler = Handler(self, env)
        # ret=self.extract(env)
        # self.cleanup(env)
        env.cleanup()
        return ret
