class EarlyTermination(RuntimeError):
    def __init__(self, result, exception):
        super().__init__("A Calibrator Ended Early.  Possible due to a timelimit being reached, "
                         "or possibly because of an error in the simulator.\n\tReturned Result%s" % (result,))
        self.result = result
        self.exception = exception


class Timeout(RuntimeError):
    pass


class SoftTimeout(Timeout):
    def __init__(self):
        super().__init__("Soft Timelimit reached")


class HardTimeout(Timeout):
    def __init__(self):
        super().__init__("Hard Timelimit reached")
