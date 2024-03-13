from __future__ import annotations

from copy import copy


class _FormattedValue:
    """
    Represents a value with a specific format for string representation.
    """

    def __init__(self, formatter: str, value: int | float) -> None:
        """
        Initializes the _FormattedValue instance.

        :param str formatter: The format string used for string representation.
        :param int | float value: The numeric value.
        """
        self.formatter = formatter
        self.value = value

    def _apply_format(self, x: float) -> str:
        """
        Applies the specified format to the given value.

        :param float x: The value to format.
        :return: The formatted string.
        :rtype: str
        """
        return self.formatter % x

    def __str__(self) -> str:
        """
        Returns the string representation of the value.

        :return: The formatted string representation.
        :rtype: str
        """
        return self._apply_format(self.value)

    def __repr__(self):
        """
        Returns the printable representation of the value.

        :return: The formatted string representation.
        :rtype: str
        """
        return str(self)

    def __float__(self) -> float:
        """
        Returns the underlying float value.

        :return: The underlying float value.
        :rtype: float
        """
        return self.value

    def __neg__(self) -> _FormattedValue:
        """
        Overloads the negation operator.

        :return: The result of inversion.
        :rtype: _FormattedValue
        """
        ret = copy(self)
        ret.value = -self.value
        return ret

    def __add__(self, other: int | float) -> float:
        """
        Overloads the addition operator.

        :param int | float other: The value to add.
        :return: The result of addition.
        :rtype: float
        """
        return self.value + other

    def __radd__(self, other: int | float) -> float:
        """
        Overloads the reverse addition operator.

        :param int | float other: The value to which the instance is added.
        :return: The result of addition.
        :rtype: float
        """
        return other + self.value

    def __sub__(self, other: int | float) -> float:
        """
        Overloads the subtraction operator.

        :param int | float other: The value to subtract.
        :return: The result of subtraction.
        :rtype: float
        """
        return self.value - other

    def __rsub__(self, other: int | float) -> float:
        """
        Overloads the reverse subtraction operator.

        :param int | float other: The value from which the instance is subtracted.
        :return: The result of subtraction.
        :rtype: float
        """
        return other - self.value

    def __mul__(self, other: int | float) -> float:
        """
        Overloads the multiplication operator.

        :param int | float other: The value to multiply.
        :return: The result of multiplication.
        :rtype: float
        """
        return self.value * other

    def __rmul__(self, other: int | float) -> float:
        """
        Overloads the reverse multiplication operator.

        :param int | float other: The value by which the instance is multiplied.
        :return: The result of multiplication.
        :rtype: float
        """
        return other * self.value

    def __truediv__(self, other: int | float) -> float:
        """
        Overloads the division operator.

        :param int | float other: The value to divide by.
        :return: The result of division.
        :rtype: float
        """
        return self.value / other

    def __rtruediv__(self, other: int | float) -> float:
        """
        Overloads the reverse division operator.

        :param int | float other: The value by which the instance is divided.
        :return: The result of division.
        :rtype: float
        """
        return other / self.value

    def __eq__(self, other: int | float) -> bool:
        """
        Overloads the equality operator.

        :param int | float other: The value to compare.
        :return: True if the values are equal, False otherwise.
        :rtype: bool
        """
        return self.value == other

    def __lt__(self, other: int | float) -> bool:
        """
        Overloads the less than operator.

        :param int | float other: The value to compare.
        :return: True if the instance value is less than the other value, False otherwise.
        :rtype: bool
        """
        return self.value < other

    def __gt__(self, other: int | float) -> bool:
        """
        Overloads the greater than operator.

        :param int | float other: The value to compare.
        :return: True if the instance value is greater than the other value, False otherwise.
        :rtype: bool
        """
        return self.value > other

    def __ne__(self, other: int | float) -> bool:
        """
        Overloads the nonequality operator.

        :param int | float other: The value to compare.
        :return: True if the values are equal, False otherwise.
        :rtype: bool
        """
        return self.value == other

    def __le__(self, other: int | float) -> bool:
        """
        Overloads the less than or equal to operator.

        :param int | float other: The value to compare.
        :return: True if the instance value is less than the other value, False otherwise.
        :rtype: bool
        """
        return self.value < other

    def __ge__(self, other: int | float) -> bool:
        """
        Overloads the greater than or equal to operator.

        :param int | float other: The value to compare.
        :return: True if the instance value is greater than the other value, False otherwise.
        :rtype: bool
        """
        return self.value >= other
