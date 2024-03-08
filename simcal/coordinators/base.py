from simcal._environment import Environment
import multiprocessing


# coordinators will handle things like being Multithreaded, being MPI, etc
class Base(object):
    def __init__(self):
        super().__init__()
        self.handlers = []
        self.ready = []

    def allocate(self, func, args=None, kwds=None, fail=None):
        self.handlers.append(func(args, kwds))

    def collect(self):
        return [h for h in self.handlers]

    def await_result(self):
        return self.collect()

    def await_all(self):
        return self.collect()

    def env_instance(self):
        return Environment()

