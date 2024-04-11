from typing import Any

from simcal.parameters.value import Value


class Base(object):
    def __init__(self):
        self.formatter = None
        self.metadata = None

    def format(self, formatter):
        """
        Specify a printf-style format string for the parameter
        :param formatter: the format string
        :return:
        """
        self.formatter = formatter
        return self

    def set_metadata(self, metadata: Any):
        """
        Add arbitrary, user-defined metadata to the parameter
        :param Any metadata: the metadata
        """
        self.metadata = metadata
        return self

    def get_metadata(self) -> Any:
        """
        Retrieve user-defined metadata that may have been added to the parameter
        :return: the metadata
        :rtype: Any
        """
        return self.metadata

    def apply_format(self, value):
        if self.formatter:
            return Value(self.formatter, value, self)
        return Value(None, value, self)
