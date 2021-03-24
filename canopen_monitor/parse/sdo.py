import array
from .eds import EDS
from .utilities import FailedValidationError, get_name, decode
from typing import List
from ..can import MessageType

SDO_TX = 'SDO_TX'
SDO_RX = 'SDO_RX'


class SDOInitiateData:
    """
    This class is used by the SDO parser to parse the SDO initiate messages
    containing data

 This message type is the first message sent from the client during an SDO
 Download and the first message sent from the server during an SDO Upload

 It will contain the data to be downloaded or provide information about the
 segments to be downloaded

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

 * **m**: multiplexer. It represents the index/sub-index of the data to be
 transferred

 * **d**: data
  * e = 0, s = 0: d is reserved for further use
  * e = 0, s = 1: d contains the number of bytes to be downloaded
  * e = 1, s = 1: d contains the data of length 4-n to be downloaded
  * e = 1, s = 0: d contains unspecified number of bytes to be downloaded

 * **x**: not used, always 0
     """

    def __init__(self, raw_sdo: List[int]):
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
            raise ValueError(f"Invalid x value in byte 0, bit 4: "
                             f"{str(byte_value & 0x10)}, expected 0")

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
            raise ValueError(f"Invalid n value in byte 0, bit 3-2: "
                             f"'{str(byte_value & 0x0C)}, expected 0")
        else:
            self.__n = 0

    def __decode_data(self, byte_value: List[int]):
        if not self.__is_expedited:
            if self.__size_indicator:
                self.__data = byte_value
            elif int.from_bytes(byte_value, "big") > 0:
                raise ValueError(f"Invalid data value in bytes 4-7: "
                                 f"'{str(byte_value)}, expected > 0")
        # Expedited Transfer
        else:
            if self.__size_indicator:
                self.__data = byte_value[3 - self.__n:4]
                if int.from_bytes(byte_value[0:3 - self.__n], "big") > 0:
                    raise ValueError(f"Invalid data value in bytes 4-7: "
                                     f"'{str(byte_value)} larger than size: "
                                     f"'{self.__n}'")
            else:
                self.__data = byte_value


class SDOInitiateNoData:
    """
    This class is used by the SDO parser to parse the SDO initiate messages
    containing no data

 This message type is the first message sent from the server during an SDO
 Download and the first message sent from the client during an SDO Upload

 It will contain the data to be downloaded or provide information about the
 segments to be downloaded

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

    def __init__(self, raw_sdo: List[int]):
        self.__index = raw_sdo[1:4]
        if raw_sdo[0] & 0x1F > 0:
            raise ValueError(f"Invalid x value (4_0): "
                             f"'{str(raw_sdo[0] & 0x1F)}'")
        if int.from_bytes(raw_sdo[4:8], "big") > 0:
            bytes = list(map(lambda x: hex(x), raw_sdo[4:8]))
            raise ValueError(f"Invalid reserved value: "
                             f"'{bytes}'")

    @property
    def index(self):
        return self.__index


class SDOSegmentData:
    """
    This class is used by the SDO parser to parse the SDO segment message
    containing data

    This message type is the segment message sent from the server during an
    SDO Download and the segment message sent from the client during an SDO
    Upload

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

    * **t**: toggle bit. This bit shall alternate for each subsequent segment
    that is downloaded. The first segment shall be 0. The toggle but shall
    equal for the request and response message.
    """

    def __init__(self, raw_sdo: List[int]):
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

    def __decode_data(self, byte_value: List[int]):
        value = byte_value[0:6 - self.__n]
        self.__data = int.from_bytes(value, "big").to_bytes(7, "big")
        if self.__n > 0:
            if int.from_bytes(byte_value[6 - self.__n:6], "big") > 0:
                raise ValueError(f"Data value larger than size: "
                                 f"'{str(byte_value)}'")


class SDOSegmentNoData:
    """
    This class is used by the SDO parser to parse the SDO segment message
    containing no data

    This message type is the segment message sent from the server during an
    SDO Upload and the segment message sent from the client during an SDO
    Download

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

