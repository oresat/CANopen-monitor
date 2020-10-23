import datetime
from typing import List

from .eds import EDS
from .utilities import FailedValidationError

"""
the Time-Stamp object represents an absolute time in milliseconds after
midnight and the number of days since January 1, 1984. This is a bit sequence
of length 48 (6 bytes).
"""


def parse(cob_id: int, data: List[int], eds: EDS):
    if len(data) != 6:
        raise FailedValidationError(data, cob_id, cob_id, __name__,
                                    "Invalid TIME message length")

    milliseconds = int.from_bytes(data[0:4], "little")
    days = int.from_bytes(data[4:6], "little")

    date = datetime.datetime(1984, 1, 1, 0, 0, 0) \
        + datetime.timedelta(days=days, milliseconds=milliseconds)

    return f"Time - {date.strftime('%m/%d/%Y %H:%M:%S.%f')}"
