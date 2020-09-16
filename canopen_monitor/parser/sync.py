from canopen_monitor.parser.utilities import *


def parse(data: bytes):
    # if len(data) > 1:
    #     raise ValueError("SYNC message is outside of bounds")
    return f"SYNC - {decode(UNSIGNED8, data)}"
