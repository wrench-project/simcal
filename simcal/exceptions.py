class Base(RuntimeError):
    pass


class EarlyTermination(Base):
    def __init__(self, result, exception):
        super().__init__("A Calibrator Ended Early.  Possible due to a timelimit being reached, "
                         "or possibly because of an error in the simulator.\n\tReturned Result%s" % (result,))
        self.result = result
        self.exception = exception


class Timeout(Base):
    pass
