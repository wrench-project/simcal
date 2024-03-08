# from simulator import Simulator
# from _environment import Environment
#
#
# # deprecated
# # we originally conceptualized Handler as a way to call cleanup after loss but give the user
# # control of when to collect so as to not remove the directory before extracting data
# # But during this process we moved loss out of the simulator and into its own thing, and
# # replaced it with an extract function which moves all data off disk and into python
# # Therefore the original model still works without a handler, just call extract, then cleanup
# # Then return extract
# #
#
# class Handler(object):
#     def __init__(self, sim: Simulator, env: Environment):
#         self.sim = sim
#         self.env = env
#
#     def collect(self):
#         ret = self.sim.extract(self.env)
#         self.sim.cleanup(self.env)
#         return ret
