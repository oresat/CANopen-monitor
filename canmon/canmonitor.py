import curses
import os
import time
from .bus import TheMagicCanBus
from .grid import Grid, Split
from .pane import Pane
import threading


class CanMonitor:
    def __init__(self, screen, devices, table_schema, block=True, timeout=0.01):
        # Monitor setup
        self.scroll_rate = 5
        self.screen = screen
        self.screen.keypad(True)  # Enable keypad
        self.screen.timeout(100)  # Set user-input timeout (ms)
        self.devices = devices
        self.bus = TheMagicCanBus(devices)
        self.block = block
        self.timeout = timeout
        self.screen_lock = threading.Lock()
        self.pid = os.getpid()

        # Stuff to be setup at a later time
        self.parent = None
        self.panes = None
        self.selected = None
        self.pane_i = -1
        self.mutex = threading.Condition()
        self.kill_threads = False

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
            # Start the user input thread
            threading.Thread(target=self.read_input, name='input-thread').start()

            while True:
                # Get CanBus input
                data = self.bus.receive()
                if(data is not None):
                    self.parent.add_item(data)

                # Draw the screen
                height, width = self.screen.getmaxyx()
                self.screen_lock.acquire()
                self.parent.resize(width, height, 0, 1)
                self.draw_banner()
                self.parent.draw()
                self.screen.refresh()
                self.screen_lock.release()

                # Check if thread needs to end
                self.mutex.acquire()
                self.mutex.wait_for(lambda: self.kill_threads,
                                    timeout=self.timeout)
                if(self.kill_threads):
                    break
                self.mutex.release()
        except KeyboardInterrupt:
            # Incredibly hacky workaround to the fact that
            #    threading.Condition() has no locked() function
            #
            #   Kids, don't try this at home.
            try:
                self.mutex.release()
            except RuntimeError:
                pass

            if(self.screen_lock.locked()):
                self.screen_lock.release()
        finally:
            self.stop()

    def stop(self):
        self.bus.stop_all()

        self.screen_lock.acquire()
        curses.nocbreak()  # Enable line buffering
        curses.echo()  # Enable user-input echo
        curses.curs_set(1)  # Enable the cursor
        curses.endwin()  # Destroy the virtual screen
        self.screen_lock.release()

        self.mutex.acquire()
        self.kill_thread = True
        self.mutex.notifyAll()
        self.mutex.release()

    def read_input(self):
        while True:
            try:
                # flush the input buffer then grab new user input
                self.screen_lock.acquire()
                input = self.screen.getch()
                curses.flushinp()

                # While locked, check what screen states need the change
                #   based in user input
                if(input == curses.KEY_DOWN):
                    self.selected.scroll()
                elif(input == curses.KEY_UP):
                    self.selected.scroll(-1)
                elif(input == curses.KEY_SR or input == curses.KEY_SLEFT):
                    self.pane_i -= 1
                elif(input == curses.KEY_SF or input == curses.KEY_SRIGHT):
                    self.pane_i += 1

                if(self.pane_i < 0):
                    self.pane_i = 0
                elif(self.pane_i >= len(self.panes)):
                    self.pane_i = len(self.panes) - 1
                self.select()
                self.screen_lock.release()

                # Check if the user input thread needs to end
                self.mutex.acquire()
                self.mutex.wait_for(lambda: self.kill_threads, timeout=self.timeout)
                if(self.kill_threads):
                    self.mutex.release()
                    break
                else:
                    self.mutex.release()
            except KeyboardInterrupt:
                pass

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
