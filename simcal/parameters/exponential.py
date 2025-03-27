from __future__ import annotations

import math
import warnings
from typing import Self
from typing import TYPE_CHECKING

from simcal.parameters.ordered import Ordered
from simcal.utility_functions import safe_exp2

if TYPE_CHECKING:
    from simcal.parameters import Value


class Exponential(Ordered):
    # start and end are in exponent terms
    def __init__(self, start, end, integer=False):
        super().__init__(0, 1, integer=integer)
        if self.integer:
            start = int(start)
            end = int(end)
        self.start = start
        self.end = end
        self.to_exponent_override = None

    def constrain(self, new_start: float | Value, new_end: float | Value) -> Self:
        from simcal.parameters import Value
        if isinstance(new_start, Value):
            new_start = new_start.value
        if isinstance(new_end, Value):
            new_end = new_end.value
        ret = Exponential(self.to_exponent(new_start), self.to_exponent(new_end), self.integer)
        ret.range_start = self.range_start
        ret.range_end = self.range_end
        return ret

    def is_valid_value(self, x: float | Value) -> bool:
        return self.start <= x <= self.end

    def from_normalized(self, x: float) -> float | Value:
        if self.from_normalize_override:
            return self.from_normalize_override(self, x)
        x_normal = (x - self.range_start) / (self.range_end - self.range_start)
        value = safe_exp2(x_normal * (self.end - self.start) + self.start)
        if self.integer:
            value = int(value)
        return self.apply_format(value)

    def to_exponent(self, x: int | float | Value) -> float :
        if self.integer:
            x = int(x)
        if self.to_exponent_override:
            return self.to_exponent_override(x)
        else:
            if self.to_normalize_override:
                warnings.warn("to_normalize_override may conflict with to_exponent calculation, "
                              "please provide a to_exponent_override as well")

        return math.log2(x)

    def to_normalized(self, x: int | float):
        if self.integer:
            x = int(x)
        if self.to_normalize_override:
            return self.to_normalize_override(self, x)
        x_normal = (math.log2(x) - self.start) / (self.end - self.start)
        return x_normal * (self.range_end - self.range_start) + self.range_start
