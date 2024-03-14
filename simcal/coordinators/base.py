from simcal._environment import Environment


# coordinators will handle things like being Multithreaded, being MPI, etc
class Base(object):
    def __init__(self):
        super().__init__()
        self.handles = []
        self.ready = []

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
