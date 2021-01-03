from __future__ import annotations
from ..canmsgs import CANMsgTable, CANMsg, MessageType
from ..parser import CANOpenParser
import curses
from abc import ABC, abstractmethod


class Pane(ABC):
    def __init__(self: Pane, border: bool = True, color_pair: int = 4):
        self._pad = curses.newpad(1, 1)
        self.parent = curses.newwin(0, 0)
        self.border = border

        # Pane state
        self._needs_refresh = False
        self._scroll_position_y = 0
        self._scroll_position_x = 0
        self.selected = False
        self._pad.scrollok(True)
        self.v_width = 0
        self.v_height = 0
        self.scroll_limit_y = 0
        self.scroll_limit_x = 0

        # Draw Style
        self._style = curses.color_pair(color_pair)

    @abstractmethod
    def draw(self: Pane):
        if self._needs_refresh:
            self.clear()

        self.parent.attron(self._style)
        self._pad.attron(self._style)

        if self.border:
            self.parent.box()

    def clear(self):
        self._pad.clear()
        self.parent.clear()
        self._needs_refresh = False

    @abstractmethod
    def add(self: Pane, item: any):
        ...

    def scroll_up(self, rate=1):
        self._scroll_position_y -= rate
        if self._scroll_position_y < 0:
            self._scroll_position_y = 0

    def scroll_down(self, rate=1):
        self._scroll_position_y += rate
        if self._scroll_position_y > self.scroll_limit_y:
            self._scroll_position_y = self.scroll_limit_y

    def scroll_left(self, rate=1):
        self._scroll_position_x -= rate
        if self._scroll_position_x < 0:
            self._scroll_position_x = 0

    def scroll_right(self, rate=1):
        self._scroll_position_x += rate
        if self._scroll_position_x > self.scroll_limit_x:
            self._scroll_position_x = self.scroll_limit_x


class CANMsgPane(Pane, ABC):
    def __init__(self: CANMsgPane, name: str, parser: CANOpenParser,
                 capacity: int = None, fields: dict = None, frame_types: list
                 = None):
        super().__init__()
        if fields is None:
            fields = {}

        if frame_types is None:
            frame_types = []

        self.name = name
        self._parser = parser
        self.capacity = capacity
        self._cols = {}
        self.table = CANMsgTable(capacity=capacity)

        # set width to column + 2 padding for each field
        for field in fields:
            self._cols[field] = [fields[field], len(field) + 2]
            self.v_width += self._cols[field][1]

        # Turn the frame-type strings into enumerations
        self.frame_types = []
        for ft in frame_types:
            self.frame_types.append(MessageType[ft])

    def draw(self: CANMsgPane):
        super().draw()
        height, width = self.parent.getmaxyx()
        y_offset, x_offset = self.parent.getbegyx()

        self.v_height = len(self.table) + 50
        self.v_height = height if self.v_height < height else self.v_height
        self.scroll_limit_y = len(self.table) - 1

        self.v_width = width if self.v_width < width else self.v_width
        self.scroll_limit_x = self.v_width - 2

        self._pad.resize(self.v_height - 1, self.v_width)

        # Update parent
        out_of = '/{}'.format(self.capacity) \
            if self.capacity is not None else ''
        banner = '{} ({}{})'.format(self.name,
                                    len(self.table),
                                    out_of)

        if self.selected:
            self.parent.attron(self._style | curses.A_REVERSE)

        self.parent.addstr(0, 1, banner)

        self.parent.attroff(self._style | curses.A_REVERSE)

        # Add fields header or directions to add fields
        if len(self._cols) == 0:
            if self.v_height < 2:
                self.v_height = 2

            self.add_line(1, 1, "No fields added for this pane!", bold=True)
            self.add_line(2, 1, "Add fields in "
                                "~/.config/canopen-monitor/layout.json",
                          bold=True)

        else:
            self.draw_header()

        for i, arb_id in enumerate(self.table):
            msg = self.table[arb_id]
            attributes = dir(msg)
            line = ""
            for col in self._cols.values():
                if col[0] in attributes:
                    if col[0] == 'arb_id':
                        value = hex(msg.arb_id)
                    else:
                        value = str(getattr(msg, col[0]))
                else:
                    value = "Not Found"

                line += value.ljust(col[1], ' ')

            is_selected = self.selected and self._scroll_position_y == i
            self.add_line(i + 1, 1, line, selected=is_selected)

        # Don't Scroll down until after scrolling past last item
        if self._scroll_position_y < height - 3:
            scroll_offset_y = 0
        else:
            scroll_offset_y = self._scroll_position_y - (height - 4)

        # Don't allow for for pad to be seen past v_width
        if self._scroll_position_x + width > self.v_width:
            self._scroll_position_x = self.v_width - width

        scroll_offset_x = self._scroll_position_x

        self.parent.refresh()
        self._pad.refresh(scroll_offset_y,
                          scroll_offset_x,
                          y_offset + 1,
                          x_offset + 1,
                          y_offset + height - 2,
                          x_offset + width - 2)

    def add_line(self, y: int, x: int, line: str = "", bold: bool = False,
                 selected: bool = False) \
            -> None:

        # Widen pad when line length is larger than current v_width
        if len(line) + 2 > self.v_width:
            self.v_width = len(line) + 2
            self._pad.resize(self.v_height - 1, self.v_width)

        if bold:
            self._pad.attron(self._style | curses.A_BOLD)
        if selected:
            self._pad.attron(self._style | curses.A_REVERSE)

        self._pad.addstr(y, x, line)

        if bold:
            self._pad.attroff(self._style | curses.A_BOLD)
        if selected:
            self._pad.attroff(self._style | curses.A_REVERSE)

    def draw_header(self) -> None:
        line = ""
        for col in self._cols:
            line += col.ljust(self._cols[col][1], ' ')

        self.add_line(0, 1, line, bold=True)

    def add(self: CANMsgPane, msg: CANMsg):
        super().add(msg)
        msg.parsed_msg = self._parser.parse(msg)[0]
        self.table += msg

        attributes = dir(msg)
        for col in self._cols.values():
            if col[0] in attributes:
                value = str(getattr(msg, col[0]))
            else:
                value = "Not Found"

            col[1] = len(value) + 2 if len(value) + 2 > col[1] else col[1]

    def has_frame_type(self, frame):
        return frame.message_type in self.frame_types
