from simcal.parameters.ordered import Ordered
from simcal.parameters.value import Value


class Linear(Ordered):  # requires testing
    def __init__(self, start, end):
        super().__init__(0, 1)
        self.start = start
        self.end = end

    def from_normalized(self, x: float) -> float | Value:
        if self.from_normalize_override:
            return self.from_normalize_override(self, x)
        x_normal = (x - self.range_start) / (self.range_end - self.range_start)
        value = x_normal * (self.end - self.start) + self.start
        return self.apply_format(value)

    def to_normalized(self, x: float):
        if self.to_normalize_override:
            return self.to_normalize_override(self, x)
        x_normal = (x - self.start) / (self.end - self.start)
        return x_normal * (self.range_end - self.range_start) + self.range_start
