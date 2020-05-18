import curses
from .bus import TheMagicCanBus
from .grid import Grid, Split
from .pane import Pane


class CanMonitor:
    def __init__(self, devices, table_schema):
        # Monitor setup
        self.scroll_rate = 5
        self.screen = curses.initscr()  # Construct the virtual screen
        self.screen.keypad(True)  # Enable keypad
        self.screen.timeout(1)  # Set user-input timeout (ms)
        self.bus = TheMagicCanBus(devices)

        # Stuff to be setup at a later time
        self.parent = None
        self.panes = None
        self.selected = None
        self.pane_i = -1

        # Curses configuration
        curses.noecho()  # Disable user-input echo
        curses.cbreak()  # Disable line buffering
        curses.curs_set(0)  # Disable cursor

        # Curses color pairs
        curses.start_color()
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_GREEN)
        curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_CYAN)
        curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_YELLOW)

        # Construct the grid(s)
        self.construct_grid(table_schema)

    def start(self, window):
        while True:
            data = self.bus.receive()
            self.parent.add_item('misc', data)
            height, width = self.screen.getmaxyx()
            self.parent.resize(width, height, 0, 1)
            self.parent.draw()

    def stop(self):
        curses.nocbreak()  # Enable line buffering
        curses.echo()  # Enable user-input echo
        curses.curs_set(1)  # Enable the cursor
        curses.endwin()  # Destroy the virtual screen

    def construct_grid(self, schema, parent=None):
        type = schema.get('type')
        split = schema.get('split')
        if(split == 'horizontal'):
            split = Split.HORIZONTAL
        else:
            split = Split.VERTICAL
        data = schema.get('data')

        if(parent is None):
            self.parent = Grid(split)

            for entry in data:
                self.construct_grid(entry, self.parent)
        else:
            if(type == 'grid'):
                component = Grid(split)

                for entry in data:
                    self.construct_grid(component, entry)
            else:
                name = schema.get('name')
                capacity = schema.get('capacity')
                stale_time = schema.get('stale_time')
                dead_time = schema.get('dead_time')
                component = Pane(name,
                                 capacity=capacity,
                                 stale_time=stale_time,
                                 dead_time=dead_time)

            parent.add_pannel(component)

        self.panes = self.parent.flat_pannels()
        self.pane_i = 0
        self.selected = self.panes[self.pane_i]
        self.selected.selected = True