* **t**: toggle bit. This bit shall alternate for each subsequent segment
that is downloaded. The first segment shall be 0. The toggle but shall equal
for the request and response message.

* **x**: not used, always 0

* **reserved**: reserved for further use, always 0
    """

    def __init__(self, raw_sdo: List[int]):
        self.__toggle_bit = raw_sdo[0] & 0x10
        if raw_sdo[0] & 0x0F > 0:
            raise ValueError(f"Invalid x value (4_0): "
                             f"'{str(raw_sdo[0] & 0x1F)}'")

        if int.from_bytes(raw_sdo[4:8], "big") > 0:
            raise ValueError(f"Invalid data value: "
                             f"'{str(raw_sdo[4:8])}")

    @property
    def toggle_bit(self):
        return self.__toggle_bit


class SDOBlockInitiateData:
    """
    This class is used by the SDO parser to parse the SDO block initiate
    messages containing data

This message type is the first message sent from the client during an SDO
Download and the first message sent from the server during an SDO Upload

It will contain information about the blocks to be downloaded

The SDO Block initiate message with data should match the below format:


.. code-block:: python


    +---------------------------------+---------+----------------+
    | ccs/scs  x   sc/cc   s   ss/cs  |    m    |      size      |
    |  7_5    4_3    2     1     0    |         |                |
    +---------------------------------+---------+----------------+
                   0                    1     3   4             7

Definitions
===========
* **ccs**: client command specifier
 6. block download

* **scs**: server command specifier
 6. block upload

* **cc/sc**: client/server CRC support
 0. Client/Server does not support generating CRC on data
 1. Client/Server supports generating CRC on data

* **s**: size indicator
 0. data set size is not indicated
 1. data set size is indicated

* **cs**: client subcommand
 0. Initiate download request

* **ss**: server subcommand
 0. Initiate upload response

* **m**: multiplexer. It represents the index/sub-index of the data to be
transferred

* **size**: download size in bytes
 * s = 0: size is reserved for further use, always 0
 * s = 1: size contains the number of bytes to be downloaded

* **x**: not used, always 0
    """

    def __init__(self, raw_sdo: List[int]):
        self.__command_specifier = raw_sdo[0] & 0xE0
        self.__x = raw_sdo[0] & 0x18
        if self.__x > 0:
            raise ValueError(f"Invalid x value (4_3): '{str(self.__x)}'")
        self.__supports_crc = raw_sdo[0] & 0x04 > 0
        self.__size_indicated = raw_sdo[0] & 0x02 > 0
        self.__subcommand = raw_sdo[0] & 0x01
        self.__index = raw_sdo[1:4]
        self.__size = raw_sdo[4:8]

    @property
    def command_specifier(self):
        return self.__command_specifier

    @property
    def supports_crc(self):
        return self.__supports_crc

    @property
    def size_indicated(self):
        return self.__size_indicated

    @property
    def subcommand(self):
        return self.__subcommand

    @property
    def index(self):
        return self.__index

    @property
    def size(self):
        return self.__size


class SDOBlockInitiateNoData:
    """
    This class is used by the SDO parser to parse the SDO block initiate
    messages containing no data

This message type is the first message sent from the server during an SDO
Download and not used as part of the SDO Block Upload

It will contain information about the number of blocks to be downloaded
before a confirmation is returned

The SDO block initiate message with no data should match the below format:


.. code-block:: python


    +-------------------------------+---------+---------------------+
    | ccs/scs  x   cc/sc    ss/cs   |    m    | blksize |  reserved |
    |  7_5    4_3    2       1_0    |         |         |           |
    +-------------------------------+---------+---------------------+
                   0                 1     3       4     5        7

Definitions
===========
* **ccs**: client command specifier
 6. block download

* **cc/sc**: client/server CRC support
 0. Client does not support generating CRC on data
 1. Client supports generating CRC on data

