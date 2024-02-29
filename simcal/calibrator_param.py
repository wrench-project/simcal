import math

from simcal._formatted_value import _FormattedValue
from simcal.utility_functions import safe_exp2


# class CalibratorParam(object):
#     def __init__(self):
#         self._internal_param = None
#         self.formatter = None
#
#     def exponential_range(self, start, end):
#         self._internal_param = ExponentialParam(start, end)
#         return self
#
#     def format(self, formatter):
#         self.formatter = formatter
#         return self
#
#     def linear_range(self, start, end):
#         self._internal_param = LinearParam(start, end)
#         return self
#
#     def ordinal(self, options):
#         self._internal_param = OrdinalParam(options)
#         return self
#
#     def categorical(self, categories):
#         self._internal_param = CategoricalParam(categories)
#         return self
#
#     def custom(self, custom_param):
#         self._internal_param = custom_param
#         return self
#
#     def getInternal(self):
#         return self._internal_param

class CalibratorParam(object):
    def __init__(self):
        self.formatter = None

    def format(self, formatter):
        self.formatter = formatter
        return self


class OrderedParam(CalibratorParam):
    def __init__(self, range_start, range_end, from_normalize_override=None, to_normalize_override=None):
        super().__init__()
        self.range_start = range_start
        self.range_end = range_end
        self.from_normalize_override = from_normalize_override
        self.to_normalize_override = to_normalize_override

    def from_normalized(self, x: float):
        if self.from_normalize_override:
            value = self.from_normalize_override(self, x)
            return value
        raise NotImplementedError(
            self.__class__.__name__ + " does not define from_normalized(self,x) and does not have an override")

    def to_normalized(self, x: float | _FormattedValue):
        if self.to_normalize_override:
            return self.to_normalize_override(self, x)
        raise NotImplementedError(
            self.__class__.__name__ + " does not define to_normalized(self,x) and does not have an override")


class ExponentialParam(OrderedParam):
    # start and end are in exponent terms
    def __init__(self, start, end, from_normalize_override=None, to_normalize_override=None):
        super().__init__(0, 1)
        self.start = start
        self.end = end

    def from_normalized(self, x: float) -> float | _FormattedValue:
        if self.from_normalize_override:
            return self.from_normalize_override(self, x)
        x_normal = (x - self.range_start) / (self.range_end - self.range_start)
        value = safe_exp2(x_normal * (self.end - self.start) + self.start)
        if self.formatter:
            return _FormattedValue(self.formatter, value)
        return value

    def to_normalized(self, x: float):
        if self.to_normalize_override:
            return self.to_normalize_override(self, x)
        x_normal = (math.log2(x) - self.start) / (self.end - self.start)
        return x_normal * (self.range_end - self.range_start) + self.range_start


class LinearParam(OrderedParam):  # requires testing
    def __init__(self, start, end):
        super().__init__(0, 1)
        self.start = start
        self.end = end

    def from_normalized(self, x: float) -> float | _FormattedValue:
        if self.from_normalize_override:
            return self.from_normalize_override(self, x)
        x_normal = (x - self.range_start) / (self.range_end - self.range_start)
        value = x_normal * (self.end - self.start) + self.start
        if self.formatter:
            return _FormattedValue(self.formatter, value)
        return value

    def to_normalized(self, x: float):
        if self.to_normalize_override:
            return self.to_normalize_override(self, x)
        x_normal = (x - self.start) / (self.end - self.start)
        return x_normal * (self.range_end - self.range_start) + self.range_start


class OrdinalParam(OrderedParam):
    def __init__(self, options):
        super().__init__(0, 1)
        self.options = options

    def from_normalized(self, x: float):
        if self.from_normalize_override:
            return self.from_normalize_override(self, x)
        x_normal = (x - self.range_start) / (self.range_end - self.range_start)
        idx = int(x_normal * len(self.options))
        if idx >= len(self.options):
            idx = len(self.options) - 1
        value = self.options[idx]
        if self.formatter:
            return _FormattedValue(self.formatter, value)
        return value

    def to_normalized(self, x: any):
        if self.to_normalize_override:
            return self.to_normalize_override(self, x)
        idx = self.options.index(x)
        x_normal = idx / len(self.options)
        return x_normal * (self.range_end - self.range_start) + self.range_start


class CategoricalParam(CalibratorParam):
    def __init__(self, categories):
        super().__init__()
        self.categories = categories

    def get_categories(self):
        return self.categories
