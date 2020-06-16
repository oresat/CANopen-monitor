import curses
from enum import Enum


class Split(Enum):
    HORIZONTAL = 0
    VERTICAL = 1


class Grid:
    def __init__(self, parent=None, split=Split.VERTICAL):
        if(parent is None):
            self.parent = curses.newwin(0, 0, 0, 0)
        else:
            height, width = parent.getmaxyx()
            self.parent = curses.newwin(height - 1, width, 1, 0)

        self.split = split
        self.pannels = []

    def flatten(self):
        flat = []
        for pannel in self.pannels:
            if(type(pannel) is Grid):
                flat += pannel.flatten()
            else:
                flat += [pannel]
        return flat

    def draw(self):
        for pannel in self.pannels:
            pannel.draw()

    def clear(self):
        for pannel in self.pannels:
            pannel.clear()
        self.parent.clear()

    def add_pannel(self, pannel):
        self.pannels.append(pannel)
        self.resize()

    def add_frame(self, frame):
        for pannel in self.pannels:
            if(type(pannel) is Grid):
                pannel.add_frame(frame)
            else:
                if(pannel.has_frame_type(frame)):
                    pannel.add(frame)

    def resize(self, parent=None):
        if(parent is not None):
            height, width = parent.getmaxyx()
            self.parent = curses.newwin(height - 1, width, 1, 0)

        p_height, p_width = self.parent.getmaxyx()
        py_offset, px_offset = self.parent.getbegyx()
        p_count = len(self.pannels)

        for i, pannel in enumerate(self.pannels):
            if(self.split == Split.VERTICAL):
                width = int(p_width / p_count)
                height = p_height
                x_offset = i * width + px_offset
                y_offset = 0 + py_offset
            else:
                width = p_width
                height = int(p_height / p_count)
                x_offset = 0 + px_offset
                y_offset = i * height + py_offset
            pannel.parent.resize(height, width)
            pannel.parent.mvwin(y_offset, x_offset)

            if(type(pannel) is Grid):
                pannel.resize()
