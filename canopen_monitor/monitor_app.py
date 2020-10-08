import time
import curses
import threading
import canopen_monitor
from .ui.pane import HeartBeatPane, InfoPane, Pane
from .ui.windows import PopupWindow
from .ui.grid import Grid, Split
from .parser.canopen import CANOpenParser
from .canmsgs.magic_can_bus import MagicCANBus


class MonitorApp:
    """The top-level application of Can Monitor that manages the middleware
    resoruces and the UI elements.

    Attributes
    ---------
    """

    def __init__(self,
                 devices: [str],
                 timeouts: tuple,
                 table_schema: dict,
                 eds_configs: dict):
        # Monitor setup
        self.screen = curses.initscr()  # Initialize standard out
        self.screen.scrollok(True)      # Enable window scroll
        self.screen.keypad(True)        # Enable special key input
        self.screen.nodelay(True)       # Disable user-input blocking

        # Bus things
        self.devices = devices
        self.bus = MagicCANBus(interface_names=self.devices,
                               stale_timeout=timeouts[0],
                               dead_timeout=timeouts[1])
        self.parser = CANOpenParser(eds_configs)

        # panel selection things
        self.panel_index = 0       # Index to get to selected panel
        self.panel_flatlist = []   # List of all Panes contained in parent
        self.selected = None        # Reference to currently selected pane

        # Threading things
        self.screen_lock = threading.Lock()
        self.stop_listening = threading.Event()

        # Curses configuration
        curses.savetty()        # Save the terminal state
        curses.raw()            # Enable raw input (DISABLES SIGNALS)
        curses.noecho()         # Disable user-input echo
        curses.cbreak()         # Disable line-buffering (less input delay)
        curses.curs_set(False)  # Disable the cursor display

        # Curses colors
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)

        # Construct the grid(s)
        self.construct_grid(table_schema)

    def start(self):
        while not self.stop_listening.is_set():
            # Get CanBus input
            data = self.bus.receive()
            if(data is not None):
                self.parent.add_frame(data)

            # Get user input
            self.read_input()

            # Draw the screen
            self.screen_lock.acquire()
            self.draw_banner()
            self.parent.draw()
            self.screen_lock.release()

    def stop(self):
        curses.nocbreak()           # Re-enable line-buffering
        curses.echo()               # Enable user-input echo
        curses.curs_set(True)       # Enable the cursor
        curses.resetty()            # Restore the terminal state
        curses.endwin()             # Destroy the virtual screen
        self.stop_listening.set()   # Signal the bus threads to stop

        if(canopen_monitor.DEBUG):  # Extra canopen_monitor.DEBUG info
            print('stopping bus-listeners from the app-layer...')

        self.bus.stop_all()         # Wait for all CanBus threads to stop

        if(canopen_monitor.DEBUG):  # Extra canopen_monitor.DEBUG info
            print('stopped all bus-listeners!')

        threads = threading.enumerate().remove(threading.current_thread())
        if(canopen_monitor.DEBUG):  # Extra canopen_monitor.DEBUG info
            print('waiting for all app-threads to close...')

        # If app-layer threads exist wait for them to close
        if(threads is not None):
            for thread in threads:
                thread.join()
            if(canopen_monitor.DEBUG):  # Extra canopen_monitor.DEBUG info
                print('stopped all app-threads gracefully!')

        elif(canopen_monitor.DEBUG):  # Extra canopen_monitor.DEBUG info
            print('no child app-threads were spawned!')

    def read_input(self):
        # Grab new user input and immediately flush the buffer
        key = self.screen.getch()
        curses.flushinp()

        # Determine the key input
        if(key == curses.KEY_RESIZE):
            self.screen.clear()
            self.parent.clear()
            self.parent.resize(self.screen)
        elif(key == curses.KEY_F1):
            window_message = '\n'.join([canopen_monitor.APP_DESCRIPTION,
                                        'Author: ' + canopen_monitor.APP_AUTHOR,
                                        'Email: ' + canopen_monitor.APP_EMAIL,
                                        'License: ' + canopen_monitor.APP_LICENSE,
                                        'Version: ' + canopen_monitor.APP_VERSION,
                                        'Website: ' + canopen_monitor.APP_URL])
            PopupWindow(self.screen,
                        window_message,
                        banner='About ' + canopen_monitor.APP_NAME,
                        color_pair=1)
        elif(key == curses.KEY_F2):
            PopupWindow(self.screen, "<Ctrl+C>: Exit program\
                                     \n\nInfo:\
                                     \n\t<F1>: App Info\
                                     \n\t<F2>: Controls\
                                     \n\nMovement:\
                                     \n\t<UP>: Scroll up\
                                     \n\t<DOWN>: Scroll down\
                                     \n\t<Ctrl+UP>: Fast scroll up\
                                     \n\t<Ctrl+DOWN>: Fast scroll down\
                                     \n\t<Shift+UP>: Select previous pane\
                                     \n\t<Shift+DOWN>: Select next pane",
                        banner='Controls',
                        color_pair=1)
        elif((key == curses.KEY_SR or key == curses.KEY_SLEFT)
                and self.panel_index > 0):
            self.panel_index -= 1
            self.update_selected_panel()
        elif((key == curses.KEY_SF or key == curses.KEY_SRIGHT)
                and self.panel_index < len(self.panel_flatlist) - 1):
            self.panel_index += 1
            self.update_selected_panel()
        elif(key == curses.KEY_UP):
            self.selected.scroll_up()
        elif(key == curses.KEY_DOWN):
            self.selected.scroll_down()
        elif(key == 567 or key == 546):  # Ctrl+Up or Ctrl+Left
            self.selected.scroll_up(rate=10)
        elif(key == 526 or key == 561):  # Ctrl+Down or Ctrl+Right
            self.selected.scroll_down(rate=10)

    def draw_banner(self):
        _, width = self.screen.getmaxyx()
        self.screen.addstr(0, 0, time.ctime(), curses.color_pair(0))
        self.screen.addstr(" | ")

        running = list(map(lambda x: x.ndev, self.bus.running()))
        for dev in self.devices:
            if(dev in running):
                color = 1
            else:
                color = 3

            self.screen.addstr(dev + " ", curses.color_pair(color))

        hottip = '<F1: Info> <F2: Controls>'
        self.screen.addstr(0, width - len(hottip), hottip)

    def update_selected_panel(self):
        if(self.selected is not None):
            self.selected.selected = False
        self.selected = self.panel_flatlist[self.panel_index]
        self.selected.selected = True

    def construct_grid(self, schema, parent=None):
        # Required attributes
        type = schema.get('type')
        split = schema.get('split')
        data = schema.get('data')
        split = {'horizontal': Split.HORIZONTAL,
                 'vertical': Split.VERTICAL}.get(split)

        # Optional attributes
        name = schema.get('name')
        fields = schema.get('fields')
        capacity = schema.get('capacity')
        frame_types = schema.get('frame_types')

        if(parent is None):
            self.parent = Grid(parent=self.screen, split=split)

            for entry in data:
                self.construct_grid(entry, self.parent)
            self.panel_flatlist = self.parent.flatten()
            self.update_selected_panel()
        else:
            if(type == 'grid'):
                component = Grid(split=split)

                for entry in data:
                    self.construct_grid(entry, component)
            elif(type == 'heartbeat_table'):
                component = HeartBeatPane(name,
                                          self.parser,
                                          capacity=capacity,
                                          fields=fields,
                                          frame_types=frame_types)
            elif(type == 'misc_table'):
                component = Pane(name,
                                 self.parser,
                                 capacity=capacity,
                                 fields=fields,
                                 frame_types=frame_types)
            elif(type == 'info_table'):
                component = InfoPane(name, self.parser)
            else:
                raise ValueError('Failed to parse layout! Invalid table type: {}'
                                 .format(type))
            parent.add_panel(component)
