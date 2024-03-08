from simcal.parameters._formatted_value import _FormattedValue
from simcal.parameters.ordered import Ordered


class Ordinal(Ordered):
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
