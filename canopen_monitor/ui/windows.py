from __future__ import annotations
import curses
import curses.ascii

from .pane import Pane


class PopupWindow(Pane):

    def __init__(self: PopupWindow,
                 parent: any,
                 header: str = 'Alert',
                 content: [str] = [],
                 footer: str = 'ESC: close',
                 style: any = None):
        super().__init__(parent=(parent or curses.newpad(0, 0)),
                         height=1,
                         width=1,
                         y=10,
                         x=10)
        """Set an init to Popup window"""
        # Pop-up window properties
        self.setWindowProperties(header, content, footer)

        # Parent window dimensions (Usually should be STDOUT directly)
        p_height, p_width = self.parent.getmaxyx()

        # Break lines as necessary
        self.content = self.break_lines(int(2 * p_width / 3), self.content)

        # UI dimensions
        self.setUIDimension(p_height, p_width)

        # UI properties
        self.style = (style or curses.color_pair(0))
        self._pad.attron(self.style)

    def setUIDimension(self, p_height, p_width):
        """Set UI Dimension (x,y) by giving parent
        height and width"""
        self.v_height = (len(self.content)) + 2
        width = len(self.header) + 2
        if (len(self.content) > 0):
            width = max(width, max(list(map(lambda x: len(x), self.content))))
        self.v_width = width + 4
        self.y = int(((p_height + self.v_height) / 2) - self.v_height)
        self.x = int(((p_width + self.v_width) / 2) - self.v_width)

    def setWindowProperties(self: PopupWindow, header, content, footer):
        """Set default window properties"""
        self.header = header
        self.content = content
        self.footer = footer
        self.enabled = False

    def break_lines(self: PopupWindow,
                    max_width: int,
                    content: [str]) -> [str]:
        # Determine if some lines of content need to be broken up
        for i, line in enumerate(content):
            length = len(line)
            mid = int(length / 2)

            self.determine_to_break_content(content, i, length, line, max_width,
                                            mid)
        return content

    def determine_to_break_content(self, content, i, length, line, max_width,
                                   mid):
        if (length >= max_width):
            # Break the line at the next available space
            for j, c in enumerate(line[mid - 1:]):
                if (c == ' '):
                    mid += j
                    break
            self.apply_line_to_content_array(content, i, line, mid)

    def apply_line_to_content_array(self, content, i, line, mid):
        """Apply the line break to the content array"""
        content.pop(i)
        content.insert(i, line[:mid - 1])
        content.insert(i + 1, line[mid:])

    def toggle(self: PopupWindow) -> bool:
        self.enabled = not self.enabled
        return self.enabled

    def __draw_header(self: PopupWindow) -> None:
        """Add the header line to the window"""
        self.add_line(0, 1, self.header, underline=True)

    def __draw__footer(self: PopupWindow) -> None:
        """Add the footer to the window"""
        f_width = len(self.footer) + 2
        self.add_line(self.v_height - 1,
                      self.v_width - f_width,
                      self.footer,
                      underline=True)

    def __draw_content(self):
        """Read each line of the content and add to the window"""
        for i, line in enumerate(self.content):
            self.add_line(1 + i, 2, line)

    def draw(self: PopupWindow) -> None:
        if (self.enabled):
            super().resize(self.v_height, self.v_width)
            super().draw()
            self.__draw_header()
            self.__draw_content()
            self.__draw__footer()
            super().refresh()
        else:
            # super().clear()
            ...


class InputPopup(PopupWindow):
    """
    Input form creates a popup window for retrieving
    text input from the user

    :param parent: parent ui element
    :type: any
    :param header: header text of popup window
    :type: str
    :param footer: footer text of popup window
    :type: str
    :param style: style of window
    :type: any
    :param input_len: Maximum length of input text
    :type: int
    """

    def __init__(self: InputPopup,
                 parent: any,
                 header: str = 'Alert',
                 footer: str = 'ESC: close',
                 style: any = None,
                 input_len: int = 30,
                 ):

        self.input_len = input_len
        content = [" " * self.input_len]
        super().__init__(parent, header, content, footer, style)
        self.cursor_loc = 0

    def read_input(self, keyboard_input: int) -> None:
        """
        Read process keyboard input (ascii or backspace)

        :param keyboard_input: curses input character value from curses.getch
        :type: int
        """
        if curses.ascii.isalnum(keyboard_input) and \
                self.cursor_loc < self.input_len:
            temp = list(self.content[0])
            temp[self.cursor_loc] = chr(keyboard_input)
            self.content[0] = "".join(temp)
            self.cursor_loc += 1
        elif keyboard_input == curses.KEY_BACKSPACE and self.cursor_loc > 0:
            self.cursor_loc -= 1
            temp = list(self.content[0])
            temp[self.cursor_loc] = " "
            self.content[0] = "".join(temp)

    def toggle(self: InputPopup) -> bool:
        """
        Toggle window and clear inserted text
        :return: value indicating whether the window is enabled
        :type: bool
        """
        self.content = [" " * self.input_len]
        self.cursor_loc = 0
        return super().toggle()

    def get_value(self) -> str:
        """
        Get the value of user input without trailing spaces
        :return: user input value
        :type: str
        """
        return self.content[0].strip()


class SelectionPopup(PopupWindow):
    """
        Input form creates a popup window for selecting
        from a list of options

        :param parent: parent ui element
        :type: any
        :param header: header text of popup window
        :type: str
        :param footer: footer text of popup window
        :type: str
        :param style: style of window
        :type: any
        """
    def __init__(self: SelectionPopup,
                 parent: any,
                 header: str = 'Alert',
                 footer: str = 'ESC: close',
                 style: any = None,
                 ):
        content = [" " * 40]
        super().__init__(parent, header, content, footer, style)
        self.cursor_loc = 0

    def read_input(self: SelectionPopup, keyboard_input: int) -> None:
        """
        Read process keyboard input (ascii or backspace)

        :param keyboard_input: curses input character value from curses.getch
        :type: int
        """
        if keyboard_input == curses.KEY_UP and self.cursor_loc > 0:
            self.cursor_loc -= 1
        elif keyboard_input == curses.KEY_DOWN and self.cursor_loc < len(
                self.content) - 1:
            self.cursor_loc += 1

    def __draw_header(self: SelectionPopup) -> None:
        """Add the header line to the window"""
        self.add_line(0, 1, self.header, underline=True)

    def __draw__footer(self: SelectionPopup) -> None:
        """Add the footer to the window"""
        f_width = len(self.footer) + 2
        self.add_line(self.v_height - 1,
                      self.v_width - f_width,
                      self.footer,
                      underline=True)

    def __draw_content(self: SelectionPopup) -> None:
        """Read each line of the content and add to the window"""
        for i, line in enumerate(self.content):
            self.add_line(1 + i, 2, line, highlight=i == self.cursor_loc)

    def draw(self: SelectionPopup) -> None:
        if (self.enabled):
            super().resize(len(self.content)+2, self.v_width)
            if self.needs_refresh:
                self.refresh()

            self.parent.attron(self._style)
            self._pad.attron(self._style)

            if (self.border):
                self._pad.box()
            self.__draw_header()
            self.__draw_content()
            self.__draw__footer()
            super().refresh()

    def toggle(self: InputPopup) -> bool:
        """
        Toggle window and reset selected item
        :return: value indicating whether the window is enabled
        :type: bool
        """
        self.cursor_loc = 0
        self.clear()
        return super().toggle()

    def get_value(self):
        if self.cursor_loc >= len(self.content):
            return ""

        return self.content[self.cursor_loc]
