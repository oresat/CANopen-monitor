from struct import unpack

# EDS Data Types (Move to utilities?)
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

SDO_TX = 'SDO_TX'
SDO_RX = 'SDO_RX'


class SDOInitiateData:
    """
 This class is used by the SDO parser to parse the SDO initiate messages containing data

 This message type is the first message sent from the client during an SDO Download
 and the first message sent from the server during an SDO Upload

 It will contain the data to be downloaded or provide information about the segments to be downloaded

 The SDO initiate message with data should match the below format:


 .. code-block:: python


     +-------------------------+---------+----------------+
     | ccs/scs  x   n    e   s |    m    |       d        |
     |  7_5     4  3_2   1   0 |         |                |
     +-------------------------+---------+----------------+
                 0              1     3  4             7

 Definitions
 ===========
 * **ccs**: client command specifier
  1. initiate download request

 * **scs**: server command specifier
  2. initiate upload response

 * **n**: number of bytes (if e = 1 and s =1)

 * **e**: transfer type
  0. normal transfer
  1. expedited transfer

 * **s**: size indicator
  0. data set size is not indicated
  1. data set size is indicated

 * **m**: multiplexer. It represents the index/sub-index of the data to be transferred

 * **d**: data
  * e = 0, s = 0: d is reserved for further use
  * e = 0, s = 1: d contains the number of bytes to be downloaded
  * e = 1, s = 1: d contains the data of length 4-n to be downloaded
  * e = 1, s = 0: d contains unspecified number of bytes to be downloaded

 * **x**: not used, always 0
     """

    def __init__(self, raw_sdo: bytes):
        self.__is_expedited = None
        self.__size_indicator = None
        self.__n = None
        self.__data = None
        self.__decode_first_section(raw_sdo[0])
        self.__index = raw_sdo[1:4]
        self.__decode_data(raw_sdo[4:8])

    @property
    def is_expedited(self):
        return self.__is_expedited

    @property
    def size_indicator(self):
        return self.__size_indicator

    @property
    def n(self):
        return self.__n

    @property
    def data(self):
        return self.__data

    @property
    def index(self):
        return self.__index

    def __decode_first_section(self, byte_value):
        if byte_value & 0x10 > 0:
            raise ValueError(f"Invalid x value (4): {hex(byte_value & 0x10)}")

        if byte_value & 0x02 == 0:
            self.__is_expedited = False
        else:
            self.__is_expedited = True

        # if size indicator is set
        if byte_value & 0x01 == 0x01:
            self.__size_indicator = True
        else:
            self.__size_indicator = False

        if self.__is_expedited and self.__size_indicator:
            self.__n = byte_value & 0x0C >> 2
        elif byte_value & 0x0C > 0:
            raise ValueError(f"Invalid n value (3_2): '{hex(byte_value & 0x0C)}")
        else:
            self.__n = 0

    def __decode_data(self, byte_value: bytes):
        if not self.__is_expedited:
            if self.__size_indicator:
                self.__data = int.from_bytes(byte_value, "big")
            elif int.from_bytes(byte_value, "big") > 0:
                raise ValueError(f"Invalid data value: '{byte_value.hex()}")
        # Expedited Transfer
        else:
            if self.__size_indicator:
                self.__data = byte_value[3 - self.__n:4]
                if int.from_bytes(byte_value[0:3 - self.__n], "big") > 0:
                    raise ValueError(f"Data value larger than size: '{self.__n}'")
            else:
                self.__data = byte_value


class SDOInitiateNoData:
    """
 This class is used by the SDO parser to parse the SDO initiate messages containing no data

 This message type is the first message sent from the server during an SDO Download
 and the first message sent from the client during an SDO Upload

 It will contain the data to be downloaded or provide information about the segments to be downloaded

 The SDO initiate message with data should match the below format:

  .. code-block:: python


      +-------------------------+---------+----------------+
      | ccs/scs      x          |    m    |   reserved     |
      |  7_5        4_0         |         |                |
      +-------------------------+---------+----------------+
                    0             1     3  4             7

  Definitions
  ===========
  * **ccs**: client command specifier
   2. initiate upload request

  * **scs**: server command specifier
   3. initiate download response

  * **x**: not used, always 0

  * **reserved**: reserved for further use, always 0
      """

    def __init__(self, raw_sdo: bytes):
        self.__index = raw_sdo[1:4]
        if raw_sdo[0] & 0x1F > 0:
            raise ValueError(f"Invalid x value (4_0): '{hex(raw_sdo[0] & 0x1F)}'")
        if int.from_bytes(raw_sdo[4:8], "big") > 0:
            raise ValueError(f"Invalid reserved value: '{raw_sdo[4:8].hex()}'")

    @property
    def index(self):
        return self.__index


