from struct import unpack
from canopen_monitor.parser.eds import EDS, Index


def get_name(eds: EDS, index: bytes):
    key = int(index[:2].hex(), 16)
    subindex_key = int(index[2:3].hex(), 16)
    result = eds[key].parameter_name

    if eds[key].sub_indices is not None:
        result += " " + eds[key].sub_indices[subindex_key].parameter_name
        defined_type = eds[key].sub_indices[subindex_key].data_type
    else:
        defined_type = eds[key].data_type

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


def decode(defined_type, data):
    if defined_type in (UNSIGNED8, UNSIGNED16, UNSIGNED32, UNSIGNED64):
        result = str(int.from_bytes(data, byteorder="big", signed=False))
    elif defined_type in (INTEGER8, INTEGER16, INTEGER32, INTEGER64):
        result = str(int.from_bytes(data, byteorder="big", signed=True))
    elif defined_type == BOOLEAN:
        if int.from_bytes(data, byteorder="big", signed=False) > 0:
            result = str(True)
        else:
            result = str(False)
    elif defined_type in (REAL32, REAL64):
        result = str(unpack('>f', data)[0])
    elif defined_type == VISIBLE_STRING:
        result = data.decode('utf-8')
    elif defined_type in (OCTET_STRING, DOMAIN):
        result = data.hex()
    elif defined_type == UNICODE_STRING:
        result = data.decode('utf-16-be')
    else:
        raise ValueError(f"Invalid data type {defined_type}. Unable to decode data {data.hex()}")

    return result