* **ss**: server subcommand
 0. initiate download response

* **m**: multiplexer. It represents the index/sub-index of the data to be
transferred

* **blksize**: Number of segments per block that shall be used by the client
for the following block download with 0 < blksize < 128

* **reserved**: reserved for further use, always 0
    """

    def __init__(self, raw_sdo: List[int]):
        self.__command_specifier = raw_sdo[0] & 0xE0
        self.__x = raw_sdo[0] & 0x18
        if self.__x > 0:
            raise ValueError(f"Invalid x value (4_3): '{str(self.__x)}'")
        self.__supports_crc = raw_sdo[0] & 0x04 > 0
        self.__subcommand = raw_sdo[0] & 0x03
        self.__index = raw_sdo[1:4]
        self.__blksize = raw_sdo[4]
        self.__reserved = raw_sdo[5:8]
        if int.from_bytes(self.__reserved, "big") > 0:
            raise ValueError(f"Invalid reserved value: "
                             f"'{str(self.__reserved)}'")

    @property
    def command_specifier(self):
        return self.__command_specifier

    @property
    def supports_crc(self):
        return self.__supports_crc

    @property
    def subcommand(self):
        return self.__subcommand

    @property
    def index(self):
        return self.__index

    @property
    def blksize(self):
        return self.__blksize


class SDOBlockUploadInitiateNoData:
    """
    This class is used by the SDO parser to parse the SDO block initiate
    messages containing no data when uploading

This message type is the first message sent from the client during an SDO
Upload

This message contains information about the number of blocks that the client
expects before returning a confirmation

The difference between this message and the Download Initiate no data message
is that this one includes pst (protocol switch threshold)

The SDO upload block initiate message with no data should match the below
format:


.. code-block:: python


    +-------------------------------+---------+----------------+------------+
    |  ccs     x     cc       cs    |    m    | blksize |  pst |  reserved  |
    |  7_5    4_3    2       1_0    |         |         |      |            |
    +-------------------------------+---------+---------+------+------------+
                   0                 1     3       4       5     6         7

Definitions
===========
* **ccs**: client command specifier
 5. block upload

* **cc**: client CRC support
 0. Client does not support generating CRC on data
 1. Client supports generating CRC on data

* **cs**: client subcommand
 0. initiate upload request

* **m**: multiplexer. It represents the index/sub-index of the data to be
transferred

* **blksize**: Number of segments per block that shall be used by the client
for the following block download with 0 < blksize < 128

* **pst**: protocol switch threshold in bytes to change the SDO transfer
protocol

 0. Change of transfer protocol not allowed
 >0. If the size of the data in bytes is less or equal pst the server may
 switch to the SDO upload protocol by transmitting the server response of the
 protocol SDO upload as described in sub-clause 7.2.4.3.5.

* **reserved**: reserved for further use, always 0
    """

    def __init__(self, raw_sdo: List[int]):
        self.__command_specifier = raw_sdo[0] & 0xE0
        self.__x = raw_sdo[0] & 0x18
        if self.__x > 0:
            raise ValueError(f"Invalid x value (4_3): '{str(self.__x)}'")
        self.__supports_crc = raw_sdo[0] & 0x04 > 0
        self.__subcommand = raw_sdo[0] & 0x03
        self.__index = raw_sdo[1:4]
        self.__blksize = raw_sdo[4]
        self.__pst = raw_sdo[5]
        self.__reserved = raw_sdo[6:8]
        if int.from_bytes(self.__reserved, "big") > 0:
            raise ValueError(f"Invalid reserved value: "
                             f"'{str(self.__reserved)}'")

    @property
    def command_specifier(self):
        return self.__command_specifier

    @property
    def supports_crc(self):
        return self.__supports_crc

    @property
    def subcommand(self):
        return self.__subcommand

    @property
    def index(self):
        return self.__index

    @property
    def blksize(self):
        return self.__blksize

    @property
    def pst(self):
        return self.__pst


class SDOBlockSegmentData:
    """
