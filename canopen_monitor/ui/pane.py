from __future__ import annotations
from ..canmsgs import CANMsgTable, CANMsg, MessageType
from ..parser import CANOpenParser
import curses
from abc import ABC, abstractmethod


class Pane(ABC):
    """
    Abstract Pane Class, contains a PAD and a window.
    """

    def __init__(self: Pane, border: bool = True, color_pair: int = 4):
        """
        Abstract pane initialization

        Arguments
        ----------

        border: boolean definition of whether or not to display border
        color_pair: curses color pair to use (must be implemented prior)
        """
        self._pad = curses.newpad(1, 1)
        self._pad.scrollok(True)
        self.parent = curses.newwin(0, 0)
        self.__border = border
        self.v_width = 0
        self.v_height = 0

        # Pane state
        self.selected = False
        self.needs_refresh = False
        self.scroll_position_y = 0
        self.scroll_position_x = 0
        self.scroll_limit_y = 0
        self.scroll_limit_x = 0

        # Draw Style
        self._style = curses.color_pair(color_pair)

    @abstractmethod
    def draw(self: Pane) -> None:
        """
        Abstract draw method, must be overwritten in child class
        draw should first resize the pad using: self._pad.resize()
        then add content using: self._pad.addstr()
        then refresh using: self._pad.refresh()

        abstract method will clear and handle border

        child class should also set _scroll_limit_x and _scroll_limit_y here
        """
        if self.needs_refresh:
            self.clear()

        self.parent.attron(self._style)
        self._pad.attron(self._style)

        if self.__border:
            self.parent.box()

    def clear(self: Pane) -> None:
        """
        Clear all contents of pad and parent window
        """
        self._pad.clear()
        self.parent.clear()
        self.needs_refresh = False

    @abstractmethod
    def add(self: Pane, item: any) -> None:
        """
        Abstract add method, must be overwritten in child class
        Child class should handle retrieving and storing added items
        to be drawn by add method
        """
        ...

    def scroll_up(self: Pane, rate: int = 1) -> bool:
        """
        Scroll pad upwards

        Arguments
        ----------
        rate: number of lines to scroll up by

        Returns
        --------
        bool: Indication of whether a limit was reached. False indicates a
        limit was reached and the pane cannot be scrolled further in that
        direction
        """
        self.scroll_position_y -= rate
        if self.scroll_position_y < 0:
            self.scroll_position_y = 0
            return False
        return True

    def scroll_down(self: Pane, rate: int = 1) -> None:
        """
        Scroll pad downwards

        Note: scroll limit must be handled by child class

        Arguments
        ----------
        rate: number of lines to scroll down by

        Returns
        --------
        bool: Indication of whether a limit was reached. False indicates a
        limit was reached and the pane cannot be scrolled further in that
        """
        self.scroll_position_y += rate
        if self.scroll_position_y > self.scroll_limit_y:
            self.scroll_position_y = self.scroll_limit_y
            return False
        return True

    def scroll_left(self: Pane, rate: int = 1):
        """
        Scroll pad left

        Arguments
        ----------
        rate: number of cols to scroll left by

        Returns
        --------
        bool: Indication of whether a limit was reached. False indicates a
        limit was reached and the pane cannot be scrolled further in that
        """
        self.scroll_position_x -= rate
        if self.scroll_position_x < 0:
            self.scroll_position_x = 0
            return False
        return True

    def scroll_right(self: Pane, rate: int = 1):
        """
        Scroll pad right

        Note: scroll limit must be handled by child class

        Arguments
        ----------
        rate: number of cols to scroll right by

        Returns
        --------
        bool: Indication of whether a limit was reached. False indicates a
        limit was reached and the pane cannot be scrolled further in that
        """
        self.scroll_position_x += rate
        if self.scroll_position_x > self.scroll_limit_x:
            self.scroll_position_x = self.scroll_limit_x
            return False
        return True


