from typing import Any

from simcal.parameters.value import Value


class Base(object):
    def __init__(self):
        self.formatter = None
        self.custom_data = None

    def format(self, formatter):
        """
        Specify a printf-style format string for the parameter
        :param formatter: the format string
        :return:
        """
        self.formatter = formatter
        return self

    def set_custom_data(self, custom_data: Any):
        """
        Add arbitrary user-defined data to the parameter, which can be retrieved later if need be
        :param Any custom_data: the metadata
        """
        self.custom_data = custom_data
        return self

    def get_custom_data(self) -> Any:
        """
        Retrieve user-defined data that may have been added to the parameter
        :return: the custom data
        :rtype: Any
        """
        return self.custom_data

    def apply_format(self, value):
        return Value(None, value, self)
