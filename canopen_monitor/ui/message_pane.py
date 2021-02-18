from __future__ import annotations
from .pane import Pane
from ..can import Message, MessageType, MessageTable
import curses


class MessagePane(Pane):
    """A derivative of Pane customized specifically to list miscellaneous CAN
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
                 cols: dict,
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
        self.__col_sep = 2
        self.__header_style = curses.color_pair(4)
        self.table = message_table

        # Cursor stuff
        self.cursor = 0
        self.cursor_min = 0
        self.cursor_max = self.d_height - 10

        # Reset the collumn widths to the minimum size of the collumn names
        self.__reset_col_widths()

    def resize(self: MessagePane, height: int, width: int) -> None:
        """A wrapper for `Pane.resize()`. This intercepts a call for a resize
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
        self.cursor = self.cursor_max
        self.scroll_position_y = 0
        self.scroll_position_x = 0

    @property
    def scroll_limit_y(self: MessagePane) -> int:
        """The maximim rows the pad is allowed to shift by when scrolling
        """
        return self.d_height - 2

    @property
    def scroll_limit_x(self: MessagePane) -> int:
        """The maximim columns the pad is allowed to shift by when scrolling
        """
        max_length = sum(list(map(lambda x: x[1], self.cols.values())))
        occluded = max_length - self.d_width + 7
        return occluded if(occluded > 0) else 0

    def scroll_up(self: MessagePane, rate: int = 1) -> None:
        """This overrides `Pane.scroll_up()`. Instead of shifting the
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
        if(self.cursor < self.cursor_min):
            self.cursor = self.cursor_min

            # Deduct the amount of cursor movement from the message table
            #   movement and reset shift to bounds if need be
            leftover = rate - prev
            self.__top -= leftover
            self.__top = min if(self.__top < min) else self.__top

    def scroll_down(self: MessagePane, rate: int = 1) -> None:
        """This overrides `Pane.scroll_up()`. Instead of shifting the
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
        if(self.cursor > (self.cursor_max - 1)):
            self.cursor = self.cursor_max - 1

            # Deduct the amount of cursor movement from the message table
            #   movement and reset shift to bounds if need be
            leftover = rate - (self.cursor - prev)
            self.__top += leftover
            self.__top = max if(self.__top > max) else self.__top

    def __draw_header(self: Pane) -> None:
        """Draw the table header at the top of the Pane

        This uses the `cols` dictionary to determine what to write
        """
        self.add_line(0,
                      2,
                      f'{self._name}:'
                      f' ({len(self.table.filter(self.types))} messages)',
                      highlight=self.selected)

        pos = 1
        for name, data in self.cols.items():
            self.add_line(1,
                          pos,
                          f'{name}:'.ljust(data[1] + self.__col_sep, ' '),
                          highlight=True,
                          color=curses.color_pair(4))
            pos += data[1] + self.__col_sep

    def draw(self: MessagePane) -> None:
        """Draw all records from the MessageTable to the Pane
        """
        super().draw()
        self.resize(self.v_height, self.v_width)

        # Get the messages to be displayed based on scroll positioning,
        #   and adjust column widths accordingly
        draw_messages = self.table.filter(self.types,
                                          self.__top,
                                          self.__top + self.d_height - 3)
        self.__check_col_widths(draw_messages)

        # Draw the header and messages
        self.__draw_header()
        for i, message in enumerate(draw_messages):
            pos = 1
            for name, data in self.cols.items():
                attr = getattr(message, data[0])
                callable = data[2] if (len(data) == 3) else str
                self.add_line(2 + i,
                              pos,
                              callable(attr).ljust(data[1] + self.__col_sep,
                                                   ' '),
                              highlight=((self.cursor == i) and self.selected))
                pos += data[1] + self.__col_sep

        # Refresh the Pane and end the draw cycle
        super().refresh()

    def __reset_col_widths(self: Message):
        for name, data in self.cols.items():
            self.cols[name] = (data[0], len(name), data[2]) \
                if (len(data) == 3) else (data[0], len(name))

    def __check_col_widths(self: MessagePane, messages: [Message]) -> None:
        for message in messages:
            for name, data in self.cols.items():
                attr = getattr(message, data[0])
                attr_len = len(str(attr))
                if(data[1] < attr_len):
                    self.cols[name] = (data[0], attr_len)
                    super().clear()
