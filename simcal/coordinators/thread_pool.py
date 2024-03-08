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
        while len(self.handlers) >= self.pool_size:
            self.pool_full.wait()

        handler = self.pool.apply_async(self, func, args, kwds, self._callback, fail)
        with self.managementLock:
            self.handlers.append(handler)
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
            self.awaiting_result.wait()
        return self.collect()

    def await_all(self):
        while len(self.handlers) > 0:
            self.awaiting_result.wait()
        return self.collect()

    def _callback(self, _):
        with self.managementLock:
            cache = [handler for handler in self.handlers if self.ready.append(handler)]
            for handler in cache:
                self.ready.append(handler)
                self.handlers.remove(handler)
        self.pool_full.notify()
        self.awaiting_result.notify()