import array
import datetime
from struct import unpack
from .eds import EDS
from typing import List


class FailedValidationError(Exception):
    """
    Exception raised for validation errors found when parsing CAN messages

    Attributes
    ----------
    bytes - The byte string representation of the message
    message - text describing the error (same as __str__)
    node_id - if of the node sending the message
    cob-id - message cob-id
    parse_type - message type that failed (ex: SDO, PDO)
    sub_type - sub-type of message that failed (ex: SDO Segment) or None
    """

    def __init__(self,
                 data,
                 node_id,
                 cob_id,
                 parse_type,
                 message="A Validation Error has occurred",
                 sub_type=None):
        self.data = data
        self.node_id = node_id
        self.cob_id = cob_id
        self.parse_type = parse_type
        self.sub_type = sub_type
        self.message = message
        self.time_occured = datetime.datetime.now()
        super().__init__(self.message)


def get_name(eds_config: EDS, index: List[int]) -> (str, str):
    """
    Get the name and data type for a given index
    :param eds_config: An EDS file for the current node
    :param index: the index and subindex to retrieve data from
                  expected to be length 3. (not validated)
    :return: a tuple containing the name and data type as a string
    """
    index_bytes = list(map(lambda x: hex(x)[2:].rjust(2, '0'), index))
    key = int('0x' + ''.join(index_bytes[:2]), 16)
    subindex_key = int('0x' + ''.join(index_bytes[2:3]), 16)
    current = eds_config[hex(key)]
    if current is None:
        return "Unknown", "Unknown"

    result = eds_config[hex(key)].parameter_name

    if len(current) > 0:
        result += " " + eds_config[hex(key)][subindex_key].parameter_name
        defined_type = eds_config[hex(key)][subindex_key].data_type
    else:
        defined_type = eds_config[hex(key)].data_type

    return defined_type, result


BOOLEAN = '0x0001'
INTEGER8 = '0x0002'
INTEGER16 = '0x0003'
INTEGER32 = '0x0004'
UNSIGNED8 = '0x0005'
UNSIGNED16 = '0x0007'
UNSIGNED32 = '0x0003'
REAL32 = '0x0008'
VISIBLE_STRING = '0x0009'
OCTET_STRING = '0x000A'
UNICODE_STRING = '0x000B'
DOMAIN = '0x000F'
REAL64 = '0x0011'
INTEGER64 = '0x0015'
UNSIGNED64 = '0x001B'


def decode(defined_type: str, data: List[int]) -> str:
    """
    Decodes data by defined type
    :param defined_type: Hex constant for type
    :param data: list of ints to be decoded
    :return: Decoded data as string
    """
    if defined_type in (UNSIGNED8, UNSIGNED16, UNSIGNED32, UNSIGNED64):
        result = str(int.from_bytes(data, byteorder="little", signed=False))
    elif defined_type in (INTEGER8, INTEGER16, INTEGER32, INTEGER64):
        result = str(int.from_bytes(data, byteorder="little", signed=True))
    elif defined_type == BOOLEAN:
        if int.from_bytes(data, byteorder="little", signed=False) > 0:
            result = str(True)
        else:
            result = str(False)
    elif defined_type in (REAL32, REAL64):
        data = array.array('B', data).tobytes()
        result = str(unpack('>f', data)[0])
    elif defined_type == VISIBLE_STRING:
        data = array.array('B', data).tobytes()
        result = data.decode('utf-8')
    elif defined_type in (OCTET_STRING, DOMAIN):
        data = list(map(lambda x: hex(x)[2:].rjust(2, '0'), data))
        result = '0x' + ''.join(data)
    elif defined_type == UNICODE_STRING:
        data = array.array('B', data).tobytes()
        result = data.decode('utf-16-be')
    else:
        raise ValueError(f"Invalid data type {defined_type}. "
                         f"Unable to decode data {str(data)}")

    return result