This class is used by the SDO parser to parse the SDO block's segment messages
containing data

This message type is the first message sent from the client during an SDO
Download and the first message sent from the server during an SDO Upload

It will contain a segment of data to be downloaded

The SDO block segment message with data should match the below format:


.. code-block:: python


    +------------------------------------------------------+
    |   c       seqno       |          seg-data            |
    |   7        6_0        |                              |
    +------------------------------------------------------+
                0             1                           7

Definitions
===========
* **c**: indicates whether there are still more segments to be downloaded
 0. more segments to be downloaded
 1. no more segments to be downloaded, enter SDO block download end phase

* **seqno**: sequence number of segment 0 < seqno < 128.

* **seg-data**: at most 7 bytes of segment data to be downloaded.
    """

    def __init__(self, raw_sdo: List[int]):
        self.__more_segments = raw_sdo[0] & 0x80 == 0
        self.__seqno = raw_sdo[0] & 0x7F
        self.__data = raw_sdo[1:8]

    @property
    def more_segments(self):
        return self.__more_segments

    @property
    def seqno(self):
        return self.__seqno

    @property
    def data(self):
        return self.__data


class SDOBlockSegmentNoData:
    """
This class is used by the SDO parser to parse the SDO block segment messages
containing no data

This message type is sent from the server during an SDO Download
and sent from the client during an SDO Upload

This message is used to indicate the last message that was received successfully

The SDO block segment message with no data should match the below format:

.. code-block:: python


    +-------------------------+---------+---------------------+
    | ccs/scs    x    ss/cs   |  ackseq | blksize |  reserved |
    |  7_5      4_2    1_0    |         |         |           |
    +-------------------------+---------+---------+-----------+
                   0               1         2      3        7

Definitions
===========
* **ccs**: client command specifier
 1. download segment response

* **scs**: server command specifier
 5. block download

* **cs**: client subcommand
 0. This section contains x data on upload

* **ss**: server subcommand
 2. block download response

* **ackseq**: sequence number of last segment that was received successfully
during the last block download. If ackseq is set to 0 the server indicates
the client that the segment with the sequence number 1 was not received
correctly and all segments shall be retransmitted by the client.

* **blksize**: Number of segments per block that shall be used by the client
for the following block download with 0 < blksize < 128

* **x**: not used, always 0

* **reserved**: reserved for further use, always 0
    """

    def __init__(self, raw_sdo: List[int]):
        self.__command_specifier = raw_sdo[0] & 0xE0
        self.__x = raw_sdo[0] & 0x1C
        if self.__x > 0:
            raise ValueError(f"Invalid x value (4_2): '{str(self.__x)}'")
        self.__subcommand = raw_sdo[0] & 0x03
        self.__ackseq = raw_sdo[1]
        self.__blksize = raw_sdo[2]
        self.__reserved = raw_sdo[3:8]
        if int.from_bytes(self.__reserved, "big") > 0:
            raise ValueError(f"Invalid reserved value: "
                             f"'{str(self.__reserved)}'")

    @property
    def command_specifier(self):
        return self.__command_specifier

    @property
    def subcommand(self):
        return self.__subcommand

    @property
    def ackseq(self):
        return self.__ackseq

    @property
    def blksize(self):
        return self.__blksize


class SDOBlockEndData:
    """
    This class is used by the SDO parser to parse the SDO block end message
    containing the checksum data

This message type is sent from the client during an SDO Download
and sent from the server during an SDO Upload

This message is sent after ending the block transfer and includes a checksum
which can be used to verify the integrity of the data transfer

The SDO block end message with data should match the below format:

.. code-block:: python


    +-------------------------+---------+-----------------+
    | ccs/scs    n     ss/cs  |   crc   |    reserved     |
    |  7_5      4_2     1_0   |         |                 |
    +-------------------------+---------+-----------------+
                   0             1      2   3              7