class SDOSegmentData:
    """
    This class is used by the SDO parser to parse the SDO segment message containing data

    This message type is the segment message sent from the server during an SDO Download
    and the segment message sent from the client during an SDO Upload

    The SDO segment message should match the below format:

    .. code-block:: python


        +----------------------+--------------------------+
        | ccs/scs  t   n    c  |        seg-data          |
        |  7_5     4  3_1   0  |                          |
        +----------------------+--------------------------+
                    0           1                        7

    Definitions
    ===========
    * **ccs**: client command specifier
     0. download segment request

    * **scs**: server command specifier
     0. upload segment response

    * **seg-data**: At most 7 bytes of segment data to be downloaded

    * **n**: number of bytes in seg-data that do not contain data

    * **c**: indicates whether there are still more segments to be downloaded
     0. more segments to be downloaded
     1. no more segments to be downloaded

    * **t**: toggle bit. This bit shall alternate for each subsequent segment that is downloaded. The first segment
    shall be 0. The toggle but shall equal for the request and response message.
        """

    def __init__(self, raw_sdo: bytes):
        self.__more_segments = None
        self.__n = None
        self.__data = None
        self.__toggle_bit = None

        self.__decode_first_section(raw_sdo[0])
        self.__decode_data(raw_sdo[4:8])

    @property
    def more_segments(self):
        return self.__more_segments

    @property
    def n(self):
        return self.__n

    @property
    def data(self):
        return self.__data

    @property
    def toggle_bit(self):
        return self.__toggle_bit

    def __decode_first_section(self, byte_value):
        self.__toggle_bit = byte_value & 0x10

        self.__n = (byte_value & 0x0E) >> 1

        if byte_value & 0x01 > 0:
            self.__more_segments = False
        else:
            self.__more_segments = True

    def __decode_data(self, byte_value: bytes):
        self.__data = int.from_bytes(byte_value[0:6 - self.__n], "big").to_bytes(7, "big")
        if self.__n > 0:
            if int.from_bytes(byte_value[6 - self.__n:6], "big") > 0:
                raise ValueError(f"Data value larger than size: '{byte_value.hex()}'")


class SDOSegmentNoData:
    """
    This class is used by the SDO parser to parse the SDO segment message containing no data

    This message type is the segment message sent from the server during an SDO Upload
    and the segment message sent from the client during an SDO Download

    The SDO segment message should match the below format:

.. code-block:: python

    +----------------------+--------------------------+
    | ccs/scs  t     x     |          reserved        |
    |  7_5     4    3_0    |                          |
    +----------------------+--------------------------+
                0           1                        7

Definitions
===========
* **ccs**: client command specifier
 3. upload segment request

* **scs**: server command specifier
 1. download segment response

* **t**: toggle bit. This bit shall alternate for each subsequent segment that is downloaded. The first segment shall be
0. The toggle but shall equal for the request and response message.

* **x**: not used, always 0

* **reserved**: reserved for further use, always 0
    """

    def __init__(self, raw_sdo: bytes):
        self.__toggle_bit = raw_sdo[0] & 0x10
        if raw_sdo[0] & 0x0F > 0:
            raise ValueError(f"Invalid x value (4_0): '{hex(raw_sdo[0] & 0x1F)}'")

        if int.from_bytes(raw_sdo[4:8], "big") > 0:
            raise ValueError(f"Invalid data value: '{raw_sdo[4:8].hex()}")

    @property
    def toggle_bit(self):
        return self.__toggle_bit


