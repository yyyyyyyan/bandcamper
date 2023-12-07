from string import Formatter
from uuid import uuid4


def get_random_filename_template():
    return uuid4().hex[:16] + "{ext}"


class FilenameFormatter(Formatter):
    """
    Custom formatter for modifying user-defined output.
    Reference: https://peps.python.org/pep-3101

    Two formatters are implemented:
        1. :u - uppercase
        2. :l - lowercase
    """

    def format_field(self, value, format_spec: str):
        if isinstance(value, str):
            # format string based on provided modifier and remove modifier character from format string
            # before continuing
            if format_spec.endswith("u"):
                value = value.upper()
                format_spec = format_spec[:-1]
            elif format_spec.endswith("l"):
                value = value.lower()
                format_spec = format_spec[:-1]
        return super().format_field(value, format_spec)
