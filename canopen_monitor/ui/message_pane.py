from __future__ import annotations
from .pane import Pane
from .colum import Column
from ..can import Message, MessageType, MessageTable
import curses


class MessagePane(Pane):
    """
    A derivative of Pane customized specifically to list miscellaneous CAN
    messages stored in a MessageTable

    :param name: The name of the pane (to be printed in the top left)
    :type name: str

    :param cols: A dictionary describing the pane layout. The key is the Pane
        collumn name, the value is a tuple containing the Message attribute to
        map the collumn to, and the max collumn width respectively.
    :type cols: dict

    :param selected: An indicator that the current Pane is selected
    :type selected: bool

    :param table: The message table
    :type table: MessageTable
    """

    def __init__(self: MessagePane,
                 cols: [Column],
                 types: [MessageType],
                 name: str = '',
                 parent: any = None,
                 height: int = 1,
                 width: int = 1,
                 y: int = 0,
                 x: int = 0,
                 message_table: MessageTable = MessageTable()):
        super().__init__(parent=(parent or curses.newpad(0, 0)),
                         height=height,
                         width=width,
                         y=y,
                         x=x)

        # Pane details
        self._name = name
        self.cols = cols
        self.types = types
        self.__top = 0
        self.__top_max = 0
        self.__header_style = curses.color_pair(4)
        self.table = message_table

        # Cursor stuff
        self.cursor = 0
        self.cursor_min = 0
        self.cursor_max = self.d_height - 10

        self.sort_index = 0
        self.sort_reverse = False

    def handle_click(self: MessagePane, x, y) -> None:
        """
        Handles a click at coordinates (x, y) within the MessagePane.
        """

        # check if y is in the column row before sorting
        if y == (self.y + 1):
            cursor = 1
            for col in self.cols:
                if x <= (cursor + col.length):
                    new_index = self.cols.index(col)
                    if new_index == self.sort_index:
                        self.sort_reverse = not self.sort_reverse
                    else:
                        self.sort_reverse = False
                        self.sort_index = new_index
                    return
                else:
                    cursor += col.length

    def clear_messages(self: MessagePane) -> None:
        """
        Clears the message table for the pane.
        """
        self.table.clear()

    def resize(self: MessagePane, height: int, width: int) -> None:
        """
        A wrapper for `Pane.resize()`. This intercepts a call for a resize
        in order to upate MessagePane-specific details that change on a resize
        event. The parent `resize()` gets called first and then MessagePane's
        details are updated.

        :param height: New virtual height
        :type height: int

        :param width: New virtual width
        :type width: int
        """
        super().resize(height, width)
        p_height = self.d_height - 3
        table_size = len(self.table.filter(self.types))
        occluded = table_size - self.__top - self.d_height + 3

        self.cursor_max = table_size if table_size < p_height else p_height
        self.__top_max = occluded if occluded > 0 else 0

    def _reset_scroll_positions(self: MessagePane) -> None:
        """
        Reset the scroll positions.
        Initialize the y position to be zero.
        Initialize the x position to be zero.
        """
        self.cursor = self.cursor_max
        self.scroll_position_y = 0
        self.scroll_position_x = 0

    @property
    def scroll_limit_y(self: MessagePane) -> int:
        """
        The maximim rows the pad is allowed to shift by when scrolling
        """
        return self.d_height - 2

    @property
    def scroll_limit_x(self: MessagePane) -> int:
        """
        The maximim columns the pad is allowed to shift by when scrolling
        """
        max_length = sum(list(map(lambda x: x.length, self.cols)))
        occluded = max_length - self.d_width + 7
        return occluded if (occluded > 0) else 0

    def scroll_up(self: MessagePane, rate: int = 1) -> None:
        """
        This overrides `Pane.scroll_up()`. Instead of shifting the
        pad vertically, the slice of messages from the `MessageTable` is
        shifted.

        :param rate: Number of messages to scroll by
        :type rate: int
        """
        # Record current cursor info for later scroll calculations
        prev = self.cursor
        min = 0

        # Move the cursor
        self.cursor -= rate

        # If the cursor is less than the minimum, reset it to the minimum then
        #   do calculations for shifting the message table
        if (self.cursor < self.cursor_min):
            self.cursor = self.cursor_min

            # Deduct the amount of cursor movement from the message table
            #   movement and reset shift to bounds if need be
            leftover = rate - prev
            self.__top -= leftover
            self.__top = min if (self.__top < min) else self.__top

    def scroll_down(self: MessagePane, rate: int = 1) -> None:
        """
        This overrides `Pane.scroll_up()`. Instead of shifting the
        pad vertically, the slice of messages from the `MessageTable` is
        shifted.

        :param rate: Number of messages to scroll by
        :type rate: int
        """
        # Record current cursor info for later scroll calculations
        prev = self.cursor
        max = self.__top + self.__top_max

        # Move the cursor
        self.cursor += rate

        # If the cursor is greater than the maximum, reset it to the minimum
        #   then do calculations for shifting the message table
        if (self.cursor > (self.cursor_max - 1)):
            self.cursor = self.cursor_max - 1

            # Deduct the amount of cursor movement from the message table
            #   movement and reset shift to bounds if need be
            leftover = rate - (self.cursor - prev)
            self.__top += leftover
            self.__top = max if (self.__top > max) else self.__top

    def __draw_header(self: Pane) -> None:
        """
        Draw the table header at the top of the Pane

        This uses the `cols` dictionary to determine what to write
        """
        self.add_line(f'{self._name}:'
                      f' ({len(self.table.filter(self.types))} messages)',
                      y=0,
                      x=1,
                      highlight=self.selected)
        self._pad.move(1, 1)
        for col in self.cols:
            self.add_line(col.header,
                          highlight=True,
                          color=curses.color_pair(4))

    def draw(self: MessagePane) -> None:
        """
        Draw all records from the MessageTable to the Pane
        """
        super().draw()
        self.resize(self.v_height, self.v_width)

        # Get the messages to be displayed based on scroll positioning,
        #   and adjust column widths accordingly
        draw_messages = self.table.filter(
            types=self.types,
            start=self.__top,
            end=self.__top + self.d_height - 3,
            sort_by=self.cols[self.sort_index].attr_name,
            reverse=self.sort_reverse
        )

        self.__check_col_widths(draw_messages)

        # Draw the header and messages
        self.__draw_header()
        for i, message in enumerate(draw_messages):
            self._pad.move(2 + i, 1)
            for col in self.cols:
                self.add_line(col.format(message),
                              highlight=((self.cursor == i) and self.selected))
        # Refresh the Pane and end the draw cycle
        super().refresh()

    def __check_col_widths(self: MessagePane, messages: [Message]) -> None:
        """
        Check the width of the message in Pane column.

        :param messages: The list of the messages
        :type messages: list
        """
        for col in self.cols:
            for message in messages:
                if col.update_length(message):
                    self._pad.clear()