Definitions
===========
* **ccs**: client command specifier
 6. Block Download

* **scs**: server command specifier
 6. Block Upload

* **n**: indicates the number of bytes in the last segment of the last block
that do not contain data. Bytes [8-n, 7] do not contain segment data.

* **cs**: client subcommand
 1. End block download request

* **ss**: server subcommand
 1. End block upload response

* **crc**: 16 bit cyclic redundancy checksum (CRC) for the data set. The
algorithm for generating the CRC is described in sub-clause 7.2.4.3.16. CRC
is only valid if in SDO block download initiate cc and sc are set to 1
otherwise CRC shall be set to 0.

* **x**: not used, always 0

* **reserved**: reserved for further use, always 0
    """

    def __init__(self, raw_sdo: List[int]):
        self.__command_specifier = raw_sdo[0] & 0xE0
        self.__n = raw_sdo[0] & 0x1C
        self.__x = raw_sdo[0] & 0x02
        if self.__x > 0:
            raise ValueError(f"Invalid x value (1): '{str(self.__x)}'")
        self.__subcommand = raw_sdo[0] & 0x01
        self.__crc = raw_sdo[1:3]
        self.__reserved = raw_sdo[3:8]
        if int.from_bytes(self.__reserved, "big") > 0:
            raise ValueError(f"Invalid reserved value: "
                             f"'{str(self.__reserved)}'")

    @property
    def command_specifier(self):
        return self.__command_specifier

    @property
    def n(self):
        return self.__n

    @property
    def subcommand(self):
        return self.__subcommand

    @property
    def crc(self):
        return self.__crc


class SDOBlockEndNoData:
    """
    This class is used by the SDO parser to parse the SDO block end message
    containing no data

This message type is sent from the server during an SDO Download
and sent from the client during an SDO Upload

This message is sent after ending the block transfer

The SDO block end message with no data should match the below format:

.. code-block:: python


    +------------------------+------------------+
    | ccs/scs    x    ss/cs  |     reserved     |
    |  7_5      4_2    1_0   |                  |
    +------------------------+------------------+
                 0            1                7

Definitions
===========
* **ccs**: client command specifier
 5. Block Upload

* **scs**: server command specifier
 5. Block Download

* **n**: indicates the number of bytes in the last segment of the last block
that do not contain data. Bytes [8-n, 7] do not contain segment data.

* **cs**: client subcommand
 3. start upload

* **ss**: server subcommand
 1. End block download request

* **x**: not used, always 0

