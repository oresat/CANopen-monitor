from canopen_monitor.parser.eds import EDS
from canopen_monitor.parser.utilities import decode, UNSIGNED8


def parse(cob_id: int, data: bytes, eds: EDS):
    if len(data) > 1:
        raise FailedValidationError(data, cob_id, cob_id, __name__,
                                    f"SYNC message is outside of bounds "
                                    "limit of 1 byte, {len(data)} provided")
    return f"SYNC - {decode(UNSIGNED8, data)}"
