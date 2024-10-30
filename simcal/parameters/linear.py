from __future__ import annotations

from typing import Self
from typing import TYPE_CHECKING

from simcal.parameters.ordered import Ordered

if TYPE_CHECKING:
    from simcal.parameters import Value


class Linear(Ordered):  # requires testing
    def __init__(self, start, end, integer=False):
        super().__init__(0, 1, integer=integer)
        if self.integer:
            start = int(start)
            end = int(end)
        self.start = start
        self.end = end

    def constrain(self, new_range_start: float | Value, new_range_end: float | Value) -> Self:
        from simcal.parameters import Value
        if isinstance(new_range_start, Value):
            new_range_start = new_range_start.value
        if isinstance(new_range_end, Value):
            new_range_end = new_range_end.value

        ret = Linear(new_range_start, new_range_end,self.integer)
        ret.start = self.start
        ret.end = self.end
        return ret

    def is_valid_value(self, x: float | Value) -> bool:
        return self.start <= x <= self.end

    def from_normalized(self, x: float) -> float | Value:
        if self.from_normalize_override:
            return self.from_normalize_override(self, x)
        x_normal = (x - self.range_start) / (self.range_end - self.range_start)
        value = x_normal * (self.end - self.start) + self.start
        if self.integer:
            value = int(value)
        return self.apply_format(value)

    def to_normalized(self, x: float):
        if self.integer:
            x = int(x)
        if self.to_normalize_override:
            return self.to_normalize_override(self, x)
        x_normal = (x - self.start) / (self.end - self.start)
        return x_normal * (self.range_end - self.range_start) + self.range_start