class SDOParser:
    """Sub-Parser for SDO messages
    The SDO parser will parse SDO download initiate and segment messages following the CANopen protocol

    Use the parse function for parsing 8-byte SDO messages

    Once the transfer is complete (is_complete() returns true) the object should be thrown away
    """

    def __init__(self):
        self.__dataSize = None
        self.__inProgressName = None
        self.__inProgressType = None
        self.__data_toggle = False
        self.__no_data_toggle = False
        self.__data = b''
        self.__is_complete = False
        self.__is_expedited = False
        self.__more_segments = True

    @property
    def is_complete(self):
        return self.__is_complete

    def parse(self, cob_id, eds, data: bytes):
        if 0x580 <= cob_id < 0x600:
            sdo_type = SDO_TX
        elif 0x600 <= cob_id < 0x680:
            sdo_type = SDO_RX
        else:
            raise ValueError(f"Provided COB-ID {hex(cob_id)} is outside of the range of SDO messages")

        command_specifier = data[0] & 0xE0
        if (sdo_type == SDO_RX and command_specifier == 0x20) or (sdo_type == SDO_TX and command_specifier == 0x40):
            return self.__parse_initiate_data(data, eds, sdo_type)
        elif (sdo_type == SDO_RX and command_specifier == 0x40) or (sdo_type == SDO_TX and command_specifier == 0x60):
            return self.__parse_initiate_no_data(data, eds)
        elif (sdo_type == SDO_RX and command_specifier == 0x00) or (sdo_type == SDO_TX and command_specifier == 0x00):
            if self.__inProgressName is None:
                raise ValueError(f"SDO Segment received before initiate")
            return self.__parse_segment_data(data, sdo_type)
        elif (sdo_type == SDO_RX and command_specifier == 0x60) or (sdo_type == SDO_TX and command_specifier == 0x20):
            if self.__inProgressName is None:
                raise ValueError(f"SDO Segment received before initiate")
            return self.__parse_segment_no_data(data)
        else:
            raise ValueError(
                f"Provided COB-ID {hex(cob_id)} ({sdo_type}) and command specifier {hex(command_specifier)}"
                f" combination does not result in a valid message type")

    def __parse_initiate_data(self, data, eds, sdo_type):
        current_download_initiate = SDOInitiateData(data)
        if self.__inProgressName is None:
            self.__set_name(eds, current_download_initiate.index)

        if current_download_initiate.is_expedited:
            self.__data = current_download_initiate.data
            self.__is_expedited = True
            """If expedited SDO upload, this is complete"""
            if sdo_type == SDO_TX:
                self.__is_complete = True

            return self.__decode()

        if current_download_initiate.size_indicator:
            self.__dataSize = current_download_initiate.data

        return "Initiating block download - " + self.__inProgressName

    def __parse_initiate_no_data(self, data, eds):
        current_download_initiate = SDOInitiateNoData(data)
        if self.__inProgressName is None:
            self.__set_name(eds, current_download_initiate.index)

        if self.__is_expedited:
            self.__is_complete = True
            return self.__decode()

        return self.__inProgressName + " 0%"

    def __parse_segment_data(self, data, sdo_type):
        download_segment = SDOSegmentData(data)
        self.__more_segments = download_segment.more_segments
        """If no more segments and SDO upload, set complete"""
        if not self.__more_segments and sdo_type == SDO_TX:
            self.__is_complete = True

        if download_segment.toggle_bit == self.__data_toggle:
            raise ValueError(f"Invalid Valid Client Toggle {not self.__data_toggle} expected")

        self.__data_toggle = download_segment.toggle_bit
        self.__data += download_segment.data

        if not download_segment.more_segments:
            return "Block download done - " + self.__inProgressName
        else:
            return "Block downloading - " + self.__inProgressName

    def __parse_segment_no_data(self, data):
        download_segment = SDOSegmentNoData(data)
        if download_segment.toggle_bit == self.__no_data_toggle:
            raise ValueError(f"Invalid Toggle bit {not self.__no_data_toggle} expected")

        self.__no_data_toggle = download_segment.toggle_bit
        if not self.__more_segments:
            result = self.__inProgressName + " 100%"
            self.__is_complete = True
            return result
        else:
            if self.__dataSize is not None:
                percent = str(round((len(data) / self.__dataSize) * 100, 1))
                return self.__inProgressName + " " + percent + "%"
            else:
                return self.__inProgressName + " XXX%"

    def __set_name(self, eds, index: bytes):
        key = int(index[:2].hex())
        subindex_key = int(index[2:3].hex())
        result = eds[key].parameter_name

        if eds[key].sub_indices is not None:
            result += " " + eds[key].sub_indices[subindex_key].parameter_name
            self.__inProgressType = eds[key].sub_indices[subindex_key].data_type
        else:
            self.__inProgressType = eds[key].data_type

        self.__inProgressName = result

    def __decode(self):
        if self.__inProgressType in (UNSIGNED8, UNSIGNED16, UNSIGNED32, UNSIGNED64):
            result = str(int.from_bytes(self.__data, byteorder="big", signed=False))
        elif self.__inProgressType in (INTEGER8, INTEGER16, INTEGER32, INTEGER64):
            result = str(int.from_bytes(self.__data, byteorder="big", signed=True))
        elif self.__inProgressType == BOOLEAN:
            if int.from_bytes(self.__data, byteorder="big", signed=False) > 0:
                result = str(True)
            else:
                result = str(False)
        elif self.__inProgressType in (REAL32, REAL64):
            result = str(unpack('>f', self.__data)[0])
        elif self.__inProgressType == VISIBLE_STRING:
            result = self.__data.decode('utf-8')
        elif self.__inProgressType in (OCTET_STRING, DOMAIN):
            result = self.__data.hex()
        elif self.__inProgressType == UNICODE_STRING:
            result = self.__data.decode('utf-16-be')
        else:
            raise ValueError(f"Invalid data type {self.__inProgressType}. Unable to decode data {self.__data.hex()}")

        return "Downloaded - " + self.__inProgressName + ": " + result
