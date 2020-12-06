from __future__ import annotations
import curses
import meta


class Pane(meta.ABC):
    def __init__(self: Pane):
        self.__pad = curses.newpad(0, 0)
        self.__cols = {}

    @meta.abstractmethod
    def draw(self: Pane):
        ...

    @meta.abstractmethod
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
