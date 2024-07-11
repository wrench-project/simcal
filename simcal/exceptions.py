class Base(RuntimeError):
    pass


class EarlyTermination(Base):
    def __init__(self, result, exception):
        super().__init__("An Unexpected Exception was Thrown during Calibration, but the calibration may "
                         "be salvageable.\n\tReturned Result:%s" % (result,))
        self.result = result
        self.exception = exception


class Timeout(Base):
    pass
