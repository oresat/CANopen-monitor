from __future__ import annotations
from .pane import Pane
from ..can import Message, MessageTable
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
                 name: str = '',
                 parent: any = None,
                 height: int = 1,
                 width: int = 1,
                 message_table: MessageTable = MessageTable()):
        super().__init__(parent=(parent or curses.newpad(0, 0)),
                         height=height,
                         width=width)

        # Pane details
        self._name = name
        self.cols = cols
        self.__top = 0
        self.__min_col_separation = 2
        self.__header_style = curses.color_pair(4)
        self.selected = True
        self.table = message_table

        # Reset the collumn widths to the minimum size of the collumn names
        for name, data in self.cols.items():
            self.cols[name] = (data[0], len(name), data[2])

    def __draw_header(self: Pane) -> None:
        """Draw the table header at the top of the Pane

        This uses the `cols` dictionary to determine what to write
        """
        self.clear_line(1)
        self.add_line(0, 2, f'{self._name}: ({len(self.table)} messages)',
                      highlight=self.selected)

        pos = 1
        for name, data in self.cols.items():
            self.add_line(1, pos, f'{name}:')
            pos += data[1] + self.__min_col_separation

    def draw(self: MessagePane) -> None:
        """Draw all records from the MessageTable to the Pane

        .. note::

            Pane scrolling and refreshing are implemented here as well
        """
        super().draw()
        p_height, p_width = self.parent.getmaxyx()
        super().resize(p_height, p_width)

        # Get the messages to be displayed based on scroll positioning,
        #   and adjust column widths accordingly
        self.__check_col_widths(self.table(self.__top,
                                           self.__top + self.d_height))

        # Draw the header and messages
        self.__draw_header()
        for i, message in enumerate(self.table(self.__top,
                                               self.__top + self.d_height)):
            pos = 1
            for name, data in self.cols.items():
                attr = getattr(message, data[0])
                callable = data[2] if(len(data) == 3) else str
                self.add_line(2 + i, pos, callable(attr))
                pos += data[1] + self.__min_col_separation

        # Refresh the Pane and end the draw cycle
        super().refresh()

    def __check_col_widths(self: MessagePane, messages: [Message]) -> None:
        for message in messages:
            for name, data in self.cols.items():
                attr = getattr(message, data[0])
                attr_len = len(str(attr))
                if(data[1] < attr_len):
                    self.cols[name] = (data[0], attr_len)
                    self.clear()
