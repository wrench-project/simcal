class CalibratorParam(object):
    def __init__(self):
        self._internal_param = None
        self.formatter = None

    def exponential_range(self, start, end):
        self._internal_param = ExponentialParam(start, end)
        return self

    def format(self, formatter):
        self.formatter = formatter

    def linear_range(self, start, end):
        self._internal_param = LinearParam(start, end)
        return self

    def ordinal(self, options):
        self._internal_param = OrdinalParam(options)
        return self

    def catigorical(self, catagories):
        self._internal_param = CategoricalParam(catagories)
        return self


class _FormatedValue:
    def __init__(self, formatter, value):
        self.formatter = formatter
        self.value = value

    def _apply_format(self, x) -> str:
        return format(self.formatter, x)

    def __str__(self):
        return self._apply_format(self.value)


class _InternalParam(object):
    def __init__(self):
        self.formatter = None

    def format(self, formatter):
        self.formatter = formatter


class OrderedParam(_InternalParam):
    def __init__(self, range_start, range_end, from_normalize_override=None, to_normalize_override=None):
        super().__init__()
        self.range_start = range_start
        self.range_end = range_end
        self.from_normalize_override = from_normalize_override
        self.to_normalize_override = to_normalize_override

    def from_normalized(self, x: float):
        if self.from_normalize_override:
            value = self.from_normalize_override(self, x)
            if self.formatter:
                return _FormatedValue(self.formatter, value)
            return value
        raise NotImplementedError(self.__class__.__name__ + " does not define from_normalized(self,x)")

    def to_normalized(self, x):
        if self.to_normalize_override:
            return self.to_normalize_override(self, x)
        raise NotImplementedError(self.__class__.__name__ + " does not define to_normalized(self,x)")


class ExponentialParam(OrderedParam):
    def __init__(self, start, end, from_normalize_override=None, to_normalize_override=None):
        super().__init__(0, 1)
        self.start = start
        self.end = end

    def from_normalized(self, x: float):
        if self.from_normalize_override:
            return self.from_normalize_override(self, x)

    def to_normalized(self, x: float):
        if self.from_normalize_override:
            return self.from_normalize_override(self, x)


class LinearParam(OrderedParam):  # requires testing
    def __init__(self, start, end):
        super().__init__(0, 1)
        self.start = start
        self.end = end

    def from_normalized(self, x: float) -> float | _FormatedValue:
        if self.from_normalize_override:
            return self.from_normalize_override(self, x)
        x_normal = (x - self.range_start) / (self.range_end - self.range_start)
        value = x_normal * (self.end - self.start) + self.start
        if self.formatter:
            return _FormatedValue(self.formatter, value)
        return value

    def to_normalized(self, x: float):
        if self.from_normalize_override:
            return self.from_normalize_override(self, x)
        x_normal = (x - self.start) / (self.end - self.start)
        return x_normal * (self.range_end - self.range_start) + self.range_start


class OrdinalParam(OrderedParam):
    def __init__(self, options):
        super().__init__(0, 1)
        self.option = options

    def from_normalized(self, x: float):
        if self.from_normalize_override:
            return self.from_normalize_override(self, x)

    def to_normalized(self, x: any):
        if self.from_normalize_override:
            return self.from_normalize_override(self, x)


class CategoricalParam(_InternalParam):
    def __init__(self, catagories):
        super().__init__()
        self.catagories = catagories

    def get_catagories(self):
        return self.catagories
