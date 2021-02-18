"""This module is primarily responsible for providing a reliable high-level
interface to the CAN Bus as well as describing the format and structure of raw
CAN messages according to the
`CANOpen spec <https://en.wikipedia.org/wiki/CANopen>`_.
"""
from .message import Message, MessageState, MessageType
from .message_table import MessageTable
from .interface import Interface
from .magic_can_bus import MagicCANBus

__all__ = [
    'Message',
    "MessageState",
    "MessageType",
    "MessageTable",
    'Interface',
    'MagicCANBus',
]
