import concurrent.futures
import threading
from functools import wraps
from multiprocessing import cpu_count

from simcal.coordinators import Base


class ThreadPool(Base):
    def __init__(self, pool_size=None):  # hard_timelimit=None
        super().__init__()  # hard_timelimit)
        self.managementLock = threading.Lock()
        self.pool_full = threading.Condition()
        self.awaiting_result = threading.Condition()
        if pool_size is None:
            pool_size = cpu_count()
        self.pool = concurrent.futures.ThreadPoolExecutor(max_workers=pool_size)
        self.pool_size = pool_size
        # if hard_timelimit:
        #     self._timer = threading.Timer(hard_timelimit, self._timeout)
        #     self._timer.start()

    # def addTimeout(self,timelimit):
    #     self._timer = threading.Timer(timelimit, self._timeout)
    #     self._timer.start()
    def allocate(self, func, args=(), kwds=None):
        if kwds is None:
            kwds = {}
        while True:
            with self.managementLock:
                if len(self.handles) < self.pool_size:
                    break
            with self.pool_full:
                self.pool_full.wait()
        with self.managementLock:
            handle = self.pool.submit(self._thread_wrapper, func, args, kwds)
            handle.add_done_callback(self._callback)
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


    def _thread_wrapper(self, func, args, kwargs):
        with self.managementLock:
            pass
        return func(*args, **kwargs)

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

    # def _timeout(self):
    #     self._callback(None)
    #     with self.managementLock:
    #         for handle in self.handles:
    #             handle.cancel()
    #             kill_child_threads()
    #         kill_child_processes()
    #         self.handles = []
    #         # TODO allow graceful canceling of gradient descent
    #     with self.pool_full:
    #         self.pool_full.notify()
    #     with self.awaiting_result:
    #         self.awaiting_result.notify()

# class TimeoutException(BaseException):
#     def __init__(self):
#         super().__init__("Timeout Exception")


# def kill_child_threads():
#     for thread in threading.enumerate():
#         if isinstance(thread, threading._MainThread):
#             continue
#         try:
#             raise_exception_in_thread(thread, TimeoutException)
#         except TimeoutException:
#             pass  # resist ourselves being canceled
#
#
# def kill_child_processes():
#     parent_id = os.getpid()
#     if os.name == 'nt':
#         ps_command = subprocess.Popen("wmic process where (ParentProcessId=%d) get ProcessId" % parent_id, shell=True,
#                                       stdout=subprocess.PIPE)
#     else:
#         ps_command = subprocess.Popen("ps -o pid --ppid %d" % parent_id, shell=True, stdout=subprocess.PIPE)
#     ps_output = ps_command.stdout.read().decode()
#     retcode = ps_command.wait()
#     for pid_str in ps_output.strip().split("\n")[1:-1]:
#         os.kill(int(pid_str), signal.SIGTERM)
#
#
# def raise_exception_in_thread(t: threading.Thread, e: BaseException):
#     ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(t.ident), ctypes.py_object(e))
