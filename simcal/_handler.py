from simulator import Simulator
from _environment import Environment

#depricated
class Handler (object):
    def __init__(self, sim: Simulator, env: Environment):
        self.sim = sim
        self.env = env

    def collect(self):
        ret = self.sim.extract(self.env)
        self.sim.cleanup(self.env)
        return ret
