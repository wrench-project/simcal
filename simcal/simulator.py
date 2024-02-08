from _environment import Environment
from _handler import Handler


class Simulator(object):
    def setup(self, env):
        raise NotImplementedError("Simulator.setup(self,env) must be user defined")

    def run(self, env, args):
        raise NotImplementedError("Simulator.run(self,env,args) must be user defined")

    def extract(self, env):
        raise NotImplementedError("Simulator.extract(self,env) must be user defined")

    def cleanup(self, env):
        env.cleanup()

    def __call__(self, args):  # handle async stuff
        env = Environment()
        self.setup(env)
        self.run(env, args)
        #handler = Handler(self, env)
        ret=self.extract(env)
        self.cleanup(env)
        return ret