class CANMsgPane(Pane):
    """
    Displays a Table of CAN messages inside of a pane
    """

    def __init__(self: CANMsgPane, name: str, parser: CANOpenParser,
                 capacity: int = None, fields: dict = None, frame_types: list
                 = None):
        """
        CANMsgPane Initialization

        Arguments
        ----------
        name: string title displayed on parent window
        parser: CANOpenParser used to generated parsed messages
        capacity: Maximum number of records to display in pane
        fields: ordered dictionary of fields to display in output (layout.json)
        frame_types: list of frame types to display in table (layout.json)
        """
        super().__init__()
        if fields is None:
            fields = {}

        if frame_types is None:
            frame_types = []

        self._name = name
        self._parser = parser
        self._cols = {}
        self.table = CANMsgTable(capacity=capacity)
        self.__top = 0

        # set width to column + 2 padding for each field
        for field in fields:
            self._cols[field] = [fields[field], len(field) + 2]
            self.v_width += self._cols[field][1]

        # Turn the frame-type strings into enumerations
        self.frame_types = []
        for ft in frame_types:
            self.frame_types.append(MessageType[ft])

    def draw(self: CANMsgPane) -> None:
        """
        Draw all records from the CANMsgTable to the Pane's Pad
        and any relevent information to the Pane's parent window
        Pane scrolling and refreshing are implemented here as well
        """
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
        out_of = '/{}'.format(self.table.capacity) \
            if self.table.capacity is not None else ''
        banner = '{} ({}{})'.format(self._name,
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

            self.__add_line(1, 1, "No fields added for this pane!", bold=True)
            self.__add_line(2, 1, "Add fields in "
                                  "~/.config/canopen-monitor/layout.json",
                            bold=True)

        self._pad.attroff(self._style)

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

            is_selected = self.selected and self.scroll_position_y == i
            self.__add_line(i + 1, 1, line, selected=is_selected)

        # Don't Scroll down until after scrolling past last item
        if self.scroll_position_y - (height - 4) > self.__top:
            self.__top = self.scroll_position_y - (height - 4)
        if self.scroll_position_y < self.__top:
            self.__top = self.scroll_position_y

        # Don't allow for for pad to be seen past v_width
        if self.scroll_position_x + width > self.v_width:
            self.scroll_position_x = self.v_width - width

        scroll_offset_x = self.scroll_position_x
        self.__draw_header(self.__top, 1)

        self.parent.refresh()
        self._pad.refresh(self.__top,
                          scroll_offset_x,
                          y_offset + 1,
                          x_offset + 1,
                          y_offset + height - 2,
                          x_offset + width - 2)

    def __add_line(self: CANMsgPane, y: int, x: int, line: str = "",
                   bold: bool = False, selected: bool = False) -> None:
        """
        Add line of text to the Pane's pad
        Handles resizing and pad attributes

        Arguments
        ----------
        y: Pad's row to start writing to
        x: Pad's col to start writing to
        line: string of text to write
        bold: boolean indicator of whether to bold line
        selected: boolean indicator of whether to mark line selected
        """
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

    def __draw_header(self: CANMsgPane, y: int, x: int) -> None:
        """
        Draw the table header to the top of the pane
        """
        line = ""
        for col in self._cols:
            line += col.ljust(self._cols[col][1], ' ')

        self.__add_line(y, x, line, bold=True)

    def add(self: CANMsgPane, msg: CANMsg) -> None:
        """
        Add provided message to the can msg table
        and update column widths as required

        Arguments
        ----------
        msg: CanMsg to be added
        """
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

    def has_frame_type(self: CANMsgPane, frame: CANMsg) -> bool:
        """
        Determine if CANMsg type is handled by this frame
        Arguments
        ----------
        frame: CANMsg to check type of

        Returns
        --------
        bool: Indicator if this pane accepts the message type of the provided message
        """
        return frame.message_type in self.frame_types
