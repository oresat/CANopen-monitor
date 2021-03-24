from __future__ import annotations
import datetime as dt
from enum import Enum
from pyvit.can import Frame

STALE_TIME = dt.timedelta(minutes=2)
DEAD_TIME = dt.timedelta(minutes=4)


class MessageType(Enum):
    """This enumeration describes all of the ranges in the CANOpen spec that
    defines specific kinds of messages.

    See `wikipedia
    <https://en.wikipedia.org/wiki/CANopen#Predefined_Connection_Set>`_
    for details
    """
    # Regular CANOpen message types
    NMT = (0x0, 0x0)
    SYNC = (0x1, 0x7F)
    TIME = (0x100, 0x100)
    EMER = (0x80, 0x0FF)
    PDO1_TX = (0x180, 0x1FF)
    PDO1_RX = (0x200, 0x27F)
    PDO2_TX = (0x280, 0x2FF)
    PDO2_RX = (0x300, 0x37F)
    PDO3_TX = (0x380, 0x3FF)
    PDO3_RX = (0x400, 0x47F)
    PDO4_TX = (0x480, 0x4FF)
    PDO4_RX = (0x500, 0x57F)
    SDO_TX = (0x580, 0x5FF)
    SDO_RX = (0x600, 0x680)
    HEARTBEAT = (0x700, 0x7FF)

    # Special Types
    UKNOWN = (-0x1, -0x1)  # Pseudo type unknown
    PDO = (0x180, 0x57F)  # Super type PDO
    SDO = (0x580, 0x680)  # Super type SDO

    def __init__(self, start, end):
        self.start = start
        self.end = end

    @property
    def supertype(self: MessageType) -> MessageType:
        """Determines the "Supertype" of a Message

        There are only two supertypes: MessageType.PDO and MessageType.SDO,
        and they emcompass all of the PDO_T/RX and SDO_T/RX ranges
        respectively. This simply returns which range the type is in if any,
        or MessageType.UNKNOWN if it's in neither supertype range.

        :return: The supertype of this type
        :rtype: MessageType
        """
        if self.PDO.start <= self.start <= self.PDO.end:
            return MessageType['PDO']
        elif self.SDO.start <= self.start <= self.SDO.end:
            return MessageType['SDO']
        else:
            return MessageType['UKNOWN']

    @staticmethod
    def cob_to_node(msg_type: MessageType, cob_id: int) -> int:
        """Determines the Node ID based on the given COB ID

        The COB ID is the raw ID sent with the CAN message, and the node id is
        simply the sub-id within the COB ID, which is used as a device
        identifier.

        :Example:

            If the COB ID is 0x621

            Then the Type is SDO_RX (an SDO being received)

            The start of the SDO_RX range is 0x600

            Therefore the Node ID is 0x621 - 0x600 = 0x21

        :param mtype: The message type
        :type mtype: MessageType

        :param cob_id: The Raw CAN Message COB ID
        :type cob_id: int

        :return: The Node ID
        :rtype: int
        """
        return cob_id - msg_type.start

    @staticmethod
    def cob_id_to_type(cob_id: int) -> MessageType:
        """Determines the message type based on the COB ID

        :param cob_id: The Raw CAN Message COB ID
        :type cob_id: int

        :return: The message type (range) the COB ID fits into
        :rtype: MessageType
        """
        for msg_type in list(MessageType):
            if msg_type.start <= cob_id <= msg_type.end:
                return msg_type
        return MessageType['UKNOWN']

    def __str__(self) -> str:
        return self.name


class MessageState(Enum):
    """This enumeration describes all possible states of a CAN Message

    +-----+----------+
    |State|Age (sec) |
    +=====+==========+
    |ALIVE|x<60      |
    +-----+----------+
    |STALE|60<=x<=120|
    +-----+----------+
    |DEAD |120<=x    |
    +-----+----------+
    """
    ALIVE = 'Alive'
    STALE = 'Stale'
    DEAD = 'Dead'

    def __str__(self: MessageState) -> str:
        return self.value + ' '


class Message(Frame):
    """This class is a wrapper class for the `pyvit.can.Frame` class

    :ref: `See this for documentation on a PyVit Frame
        <https://github.com/linklayer/pyvit/blob/master/pyvit/can.py>`_

    It's primary purpose is to carry all of the same CAN message data as a
    frame, while adding age and state attributes as well.
    """

    def __init__(self: Message, arb_id: int, **kwargs):
        super().__init__(arb_id, **kwargs)
        self.node_name = MessageType.cob_to_node(self.type, self.arb_id)
        self.message = self.data

    @property
    def age(self: Message) -> dt.timedelta:
        """The age of the Message since it was received from the CAN bus

        :return: Age of the message
        :rtype: datetime.timedelta
        """
        return dt.datetime.now() - self.timestamp

    @property
    def state(self: Message) -> MessageState:
        """The state of the message since it was received from the CAN bus

        :return: State of the message
        :rtype: MessageState
        """
        if self.age >= DEAD_TIME:
            return MessageState['DEAD']
        elif self.age >= STALE_TIME:
            return MessageState['STALE']
        else:
            return MessageState['ALIVE']

    @property
    def type(self: Message) -> MessageType:
        """Type of CAN Message

        :return: CAN Message Type
        :rtype: MessageType
        """
        return MessageType.cob_id_to_type(self.arb_id)

    @property
    def supertype(self: Message) -> MessageType:
        """Super-Type of CAN Message

        :return: CAN Message Super-Type
        :rtype: MessageType
        """
        return self.type.supertype

    @property
    def node_id(self: Message) -> int:
        """The Node ID, otherwise known as the unique device identifier

        This is a property that is arbitratily decided in an Object Dictionary
        and can sometimes have a name attatched to it

        .. example::

            0x621 and 0x721 are addressing the same device on the network,
            because both of them share the Node ID of 0x21

        :return: Node ID
        :rtype: int
        """
        return MessageType.cob_to_node(self.type, self.arb_id)

        def __lt__(self: Message, src: Message):
            """Overloaded less-than operator, primarilly to support `sorted()`
            on a list of `Message`, such that it's sorted by COB ID

            :param src: The right-hand message to compare against
            :type src: Message

            .. example::

                self < src
            """
            return self._arb_id < src._arb_id
