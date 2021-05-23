from .eds import EDS
from .utilities import FailedValidationError, decode, DataType


def parse(cob_id: int, data: bytes, eds: EDS):
    if len(data) > 1:
        raise FailedValidationError(data, cob_id, cob_id, __name__,
                                    f'SYNC message is outside of bounds '
                                    f'limit of 1 byte, {len(data)} provided')
    return f'SYNC - {decode(DataType.UNSIGNED8.value, data)}'
