from __future__ import annotations
from ..canmsgs import CANMsgTable
import curses
import typing


class Pane(typing.ABCMeta):
    def __init__(self: Pane, capacity: int = None):
        self.__pad = curses.newpad(0, 0)
        self.__cols = {}
        self.__table = CANMsgTable(capacity=capacity)

    @typing.abstractmethod
    def draw(self: Pane):
        ...

    @typing.abstractmethod
    def add(self: Pane, msg):
        ...


class HeartBeatPane(Pane):
    def __init__(self: MiscPane):
        self.__cols['COB ID'] = ('arb_id', 0)


class MiscPane(Pane):
    def __init__(self: MiscPane):
        self.__cols += [
            "COB ID",
            "Message"
        ]
