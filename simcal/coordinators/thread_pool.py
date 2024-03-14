import concurrent.futures
import threading
from multiprocessing import cpu_count

from simcal.coordinators import Base


class ThreadPool(Base):
    def __init__(self, pool_size=None, timelimit=None):
        super().__init__(timelimit)
        self.managementLock = threading.Lock()
        self.pool_full = threading.Condition()
        self.awaiting_result = threading.Condition()
        if pool_size is None:
            pool_size = cpu_count()
        self.pool = concurrent.futures.ThreadPoolExecutor(max_workers=pool_size)
        self.pool_size = pool_size
        if timelimit:
            self._timer = threading.Timer(timelimit, self._timeout)
            self._timer.start()
        # TODO make threading alarm thing based on timelimit

    def allocate(self, func, args=(), kwds=None):
        if kwds is None:
            kwds = {}
        while len(self.handles) >= self.pool_size:
            with self.pool_full:
                self.pool_full.wait()
        handle = self.pool.submit(func, *args, **kwds)
        handle.add_done_callback(self._callback)
        with self.managementLock:
            self.handles.append(handle)
        return handle

    def collect(self):
        ret = []
        with self.managementLock:
            for handle in self.ready:
                ret.append(handle.result())
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

    def _fail(self, _):
        raise _

    def _callback(self, _):
        with self.managementLock:
            cache = [handle for handle in self.handles if handle.done()]
            for handle in cache:
                self.ready.append(handle)
                self.handles.remove(handle)
        with self.pool_full:
            self.pool_full.notify()
        with self.awaiting_result:
            self.awaiting_result.notify()

    def _timeout(self):
        self._callback(None)
        with self.managementLock:
            for handle in self.handles:
                handle.cancel()
            self.handles = []
        with self.pool_full:
            self.pool_full.notify()
        with self.awaiting_result:
            self.awaiting_result.notify()
