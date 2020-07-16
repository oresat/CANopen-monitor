import curses
import enum


class Split(enum.Enum):
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
        self.panels = []

    def flatten(self):
        flat = []
        for panel in self.panels:
            if(type(panel) is Grid):
                flat += panel.flatten()
            else:
                flat += [panel]
        return flat

    def draw(self):
        for panel in self.panels:
            panel.draw()

    def clear(self):
        for panel in self.panels:
            panel.clear()
        self.parent.clear()

    def add_panel(self, panel):
        self.panels.append(panel)
        self.resize()

    def add_frame(self, frame):
        for panel in self.panels:
            if(type(panel) is Grid):
                panel.add_frame(frame)
            else:
                if(panel.has_frame_type(frame)):
                    panel.add(frame)

    def resize(self, parent=None):
        if(parent is not None):
            height, width = parent.getmaxyx()
            self.parent = curses.newwin(height - 1, width, 1, 0)

        p_height, p_width = self.parent.getmaxyx()
        py_offset, px_offset = self.parent.getbegyx()
        p_count = len(self.panels)

        for i, panel in enumerate(self.panels):
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
            panel.parent.resize(height, width)
            panel.parent.mvwin(y_offset, x_offset)

            if(type(panel) is Grid):
                panel.resize()
