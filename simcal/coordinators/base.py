from simcal.environment import Environment


# coordinators will handle things like being Multithreaded, being MPI, etc
class Base(object):
    def __init__(self):  # , timelimit=None):
        super().__init__()
        self.handles = []
        self.ready = []
        # self.timelimit = timelimit

    def allocate(self, func, args=(), kwds=None):
        if kwds is None:
            kwds = {}
        self.handles.append(func(*args, **kwds))

    def collect(self):
        return [h for h in self.handles]

    def await_result(self):
        return self.collect()

    def await_all(self):
        return self.collect()

    def env_instance(self):
        return Environment()
