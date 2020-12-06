import curses
from ..canmsgs import CANMsgTable, MessageType


class Pane(CANMsgTable):
    """
    A model of an NCurses window pane
    """

    def __init__(self, name, parser, capacity=None, fields=[], frame_types=[]):
        super().__init__(name=name,
                         capacity=capacity)
        # Pane properties
        self.parser = parser
        self.fields = fields
        self.parent = curses.newwin(0, 0)

        # Column layout configuration
        self.cols = [
            'COB ID',
            'Node Name',
            'Interface',
            'Type',
            'Message'
        ]
        self.col_widths = []
        for col in self.cols:
            self.col_widths.append(len(col) + 2)

        # Turn the frame-type strings into enumerations
        self.frame_types = []
        for ft in frame_types:
            self.frame_types.append(MessageType[ft])

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
        return frame.message_type in self.frame_types

    def scroll_up(self, rate=1):
        self.scroll_position -= rate
        if(self.scroll_position < 0):
            self.scroll_position = 0

    def scroll_down(self, rate=1):
        self.scroll_position += rate
        if(self.scroll_position > (len(self.message_table) - 1)):
            self.scroll_position = (len(self.message_table) - 1)

    def check_col_widths(self):
        # Check the column lengths beforehand
        for msg in self.message_table.values():
            if(len(hex(msg.arb_id)) > self.col_widths[0]):
                self.col_widths[0] = len(hex(msg.arb_id)) + 2
            if(len(msg.node_name) > self.col_widths[1]):
                self.col_widths[1] = len(msg.node_name) + 2
            if(len(msg.interface) > self.col_widths[2]):
                self.col_widths[2] = len(msg.interface) + 2
            if(len(str(msg.message_type)) > self.col_widths[3]):
                self.col_widths[3] = len(str(msg.message_type)) + 2

    def draw_banner(self, style):
        banner = ''

        for i, col in enumerate(self.cols):
            banner += col.ljust(self.col_widths[i], ' ')

        self.parent.attron(style | curses.A_REVERSE)
        self.pad.addstr(0, 1, banner)
        self.parent.attroff(style | curses.A_REVERSE)

    def draw_schema(self, style):
        self.check_col_widths()
        self.draw_banner(style)

        for i, id in enumerate(self.ids()):
            if(self.selected and i == self.scroll_position):
                self.pad.attron(style | curses.A_BOLD)
            msg = self.message_table[id]
            cob_id = str(hex(self.message_table[id].arb_id))

            parsed_msg, msg.node_name = self.parser.parse(msg)
            msg.node_name = str(msg.node_name)

            cols = [
                cob_id,
                msg.node_name,
                msg.interface,
                msg.message_type.name,
                parsed_msg
            ]

            line = '{}{}{}{}{}'.format(cols[0].ljust(self.col_widths[0], ' '),
                                       cols[1].ljust(self.col_widths[1], ' '),
                                       cols[2].ljust(self.col_widths[2], ' '),
                                       cols[3].ljust(self.col_widths[3], ' '),
                                       cols[4].ljust(self.col_widths[4], ' '))

            self.pad.addstr(i + 1, 1, line)
            self.pad.attroff(style | curses.A_BOLD)

    def draw(self):
        style = curses.color_pair(4)
        height, width = self.parent.getmaxyx()
        y_offset, x_offset = self.parent.getbegyx()

        vheight = len(self.message_table) + 50
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

        out_of = '/{}'.format(self.capacity) \
                 if self.capacity is not None else ''
        banner = '{} ({}{})'.format(self.name,
                                    len(self.message_table),
                                    out_of)
        self.parent.addstr(0, 1, banner)
        self.parent.attroff(style | curses.A_REVERSE)

        self.draw_schema(style)

        self.parent.refresh()

        scroll_offset = self.scroll_position
        if(self.scroll_position + (height - 3) > len(self.message_table)):
            scroll_offset = len(self.message_table) - (height - 3)
        self.pad.refresh(scroll_offset,
                         0,
                         y_offset + 1,
                         x_offset + 1,
                         y_offset + height - 2,
                         x_offset + width - 2)

    def clear(self):
        self.pad.clear()
        self.parent.clear()
        self.needs_refresh = False


class InfoPane(Pane):
    def __init__(self, name, parser):
        super().__init__(name, parser)

        # Column layout configuration
        self.cols = []


class HeartBeatPane(Pane):
    def __init__(self, name, parser, capacity=None, fields=[], frame_types=[]):
        super().__init__(name,
                         parser,
                         capacity=capacity,
                         fields=fields,
                         frame_types=frame_types)

        # Column layout configuration
        self.cols = [
            'COB ID',
            'Node Name',
            'Interface',
            'State',
            'Status'
        ]
        self.col_widths = []
        for col in self.cols:
            self.col_widths.append(len(col) + 2)

    def check_col_widths(self):
        # Check the column lengths beforehand
        for msg in self.message_table.values():
            if(len(hex(msg.arb_id)) > self.col_widths[0]):
                self.col_widths[0] = len(hex(msg.arb_id)) + 2
            if(len(msg.node_name) > self.col_widths[1]):
                self.col_widths[1] = len(msg.node_name) + 2
            if(len(msg.interface) > self.col_widths[2]):
                self.col_widths[2] = len(msg.interface) + 2
            if(len(msg.status()) > self.col_widths[3]):
                self.col_widths[3] = len(msg.status()) + 2

    def draw_schema(self, style):
        self.check_col_widths()
        self.draw_banner(style)

        for i, id in enumerate(self.ids()):
            if(self.selected and i == self.scroll_position):
                self.pad.attron(style | curses.A_BOLD)
            msg = self.message_table[id]
            cob_id = str(hex(self.message_table[id].arb_id))

            parsed_msg, msg.node_name = self.parser.parse(msg)
            msg.node_name = str(msg.node_name)

            cols = [
                cob_id,
                msg.node_name,
                msg.interface,
                msg.status(),
                parsed_msg
            ]

            line = '{}{}{}{}{}'.format(cols[0].ljust(self.col_widths[0], ' '),
                                       cols[1].ljust(self.col_widths[1], ' '),
                                       cols[2].ljust(self.col_widths[2], ' '),
                                       cols[3].ljust(self.col_widths[3], ' '),
                                       cols[4].ljust(self.col_widths[4], ' '))
            self.pad.addstr(i + 1, 1, line)
            self.pad.attroff(style | curses.A_BOLD)
