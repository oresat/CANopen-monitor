import curses
import time
from .bus import TheMagicCanBus
from .grid import Grid, Split
from .pane import Pane
import threading


class CanMonitor:
    def __init__(self, screen, devices, table_schema, timeout=0.1):
        # Monitor setup
        self.scroll_rate = 5
        self.screen = screen
        self.screen.keypad(True)  # Enable keypad
        self.screen.timeout(int(timeout * 1000))  # Set user-input timeout (ms)

        # Bus things
        self.devices = devices
        self.bus = TheMagicCanBus(devices, timeout=timeout)

        # Stuff to be setup at a later time
        self.parent = None
        self.panes = None
        self.selected = None
        self.pane_i = -1

        # Threading things
        self.screen_lock = threading.Lock()
        self.stop_listening = threading.Event()

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

    def start(self):
        try:
            while not self.stop_listening.is_set():
                # Get CanBus input
                data = self.bus.receive()
                if(data is not None):
                    self.parent.add_item(data)

                # Get user input
                self.read_input()

                # Draw the screen
                height, width = self.screen.getmaxyx()
                self.screen_lock.acquire()
                self.parent.resize(width, height, 0, 1)
                self.draw_banner()
                self.parent.draw()
                self.screen.refresh()
                self.screen_lock.release()
        finally:
            self.stop()

    def stop(self):
        self.screen_lock.acquire()
        curses.nocbreak()  # Enable line buffering
        curses.echo()  # Enable user-input echo
        curses.curs_set(1)  # Enable the cursor
        curses.endwin()  # Destroy the virtual screen
        self.screen_lock.release()

        self.stop_listening.set()

        print('stopping bus from the top-layer!')
        self.bus.stop_all()
        print('Stopped the bus!')

        threads = threading.enumerate().remove(threading.current_thread())
        print('waiting for all app threads to close.')
        if(threads is not None):
            for thread in threads:
                thread.join()
            print('all app threads closed gracefully!')
        else:
            print('no child app threads were spawned!')

    def read_input(self):
        # Grab new user input then flush the buffer
        input = self.screen.getch()
        curses.flushinp()

        # Determine the changes needed on screen
        if(input == curses.KEY_DOWN):
            self.selected.scroll()
        elif(input == curses.KEY_UP):
            self.selected.scroll(-1)
        elif(input == curses.KEY_SR or input == curses.KEY_SLEFT):
            self.pane_i -= 1
        elif(input == curses.KEY_SF or input == curses.KEY_SRIGHT):
            self.pane_i += 1
        elif(input == curses.KEY_END):
            self.stop()

        # Enforce pannel select bounds
        if(self.pane_i < 0):
            self.pane_i = 0
        elif(self.pane_i >= len(self.panes)):
            self.pane_i = len(self.panes) - 1
        self.select()

    def draw_banner(self):
        self.screen.addstr(0, 0, time.ctime(), curses.color_pair(1))
        self.screen.addstr(" | ")

        running = list(map(lambda x: x.ndev, self.bus.running()))
        for dev in self.devices:
            if(dev in running):
                color = 3
            else:
                color = 1

            self.screen.addstr(dev + " ", curses.color_pair(color))

    def select(self):
        if(self.selected is not None):
            self.selected.selected = False
        self.selected = self.panes[self.pane_i]
        self.selected.selected = True

    def construct_grid(self, schema, parent=None):
        type = schema.get('type')
        split = schema.get('split')
        data = schema.get('data')

        if(split == 'horizontal'):
            split = Split.HORIZONTAL
        elif(split == 'vertical'):
            split = Split.VERTICAL

        if(parent is None):
            self.parent = Grid(split=split)

            for entry in data:
                self.construct_grid(entry, self.parent)

            self.panes = self.parent.flat_pannels()
            self.pane_i = 0
            self.select()

        else:
            if(type == 'grid'):
                component = Grid(split=split)

                for entry in data:
                    self.construct_grid(entry, component)
            else:
                name = schema.get('name')
                fields = schema.get('fields')
                capacity = schema.get('capacity')
                stale_time = schema.get('stale_node_timeout')
                dead_time = schema.get('dead_node_timeout')
                frame_types = schema.get('frame_types')
                component = Pane(name,
                                 fields=fields,
                                 capacity=capacity,
                                 stale_time=stale_time,
                                 dead_time=dead_time,
                                 frame_types=frame_types)
            parent.add_pannel(component)
