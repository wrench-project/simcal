from simcal.parameters._formatted_value import _FormattedValue
from simcal.parameters.base import Base


class Ordered(Base):
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