* **reserved**: reserved for further use, always 0
    """

    def __init__(self, raw_sdo: List[int]):
        self.__command_specifier = raw_sdo[0] & 0xE0
        self.__x = raw_sdo[0] & 0x1C
        if self.__x > 0:
            raise ValueError(f"Invalid x value (1): '{str(self.__x)}'")
        self.__subcommand = raw_sdo[0] & 0x03
        self.__reserved = raw_sdo[1:8]
        if int.from_bytes(self.__reserved, "big") > 0:
            raise ValueError(f"Invalid reserved value: "
                             f"'{str(self.__reserved)}'")

    @property
    def command_specifier(self):
        return self.__command_specifier

    @property
    def subcommand(self):
        return self.__subcommand


class SDOParser:
    """Sub-Parser for SDO messages The SDO parser will parse SDO download
    initiate and segment messages following the CANopen protocol

    Use the parse function for parsing 8-byte SDO messages

    Once the transfer is complete (is_complete() returns true) the object
    should be thrown away
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

        # Added for Block Segments
        self.__block_download = False
        self.__block_size = 1
        self.__last_sequence = 0
        self.__awaiting_conf = False

    @property
    def is_complete(self):
        return self.__is_complete

    def parse(self, cob_id: int, data: List[int], eds: EDS):
        node_id = None
        try:
            if cob_id in range(*MessageType.SDO_TX.value):
                sdo_type = SDO_TX
                node_id = cob_id - MessageType.SDO_TX.value[0]
            elif cob_id in range(*MessageType.SDO_RX.value):
                sdo_type = SDO_RX
                node_id = cob_id - MessageType.SDO_RX.value[0]
            else:
                raise ValueError(f"Provided COB-ID {str(cob_id)} "
                                 f"is outside of the range of SDO messages")

            if len(data) != 8:
                raise FailedValidationError(data, node_id, cob_id, __name__,
                                            f"Invalid SDO payload length, "
                                            f"expected 8, received {len(data)}")

            if self.__block_download:
                if self.__inProgressName is None:
                    self.__inProgressName = ""
                return self.__parse_block_data(data)

            if self.__awaiting_conf:
                if self.__inProgressName is None:
                    self.__inProgressName = ""
                return self.__parse_block_no_data(data)

            command_specifier = data[0] & 0xE0
            if (sdo_type == SDO_RX and command_specifier == 0x20) or (
                    sdo_type == SDO_TX and command_specifier == 0x40):

                return self.__parse_initiate_data(data, eds, sdo_type)

            elif (sdo_type == SDO_RX and command_specifier == 0x40) or (
                    sdo_type == SDO_TX and command_specifier == 0x60):

                return self.__parse_initiate_no_data(data, eds)

            elif (sdo_type == SDO_RX and command_specifier == 0x00) or (
                    sdo_type == SDO_TX and command_specifier == 0x00):

                if self.__inProgressName is None:
                    raise ValueError("SDO Segment received before initiate")

                return self.__parse_segment_data(data, sdo_type)

            elif (sdo_type == SDO_RX and command_specifier == 0x60) or (
                    sdo_type == SDO_TX and command_specifier == 0x20):

                if self.__inProgressName is None:
                    raise ValueError("SDO Segment received before initiate")

                return self.__parse_segment_no_data(data)

            elif (sdo_type == SDO_RX and command_specifier == 0xE0) or (
                    sdo_type == SDO_TX and command_specifier == 0xE0):

                return self.__parse_block_initiate_data(data, eds)

            elif sdo_type == SDO_TX and command_specifier == 0xC0:

                subcommand = data[0] & 3
                """Check for upload"""
                if subcommand == 1:
                    return self.__parse_block_end_data(data)

                self.__block_download = True
                return self.__parse_block_initiate_no_data(data, eds)

            elif sdo_type == SDO_RX and command_specifier == 0xC0:
                return self.__parse_block_end_data(data)

            elif sdo_type == SDO_TX and command_specifier == 0xA0:
                return self.__parse_block_end_no_data(data)

            elif sdo_type == SDO_RX and command_specifier == 0xA0:
                subcommand = data[0] & 3

                """Check for upload"""
                if subcommand == 1:
                    return self.__parse_block_end_no_data(data)
                return self.__parse_block_upload_initiate_no_data(data, eds)

            else:
                raise ValueError(
                    f"Provided COB-ID {str(cob_id)} ({sdo_type}) and command "
                    f"specifier {str(command_specifier)} combination does "
                    f"not result in a valid message type")

        except ValueError as error:
            raise FailedValidationError(data, node_id, cob_id, __name__,
                                        str(error))

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

            return f"Downloaded - {self.__inProgressName}: " \
                   f"{decode(self.__inProgressType, self.__data)}"

        if current_download_initiate.size_indicator:
            self.__dataSize = int.from_bytes(current_download_initiate.data,
                                             "big")

        return "Initiating block download - " + self.__inProgressName

    def __parse_initiate_no_data(self, data, eds):
        current_download_initiate = SDOInitiateNoData(data)
        if self.__inProgressName is None:
            self.__set_name(eds, current_download_initiate.index)

        if self.__is_expedited:
            self.__is_complete = True
            return f"Downloaded - {self.__inProgressName}: " \
                   f"{decode(self.__inProgressType, self.__data)}"

        return self.__inProgressName + " 0%"

    def __parse_segment_data(self, data, sdo_type):
        download_segment = SDOSegmentData(data)
        self.__more_segments = download_segment.more_segments
        """If no more segments and SDO upload, set complete"""
        if not self.__more_segments and sdo_type == SDO_TX:
            self.__is_complete = True

        if download_segment.toggle_bit == self.__data_toggle:
            raise ValueError(f"Invalid Valid Client Toggle "
                             f"{not self.__data_toggle} expected")

        self.__data_toggle = download_segment.toggle_bit
        self.__data += download_segment.data

        if not download_segment.more_segments:
            return "Block download done - " + self.__inProgressName
        else:
            return "Block downloading - " + self.__inProgressName

    def __parse_segment_no_data(self, data):
        download_segment = SDOSegmentNoData(data)
        if download_segment.toggle_bit == self.__no_data_toggle:
            raise ValueError(
                f"Invalid Toggle bit {not self.__no_data_toggle} expected")

        self.__no_data_toggle = download_segment.toggle_bit
        if not self.__more_segments:
            result = self.__inProgressName + " 100%"
            self.__is_complete = True
            return result
        else:
            if self.__dataSize is not None:
                percent = len(data) / self.__dataSize
                percent = str(round(percent * 100, 1))
                return self.__inProgressName + " " + percent + "%"
            else:
                return self.__inProgressName + " XXX%"

    def __parse_block_initiate_data(self, data, eds):
        current_download_initiate = SDOBlockInitiateData(data)
        if self.__inProgressName is None:
            self.__set_name(eds, current_download_initiate.index)

        if current_download_initiate.size_indicated:
            self.__dataSize = int.from_bytes(current_download_initiate.size,
                                             "big")

        return "Initiating block download - " + self.__inProgressName

    def __parse_block_initiate_no_data(self, data, eds):
        current_download_initiate = SDOBlockInitiateNoData(data)
        if self.__inProgressName is None:
            self.__set_name(eds, current_download_initiate.index)

        self.__block_size = current_download_initiate.blksize

        return self.__inProgressName + " 0%"

    def __parse_block_upload_initiate_no_data(self, data, eds):
        current_download_initiate = SDOBlockUploadInitiateNoData(data)
        if self.__inProgressName is None:
            self.__set_name(eds, current_download_initiate.index)

        self.__block_size = current_download_initiate.blksize

        return self.__inProgressName + " 0%"

    def __parse_block_data(self, data):
        download_segment = SDOBlockSegmentData(data)
        self.__block_download = download_segment.more_segments
        self.__last_sequence = download_segment.seqno

        if self.__last_sequence % self.__block_size == 0:
            self.__awaiting_conf = True

        self.__data += array.array('B', download_segment.data)

        return "Block downloading - " + self.__inProgressName

    def __parse_block_no_data(self, data):
        # download_segment = SDOBlockSegmentNoData(data)  # Unused
        self.__awaiting_conf = False
        if not self.__last_sequence:
            self.__block_download = True

        if self.__dataSize is not None:
            percent = str(round((len(data) / self.__dataSize) * 100, 1))
            return self.__inProgressName + " " + percent + "%"
        else:
            return self.__inProgressName + " XXX%"

    def __parse_block_end_data(self, data):
        # download_segment = SDOBlockEndData(data)  # Unused

        if self.__inProgressName is not None:
            return self.__inProgressName + " 100%"
        else:
            return "100%"

    def __parse_block_end_no_data(self, data):
        download_segment = SDOBlockEndNoData(data)

        """On upload confirmation"""
        if download_segment.subcommand == 3:
            self.__block_download = True
            return "Initiating block download - " + self.__inProgressName

        self.__is_complete = True

        return "Block download done - " + self.__inProgressName

    def __set_name(self, eds, index: List[int]):
        try:
            values = get_name(eds, index)
        except TypeError:
            raise ValueError(f"Unable to eds content at index {str(index)}")

        self.__inProgressType = values[0]
        self.__inProgressName = values[1]
