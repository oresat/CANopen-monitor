from math import ceil, floor
from struct import unpack

PDO1_TX = 0x1A00
PDO1_RX = 0x1600
PDO2_TX = 0x1A01
PDO2_RX = 0x1601
PDO3_TX = 0x1A02
PDO3_RX = 0x1602
PDO4_TX = 0x1A03
PDO4_RX = 0x1603


def parse(cob_id, eds, data: bytes):
    """
    PDO mappings come from the eds file and is dependent on the type (Reciving/transmission PDO).
    mapping value is made up of index subindex and size. For Example 0x31010120 Means 3101sub01 size 32bit

    The eds mapping is determined by the cob_id passed ot this function. That indicated which PDO record to look up
    in the EDS file.
    """
    if 0x180 <= cob_id < 0x200:  # PDO1 tx
        pdo_type = PDO1_TX
    elif 0x200 <= cob_id < 0x280:  # PDO1 rx
        pdo_type = PDO1_RX
    elif 0x280 <= cob_id < 0x300:  # PDO2 tx
        pdo_type = PDO2_TX
    elif 0x300 <= cob_id < 0x380:  # PDO2 rx
        pdo_type = PDO2_RX
    elif 0x380 <= cob_id < 0x400:  # PDO3 tx
        pdo_type = PDO3_TX
    elif 0x400 <= cob_id < 0x480:  # PDO3 rx
        pdo_type = PDO3_RX
    elif 0x480 <= cob_id < 0x500:  # PDO4 tx
        pdo_type = PDO4_TX
    elif 0x500 <= cob_id < 0x580:  # PDO4 rx
        pdo_type = PDO4_RX
    else:
        raise ValueError(f"Unable to determine pdo type with given cob_id {hex(cob_id)}")

    num_elements = int(eds[pdo_type].sub_indices[0].default_value)
    if num_elements < 0x40:
        return parse_pdo(num_elements, pdo_type, eds, data)

    if num_elements in (0xFE, 0xFF):
        return parse_mpdo(num_elements, pdo_type, eds, data)

    raise ValueError(f"Invalid pdo mapping detected in eds file at [{pdo_type}sub0]")


def parse_pdo(num_elements, pdo_type, eds, data):
    """
    Parse pdo message. Message will include num_elements elements. Elements are processed in reverse order, from
    rightmost to leftmost
    """
    output_string = ""
    data_start = 0
    for i in range(num_elements, 0, -1):
        pdo_definition = int(eds[pdo_type].sub_indices[i].default_value).to_bytes(4, "big")
        index = pdo_definition[0:3]
        size = pdo_definition[3]
        mask = 1
        for j in range(1, size):
            mask = mask << 1
            mask += 1
        eds_details = get_name(eds, index)
        num_bytes = ceil(size / 8)
        masked_data = int.from_bytes(data[len(data) - num_bytes - floor(data_start / 8):len(data) -
                                          floor(data_start / 8)], "big") & mask
        masked_data = masked_data >> data_start % 8
        masked_data = masked_data.to_bytes(num_bytes, "big")
        output_string = f"{eds_details[1]} - {decode(eds_details[0], masked_data)}" + output_string
        if i > 1:
            output_string = "\n" + output_string
        data_start += size

    return output_string


def parse_mpdo(num_elements, pdo_type, eds, data):
    mpdo = MPDO(data)
    if mpdo.is_source_addressing and num_elements != 0xFE:
        raise ValueError(f"MPDO type and definition do not match. Check [{pdo_type}sub0]")

    eds_details = get_name(eds, mpdo.index)
    return f"{eds_details[1]} - {decode(eds_details[0], mpdo.data)}"


class MPDO:
    """


 .. code-block:: python


     +-------------+---------+----------------+
     |   f   addr  |    m    |       d        |
     |   7   6_0   |         |                |
     +-------------+---------+----------------+
            0        1     3  4             7

 Definitions
 ===========
 * **f**: address type
  0. Source addressing
  1. Destination addressing

 * **addr**: node-ID of the MPDO consumer in destination addressing or MPDO producer in source
 addressing.
  0. Shall be reserved in source addressing mode. Shall address all CANopen devices in the network
  that are configured for MPDO reception in destination addressing mode.
  1..127. Shall address the CANopen device in the network with the very same node-ID

 * **m**: multiplexer. It represents the index/sub-index of the process data to be transferred by
 the MPDO. In source addressing this shall be used to identify the data from the transmitting CANopen
 device or in destination addressing addressing to identity the data on the receiving CANopen device.

 * **d**: process data. Data length lower than 4 bytes is filled up to fit 32-bit
     """

    def __init__(self, raw_sdo: bytes):
        self.__is_source_addressing = raw_sdo[0] & 0x8 == 0x8
        self.__is_destination_addressing = not self.__is_source_addressing
        self.__addr = raw_sdo[0] & 0x7F
        self.__index = raw_sdo[1:4]
        self.__data = raw_sdo[4:8]

    @property
    def is_source_addressing(self):
        return self.__is_source_addressing

    @property
    def is_destination_addressing(self):
        return self.__is_destination_addressing

    @property
    def addr(self):
        return self.__addr

    @property
    def index(self):
        return self.__index

    @property
    def data(self):
        return self.__data


# TODO: Below are functions from the SDO that need to be consolidated somewhere
def get_name(eds, index: bytes):
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
