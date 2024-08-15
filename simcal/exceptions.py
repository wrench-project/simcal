class Base(RuntimeError):
    pass


class EarlyTermination(Base):  # used to return partial calibrations in case of error
    def __init__(self, result, exception):
        super().__init__("An Unexpected Exception was Thrown during Calibration, but the calibration may "
                         "be salvageable.\n\tReturned Result:%s" % (result,))
        self.result = result
        self.exception = exception


class SimulationFail(Base):  # used to return the particular parameters that caused an error
    def __init__(self, param, exception):
        super().__init__("A Simulation threw an exception. \n\tParameters given:%s" % (param,))
        self.param = param
        self.exception = exception


class InvalidSimulation(Base): # unused, left to simulation implementer to throw
    def __init__(self, msg, data=None, exception=None):
        super().__init__(msg)
        self.data = data
        self.exception = exception


class Timeout(Base):
    pass
