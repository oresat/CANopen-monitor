import curses
from ..canmsgs import CANMsgTable, MessageType


class Pane(CANMsgTable):
    """
    A model of an NCurses window pane
    """

    def __init__(self,
                 name,
                 parser,
                 capacity=None,
                 fields=[],
                 frame_types=[]):
        super().__init__(name=name,
                         capacity=capacity)
        # Pane properties
        self.parser = parser
        self.fields = fields
        self.parent = curses.newwin(0, 0)

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

    def draw_schema(self, style):
        # Pane banner
        if(MessageType.HEARTBEAT in self.frame_types):
            banner = '{}{}{}{}'.format('COB ID'.ljust(10, ' '),
                                       'Node Name'.ljust(30, ' '),
                                       'State'.ljust(40, ' '),
                                       'Status'.ljust(10, ' '))
        else:
            banner = '{}{}{}'.format('COB ID'.ljust(10, ' '),
                                     'Node Name'.ljust(25, ' '),
                                     'Message'.ljust(40, ' '))
        self.pad.addstr(0, 1, banner)

        for i, id in enumerate(self.ids()):
            if(self.selected and i == self.scroll_position):
                self.pad.attron(style | curses.A_BOLD)
            msg = self.message_table[id]
            cob_id = str(hex(self.message_table[id].arb_id))

            # TODO: Remove this and make the parser do this
            if(len(msg.data) > 3):
                parsed_msg, node_name = self.parser.parse(msg)
            else:
                parsed_msg, node_name = ['Empty data block!', str(hex(id))]

            if(MessageType.HEARTBEAT in self.frame_types):
                if(len(parsed_msg) > 40):
                    parsed_msg = parsed_msg[:39]
                msg = '{}{}{}{}'.format(cob_id.ljust(10, ' '),
                                        node_name.ljust(30, ' '),
                                        parsed_msg.ljust(40, ' '),
                                        msg.status().ljust(10, ' '))
            else:
                msg = '{}{}{}'.format(cob_id.ljust(10, ' '),
                                      node_name.ljust(25, ' '),
                                      parsed_msg.ljust(40, ' '))
            self.pad.addstr(i + 1, 1, msg)
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
        self.parent.addstr(0, 1, self.name + " (" + str(len(self.message_table)))
        if(self.capacity is not None):
            self.parent.addstr("/" + str(self.capacity))
        self.parent.addstr(")")
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
