from __future__ import annotations
import array
from datetime import datetime, timedelta
from struct import unpack
from typing import List, Union
from .eds import DataType, EDS


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
        self.time_occured = datetime.now()
        super().__init__(self.message)


def get_name(eds_config: EDS, index: Union[List[int], bytes]) -> (str, str):
    """
    Get the name and data type for a given index
    :param eds_config: An EDS file for the current node
    :param index: the index and subindex to retrieve data from
                  expected to be length 3. (not validated)
    :return: (str, str): a tuple containing the name and data type as a string
    :raise: IndexError: The index or subindex failed to find a value in the
    provided OD file
    :raise: ValueError: The provided index/subindex does not contain a
    parameter_name and data_type attribute
    """
    index_bytes = list(map(lambda x: hex(x)[2:].rjust(2, '0'), index))
    key = int('0x' + ''.join(index_bytes[1::-1]), 16)
    subindex_key = int('0x' + ''.join(index_bytes[2:3]), 16)

    current = eds_config[hex(key)]
    result = eds_config[hex(key)].parameter_name

    if len(current) > 0:
        result += " " + eds_config[hex(key)][subindex_key].parameter_name
        defined_type = eds_config[hex(key)][subindex_key].data_type
    else:
        defined_type = eds_config[hex(key)].data_type

    return defined_type, result


def decode(defined_type: Union[str, DataType], data: List[int]) -> str:
    """
    Decodes data by defined type
    :param defined_type: Hex constant for type
    :param data: list of ints to be decoded
    :return: Decoded data as string
    :raise: ValueError: Indicates datatype provided is not supported
    """
    if defined_type in DataType.UNSIGNED_INTEGERS.value:
        result = str(int.from_bytes(data, byteorder="little", signed=False))
    elif defined_type in DataType.SIGNED_INTEGERS.value:
        result = str(int.from_bytes(data, byteorder="little", signed=True))
    elif defined_type == DataType.BOOLEAN.value:
        if int.from_bytes(data, byteorder="little", signed=False) > 0:
            result = str(True)
        else:
            result = str(False)
    elif defined_type in DataType.FLOATING_POINTS.value:
        data = array.array('B', data).tobytes()
        result = str(unpack('>f', data)[0])
    elif defined_type == DataType.VISIBLE_STRING.value:
        data = array.array('B', data).tobytes()
        result = data.decode('utf-8')
    elif defined_type == DataType.OCTET_STRING.value:
        data = list(map(lambda x: hex(x)[2:].rjust(2, '0'), data))
        result = '0x' + ''.join(data)
    elif defined_type == DataType.UNICODE_STRING.value:
        data = array.array('B', data).tobytes()
        result = data.decode('utf-16-be')
    elif defined_type == DataType.TIME_OF_DAY.value:
        delta = get_time_values(data)
        date = datetime(1984, 1, 1) + delta
        result = date.isoformat()
    elif defined_type == DataType.TIME_DIFFERENCE.value:
        result = str(get_time_values(data))
    elif defined_type in DataType.NON_FORMATTED.value:
        result = format_bytes(data)
    elif defined_type == DataType.ECSS_TIME.value:
        # This is ECSS SCET Time
        # data[0:4]: Fine Time: Microseconds
        # data[4:8]: Coarse Time: Seconds
        coarse = data[4:8]
        fine = int.from_bytes(data[:4], byteorder="little", signed=False)
        coarse = int.from_bytes(data[4:8], byteorder="little", signed=False)
        delta = timedelta(seconds=coarse, microseconds=fine)
        date = datetime(1970, 1, 1) + delta
        result = date.isoformat()
    else:
        raise ValueError(f"Invalid data type {defined_type}. "
                         f"Unable to decode data {str(data)}")

    return result


def get_time_values(data: [int]) -> timedelta:
    # Component ms is the time in milliseconds after midnight. Component
    # days is the number of days since January 1, 1984.
    # Format UNSIGNED 28 (ms), VOID4, UNSIGNED 16 (Days)
    ms_raw = data[:4]
    ms_raw[3] = ms_raw[3] >> 4
    ms = int.from_bytes(ms_raw, byteorder="little", signed=False)
    days = int.from_bytes(data[5:7], byteorder="little", signed=False)
    return timedelta(days=days, milliseconds=ms)


def format_bytes(data: Union[List[int], bytes]) -> str:
    return ' '.join(list(map(lambda x: hex(x)[2:]
                             .upper()
                             .rjust(2, '0'),
                             data)))
