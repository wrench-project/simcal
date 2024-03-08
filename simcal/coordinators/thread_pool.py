import multiprocessing

from simcal.coordinators import Base


class ThreadPool(Base):
    def __init__(self, pool_size=None):
        super().__init__()
        self.managementLock = multiprocessing.Lock()
        self.pool_full = multiprocessing.Condition()
        self.awaiting_result = multiprocessing.Condition()
        if pool_size is None:
            pool_size = multiprocessing.cpu_count()
        self.pool = multiprocessing.Pool(processes=pool_size)
        self.pool_size = pool_size

    def allocate(self, func, args=None, kwds=None, fail=None):
        # not sure how async handles None arguments, hopefully it's fine, otherwise, use () and {}
        while len(self.handles) >= self.pool_size:
            with self.pool_full:
                self.pool_full.wait()

        handler = self.pool.apply_async(func, args, kwds, self._callback, fail)
        with self.managementLock:
            self.handles.append(handler)
        return handler

    def collect(self):

        ret = []
        with self.managementLock:
            for handler in self.ready:
                ret.append(handler.get())
            self.ready = []
        return ret

    def await_result(self):
        while len(self.ready) == 0:
            with self.awaiting_result:
                self.awaiting_result.wait()
        return self.collect()

    def await_all(self):
        while len(self.handles) > 0:
            with self.awaiting_result:
                self.awaiting_result.wait()
        return self.collect()

    def _callback(self, _):
        with self.managementLock:
            cache = [handler for handler in self.handles if self.ready.append(handler)]
            for handler in cache:
                self.ready.append(handler)
                self.handles.remove(handler)
        self.pool_full.notify()
        self.awaiting_result.notify()
