import datetime

from canopen_monitor.parser.utilities import *

"""
the Time-Stamp object represents an absolute time in milliseconds after midnight and the number of days since
January 1, 1984. This is a bit sequence of length 48 (6 bytes).
"""


def parse(data: bytes):
    if len(data) != 6:
        raise ValueError("Invalid TIME message length")

    milliseconds = int.from_bytes(data[0:4], "big")
    days = int.from_bytes(data[4:6], "big")

    date = datetime.datetime(1984, 1, 1, 0, 0, 0) + datetime.timedelta(days=days, milliseconds=milliseconds)

    return f"Time - {date.strftime('%m/%d/%Y %H:%M:%S.%f')}"
