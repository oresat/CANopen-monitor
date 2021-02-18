from __future__ import annotations
import curses
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
        # Pop-up window properties
        self.header = header
        self.content = content
        self.footer = footer
        self.enabled = False

        # Parent window dimensions (Usually should be STDOUT directly)
        p_height, p_width = self.parent.getmaxyx()

        # Break lines as necessary
        self.content = self.break_lines(int(2 * p_width / 3), self.content)

        # UI dimensions
        p_height, p_width = self.parent.getmaxyx()
        self.v_height = (len(self.content)) + 2
        width = len(self.header) + 2
        if(len(self.content) > 0):
            width = max(width, max(list(map(lambda x: len(x), self.content))))
        self.v_width = width + 4
        self.y = int(((p_height + self.v_height) / 2) - self.v_height)
        self.x = int(((p_width + self.v_width) / 2) - self.v_width)

        # UI properties
        self.style = (style or curses.color_pair(0))
        self._pad.attron(self.style)

    def break_lines(self: PopupWindow,
                    max_width: int,
                    content: [str]) -> [str]:
        # Determine if some lines of content need to be broken up
        for i, line in enumerate(content):
            length = len(line)
            mid = int(length / 2)

            if(length >= max_width):
                # Break the line at the next available space
                for j, c in enumerate(line[mid - 1:]):
                    if(c == ' '):
                        mid += j
                        break

                # Apply the line break to the content array
                content.pop(i)
                content.insert(i, line[:mid - 1])
                content.insert(i + 1, line[mid:])
        return content

    def toggle(self: PopupWindow) -> bool:
        self.enabled = not self.enabled
        return self.enabled

    def __draw_header(self: PopupWindow) -> None:
        self.add_line(0, 1, self.header, underline=True)

    def __draw__footer(self: PopupWindow) -> None:
        f_width = len(self.footer) + 2
        self.add_line(self.v_height - 1,
                      self.v_width - f_width,
                      self.footer,
                      underline=True)

    def draw(self: PopupWindow) -> None:
        if(self.enabled):
            super().resize(self.v_height, self.v_width)
            super().draw()
            self.__draw_header()

            for i, line in enumerate(self.content):
                self.add_line(1 + i, 2, line)

            self.__draw__footer()
            super().refresh()
        else:
            # super().clear()
            ...
