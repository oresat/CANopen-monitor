import curses
import canopen_monitor.canmsgs.canmsg_table as cmt


class Pane(cmt.CANMsgTable):
    def __init__(self,
                 name,
                 capacity=None,
                 stale_time=60,
                 dead_time=600,
                 fields=[],
                 frame_types=[]):
        super().__init__(name=name,
                         capacity=capacity,
                         stale_time=stale_time,
                         dead_time=dead_time)
        # Pane properties
        self.fields = fields
        self.frame_types = frame_types
        self.parent = curses.newwin(0, 0)

        # Pane states
        self.needs_refresh = False
        self.scroll_position = 0
        self.selected = False
        self.pad = curses.newpad(1, 1)
        self.pad.scrollok(True)

    def add(self, frame):
        self.needs_refresh = True
        super().add(frame)

    def has_frame_type(self, frame):
        return str(frame.type) in self.frame_types

    def scroll_up(self, rate=1):
        self.scroll_position -= rate
        if(self.scroll_position < 0):
            self.scroll_position = 0

    def scroll_down(self, rate=1):
        self.scroll_position += rate
        if(self.scroll_position > (len(self.table) - 1)):
            self.scroll_position = (len(self.table) - 1)

    def draw(self):
        style = curses.color_pair(4)
        height, width = self.parent.getmaxyx()
        y_offset, x_offset = self.parent.getbegyx()

        vheight = len(self.table) + 50
        if(vheight < height):
            vheight = height

        vwidth = width
        if(vwidth < width):
            vwidth = width

        self.pad.resize(vheight - 1, vwidth - 2)

        if(self.needs_refresh):
            self.clear()
        self.parent.attron(style)
        self.pad.attron(style)

        self.parent.box()
        if(self.selected):
            self.parent.attron(style | curses.A_REVERSE)
        self.parent.addstr(0, 1, self.name + " (" + str(len(self.table)))
        if(self.capacity is not None):
            self.parent.addstr("/" + str(self.capacity))
        self.parent.addstr(")")
        self.parent.attroff(style | curses.A_REVERSE)

        for i, id in enumerate(self.ids()):
            if(self.selected and i == self.scroll_position):
                self.pad.attron(style | curses.A_BOLD)
            self.pad.addstr(i, 1, "#" + str(i + 1) + ": " + str(self.table[id]))
            self.pad.attroff(style | curses.A_BOLD)

        self.parent.refresh()

        scroll_offset = self.scroll_position
        if(self.scroll_position + (height - 3) > len(self.table)):
            scroll_offset = len(self.table) - (height - 3)
        self.pad.refresh(scroll_offset, 0, y_offset + 1, x_offset + 1, y_offset + height - 2, x_offset + width - 2)

    def clear(self):
        self.pad.clear()
        self.parent.clear()
        self.needs_refresh = False
