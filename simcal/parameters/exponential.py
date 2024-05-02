import math

from simcal.parameters.value import Value
from simcal.parameters.ordered import Ordered
from simcal.utility_functions import safe_exp2


class Exponential(Ordered):
    # start and end are in exponent terms
    def __init__(self, start, end, from_normalize_override=None, to_normalize_override=None):
        super().__init__(0, 1)
        self.start = start
        self.end = end

    def is_valid_value(self, x: float | Value) -> bool:
        return self.start <= x <= self.end

    def from_normalized(self, x: float) -> float | Value:
        if self.from_normalize_override:
            return self.from_normalize_override(self, x)
        x_normal = (x - self.range_start) / (self.range_end - self.range_start)
        value = safe_exp2(x_normal * (self.end - self.start) + self.start)
        return self.apply_format(value)

    def to_normalized(self, x: float):
        if self.to_normalize_override:
            return self.to_normalize_override(self, x)
        x_normal = (math.log2(x) - self.start) / (self.end - self.start)
        return x_normal * (self.range_end - self.range_start) + self.range_start
