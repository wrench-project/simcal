class CalibratorParam(object):
    def __init__(self):
        self._internal_param = None
        self.formatter = None

    def exponential_range(self, start, end):
        self._internal_param = _ExponentialParam(start, end)
        return self

    def linear_range(self, start, end):
        self._internal_param = _LinearParam(start, end)
        return self

    def option_set(self, options):
        self._internal_param = _OptionParam(options)
        return self

    def format(self, formatter):
        self.formatter = formatter


class _InternalParam(object):
    pass


class _ExponentialParam(_InternalParam):
    def __init__(self, start, end):
        pass


class _LinearParam(_InternalParam):
    def __init__(self, start, end):
        pass


class _OptionParam(_InternalParam):
    def __init__(self, options):
        pass
