from canopen_monitor.parser import FailedValidationError
from canopen_monitor.parser.utilities import *


def parse(data: bytes, cob_id):
    if len(data) > 1:
        raise FailedValidationError(data, cob_id, cob_id, __name__,
                                    f"SYNC message is outside of bounds "
                                    "limit of 1 byte, {len(data)} provided")
    return f"SYNC - {decode(UNSIGNED8, data)}"
