import string
from math import ceil, floor
from .eds import EDS
from .utilities import FailedValidationError, get_name, decode
from ..can import MessageType

PDO1_TX = 0x1A00
PDO1_RX = 0x1600
PDO2_TX = 0x1A01
PDO2_RX = 0x1601
PDO3_TX = 0x1A02
PDO3_RX = 0x1602
PDO4_TX = 0x1A03
PDO4_RX = 0x1603


def parse(cob_id: int, data: bytes, eds: EDS):
    """
    PDO mappings come from the eds file and is dependent on the type (
    Receiving/transmission PDO). Mapping value is made up of index subindex
    and size. For Example 0x31010120 Means 3101sub01 size 32bit

    The eds mapping is determined by the cob_id passed ot this function. That
    indicated which PDO record to look up in the EDS file.
    """
    msg_type = MessageType.cob_id_to_type(cob_id)
    pdo_type = {
        MessageType.PDO1_TX: PDO1_TX,
        MessageType.PDO1_RX: PDO1_RX,
        MessageType.PDO2_TX: PDO2_TX,
        MessageType.PDO2_RX: PDO2_RX,
        MessageType.PDO3_TX: PDO3_TX,
        MessageType.PDO3_RX: PDO3_RX,
        MessageType.PDO4_TX: PDO4_TX,
        MessageType.PDO4_RX: PDO4_RX,
        MessageType.UKNOWN: None
    }[msg_type]

    if(not pdo_type or msg_type.supertype is not MessageType.PDO):
        raise FailedValidationError(data,
                                    cob_id - MessageType.PDO1_TX.value[0],
                                    cob_id,
                                    __name__,
                                    f"Unable to determine pdo type with given"
                                    f" cob_id {hex(cob_id)}, expected value"
                                    f" between {MessageType.PDO1_TX.value[0]}"
                                    f" and {MessageType.PDO4_RX.value[1] + 1}")

    if len(data) > 8 or len(data) < 1:
        raise FailedValidationError(data,
                                    cob_id - MessageType.PDO1_TX.value[0],
                                    cob_id,
                                    __name__,
                                    f"Invalid payload length {len(data)} "
                                    f"expected between 1 and 8")
    try:
        eds_elements = eds[hex(pdo_type)][0]
    except TypeError:
        raise FailedValidationError(data,
                                    cob_id - MessageType.PDO1_TX.value[0],
                                    cob_id,
                                    __name__,
                                    f"Unable to find eds data for pdo type "
                                    f"{hex(pdo_type)}")

    # default_value could be 2 or '0x02', this is meant to work with both
    if (c in string.hexdigits for c in str(eds_elements.default_value)):
        num_elements = int(str(eds_elements.default_value), 16)
    else:
        num_elements = int(str(eds_elements.default_value))

    if num_elements < 0x40:
        return parse_pdo(num_elements, pdo_type, cob_id, eds, data)

    if num_elements in (0xFE, 0xFF):
        if len(data) != 8:
            raise FailedValidationError(data,
                                        cob_id - MessageType.PDO1_TX.value[0],
                                        cob_id,
                                        __name__,
                                        f"Invalid payload length {len(data)} "
                                        f"expected 8")
        return parse_mpdo(num_elements, pdo_type, eds, data, cob_id)

    raise FailedValidationError(data,
                                cob_id - MessageType.PDO1_TX.value[0],
                                cob_id,
                                __name__,
                                f"Invalid pdo mapping detected in eds file at "
                                f"[{pdo_type}sub0]")


def parse_pdo(num_elements, pdo_type, cob_id, eds, data):
    """
    Parse pdo message. Message will include num_elements elements. Elements
    are processed in reverse order, from rightmost to leftmost
    """
    output_string = ""
    data_start = 0
    for i in range(num_elements, 0, -1):
        try:
            eds_record = eds[hex(pdo_type)][i]
        except TypeError:
            raise FailedValidationError(data,
                                        cob_id - MessageType.PDO1_TX.value[0],
                                        cob_id,
                                        __name__,
                                        f"Unable to find eds data for pdo type"
                                        f" {hex(pdo_type)} index {i}")

        pdo_definition = int(eds_record.default_value, 16).to_bytes(4, "big")

        index = pdo_definition[0:3]
        size = pdo_definition[3]
        mask = 1
        for j in range(1, size):
            mask = mask << 1
            mask += 1
        eds_details = get_name(eds, index)
        num_bytes = ceil(size / 8)

        start = len(data) - num_bytes - floor(data_start / 8)
        end = len(data) - floor(data_start / 8)
        masked_data = int.from_bytes(data[start:end], "big") & mask
        masked_data = masked_data >> data_start % 8
        masked_data = masked_data.to_bytes(num_bytes, "big")
        output_string = f"{eds_details[1]} -" \
                        f" {decode(eds_details[0], masked_data)}" + \
                        output_string
        if i > 1:
            output_string = " " + output_string
        data_start += size

    return output_string


def parse_mpdo(num_elements, pdo_type, eds, data, cob_id):
    mpdo = MPDO(data)
    if mpdo.is_source_addressing and num_elements != 0xFE:
        raise FailedValidationError(data,
                                    cob_id - MessageType.PDO1_TX.value[0],
                                    cob_id,
                                    __name__,
                                    f"MPDO type and definition do not match. "
                                    f"Check eds file at [{pdo_type}sub0]")

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

 * **addr**: node-ID of the MPDO consumer in destination addressing or MPDO
 producer in source addressing. 0. Shall be reserved in source addressing
 mode. Shall address all CANopen devices in the network that are configured
 for MPDO reception in destination addressing mode. 1..127. Shall address the
 CANopen device in the network with the very same node-ID

 * **m**: multiplexer. It represents the index/sub-index of the process data
 to be transferred by the MPDO. In source addressing this shall be used to
 identify the data from the transmitting CANopen device or in destination
 addressing addressing to identity the data on the receiving CANopen device.

 * **d**: process data. Data length lower than 4 bytes is filled up to fit
 32-bit
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
