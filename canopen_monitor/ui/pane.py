from __future__ import annotations
from ..canmsgs import CANMsgTable, CANMsg, MessageType
from ..parser import CANOpenParser
import curses
from abc import ABC, abstractmethod


class Pane(ABC):
    def __init__(self: Pane, name: str, parser: CANOpenParser, capacity: int =
    None):
        self.pad = curses.newpad(1, 1)
        self.cols = {}
        self.capacity = capacity
        self.table = CANMsgTable(capacity=capacity)
        self.__parser = parser
        self.parent = curses.newwin(0, 0)
        self.name = name

        # Pane states
        self.__needs_refresh = False
        self.__scroll_position_y = 0
        self.__scroll_position_x = 0
        self.selected = False
        self.pad = curses.newpad(1, 1)
        self.pad.scrollok(True)
        self.vwidth = 0

        # Draw Style
        self.__style = curses.color_pair(4)

    @abstractmethod
    def draw(self: Pane):
        height, width = self.parent.getmaxyx()
        y_offset, x_offset = self.parent.getbegyx()

        vheight = len(self.table) + 50
        vheight = height if vheight < height else vheight

        self.vwidth = width if self.vwidth < width else self.vwidth

        self.pad.resize(vheight - 1, self.vwidth)

        if self.__needs_refresh:
            self.clear()

        # needed?
        self.parent.attron(self.__style)
        self.pad.attron(self.__style)

        self.parent.box()
        out_of = '/{}'.format(self.capacity) \
            if self.capacity is not None else ''
        banner = '{} ({}{})'.format(self.name,
                                    len(self.table),
                                    out_of)

        if self.selected:
            self.parent.attron(self.__style | curses.A_REVERSE)

        self.parent.addstr(0, 1, banner)

        self.parent.attroff(self.__style | curses.A_REVERSE)

        # Draw Header
        line = ""
        for col in self.cols:
            line += col.ljust(self.cols[col][1], ' ')

        self.pad.attron(self.__style | curses.A_BOLD)
        self.pad.addstr(0, 1, line)
        self.pad.attroff(self.__style | curses.A_BOLD)
        # self.pad.attron(self.__style)

        for i, arb_id in enumerate(self.table):
            msg = self.table[arb_id]
            attributes = dir(msg)
            line = ""
            for col in self.cols.values():
                if col[0] in attributes:
                    if col[0] == 'arb_id':
                        value = hex(msg.arb_id)
                    else:
                        value = str(getattr(msg, col[0]))
                else:
                    value = "Not Found"

                line += value.ljust(col[1], ' ')

            if len(line) > self.vwidth:
                self.vwidth = len(line) + 2
                self.pad.resize(vheight - 1, self.vwidth)
            if i == self.__scroll_position_y and self.selected:
                self.pad.attron(self.__style | curses.A_REVERSE)
            self.pad.addstr(i + 1, 1, line)
            if i == self.__scroll_position_y and self.selected:
                self.pad.attroff(self.__style | curses.A_REVERSE)
                # self.pad.attron(self.__style)

        self.parent.refresh()

        if self.__scroll_position_y < height - 3:
            scroll_offset_y = 0
        else:
            scroll_offset_y = self.__scroll_position_y - (height - 4)

        if self.__scroll_position_x + width > self.vwidth:
            self.__scroll_position_x = self.vwidth - width

        scroll_offset_x = self.__scroll_position_x

        self.pad.refresh(scroll_offset_y,
                         scroll_offset_x,
                         y_offset + 1,
                         x_offset + 1,
                         y_offset + height - 2,
                         x_offset + width - 2)

    def clear(self):
        self.pad.clear()
        self.parent.clear()
        self.__needs_refresh = False

    @abstractmethod
    def add(self: Pane, msg: CANMsg):
        if self.table is not None:
            msg.parsed_msg = self.__parser.parse(msg)[0]
            self.table += msg
        self.__needs_refresh = True
        ...

    def scroll_up(self, rate=1):
        self.__scroll_position_y -= rate
        if self.__scroll_position_y < 0:
            self.__scroll_position_y = 0

    def scroll_down(self, rate=1):
        self.__scroll_position_y += rate
        if self.__scroll_position_y > len(self.table) - 1:
            self.__scroll_position_y = len(self.table) - 1

    def scroll_left(self, rate=1):
        self.__scroll_position_x -= rate
        if self.__scroll_position_x < 0:
            self.__scroll_position_x = 0

    def scroll_right(self, rate=1):
        self.__scroll_position_x += rate
        if self.__scroll_position_x > self.vwidth:
            self.__scroll_position_x = self.vwidth - 2

class HeartBeatPane(Pane):

    def __init__(self: HeartBeatPane, name, parser: CANOpenParser,
                 capacity: int = None, fields=[], frame_types=[]):
        super().__init__(name, parser, capacity)
        self.cols['COB ID'] = ['arb_id', 0]
        self.cols['Node Name'] = ['node_name', 0]
        self.cols['Interface'] = ['interface', 0]
        self.cols['State'] = ['status', 0]
        self.cols['Status'] = ['parsed_msg', 0]

        # Turn the frame-type strings into enumerations
        self.frame_types = []
        for ft in frame_types:
            self.frame_types.append(MessageType[ft])

        for col in self.cols:
            self.cols[col][1] = len(col) + 2

    def add(self: Pane, msg: CANMsg):
        super().add(msg)
        attributes = dir(msg)
        for col in self.cols.values():
            if col[0] in attributes:
                value = str(getattr(msg, col[0]))
            else:
                value = "Not Found"

            col[1] = len(value) + 2 if len(value) + 2 > col[1] else col[1]

    def draw(self: HeartBeatPane):
        super().draw()


    def has_frame_type(self, frame):
        return frame.message_type in self.frame_types


class MiscPane(HeartBeatPane):
    def __init__(self, name, parser: CANOpenParser, capacity: int = None,
                 fields=[], frame_types=[]):
        super().__init__(name, parser, capacity, fields, frame_types)
        # self.cols += [
        #    "COB ID",
        #    "Message"
        #]


class InfoPane(HeartBeatPane):
    def __init__(self, name, parser: CANOpenParser, capacity: int = None,
                 fields=[], frame_types=[]):
        super().__init__(name, parser, capacity, fields, frame_types)
        # self.cols += [
        #    "COB ID",
        #    "Message"
        #]
