import curses
import time
import json
from .bus import Bus
from .frame_data import FrameData
from .frame_table import FrameTable
from .grid import Grid, Split
from .pane import Pane
from .utilities import load_config, config_factory

SCROLL_RATE = 5


def init_devices(window, config):
    devs = []
    try:
        for name in config:
            dev = Bus(name)
            dev.start()
            devs.append(dev)
    except OSError:
        error(window, "failed to start device: " + name)
    return devs


def init_tables(window, config):
    '''Initialize all of the '''
    tables = []
    try:
        for c in config:
            tables.append(FrameTable(c['name'],
                                     c['capacity'],
                                     c['stale_node_timeout'],
                                     c['dead_node_timeout']))
    except KeyError as e:
        error(window, "malformed config: "
              + str(c)
              + "\n\t\texpected field: " + str(e))
    return tables


def error(window, message):
    '''Displays an error message via ncurses then hangs and never returns.'''
    window.addstr(1, 1, "fatal error: " + message, curses.color_pair(1))
    window.refresh()
    while True:
        pass


def construct_screen():
    '''Construct the virtual screen and initialize global color pairs.'''
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_GREEN)
    curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_CYAN)
    curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_YELLOW)

    screen = curses.initscr()  # Construct the virtual screen
    screen.keypad(True)  # Enable keypad
    screen.timeout(1)  # Set user-input timeout (ms)
    curses.noecho()  # Disable user-input echo
    curses.cbreak()  # Disable line buffering
    curses.curs_set(0)  # Disable cursor
    return screen


def destruct_screen():
    '''Destroy the virtual screen and restore original display settings.'''
    curses.nocbreak()  # Enable line buffering
    curses.echo()  # Enable user-input echo
    curses.curs_set(1)  # Enable the cursor
    curses.endwin()  # Destroy the virtual screen


def draw_banner(window, devices, selected):
    window.addstr(0, 1, "")
    window.addstr(time.ctime(), curses.color_pair(1))
    window.addstr(" | devices: [ ")

    for dev in devices:
        if(dev.is_dead()):
            color = 2
        else:
            color = 3
        window.addstr(dev.ndev + " ", curses.color_pair(color))

    window.addstr("] | " + selected.name + "\t\t")
    window.refresh()


def start(window):
    stdscr = construct_screen()
    height, width = stdscr.getmaxyx()
    banner = curses.newwin(1, width, 0, 0)
    # fields = ["COB ID", "Node Name", "Bus", "Type", "Data"]
    fields = ["Data"]

    # Init configs
    try:
        dev_config = load_config("~/.canmon/devices.json")
    except FileNotFoundError as e:
        config_factory(e.filename)
        dev_config = load_config(e.filename)
    except json.decoder.JSONDecodeError as e:
        error(dev_config, "malformed config file: " + e.doc + "\n\t" + str(e))

    try: table_config = load_config("~/.canmon/tables.json")
    except FileNotFoundError as e:
        config_factory(e.filename)
        table_config = load_config(e.filename)
    except json.decoder.JSONDecodeError as e: error(t_data, "malformed config file: " + e.doc + "\n\t" + str(e))

    # Init the devices and tables
    devs = init_devices(stdscr, dev_config)
    tables = init_tables(stdscr, table_config)

    # Init the grid(s)
    g1 = Grid(split = Split.HORIZONTAL)
    g2 = Grid()

    g1.add_pannel(g2)
    g1.add_pannel(Pane("Misc", fields))

    g2.add_pannel(Pane("Hearbeat", fields))
    g2.add_pannel(Pane("PDO", fields))

    panes = g1.flat_pannels()
    pane_index = 0
    selected = panes[pane_index]
    selected.selected = True

    n = [
        "Misc",
        "Hearbeat",
        "PDO"
    ]
    i = 0

    # Event loop
    while True:
        # Update bus status(es)
        for d in devs:
            try:
                new_frame = FrameData(d.recv(), d.ndev)
                d.reset()

                g1.add_item(n[i], new_frame)
                i += 1
                if(i > 2): i = 0
            except OSError:
                d.incr()
                continue

        # Display stuff
        height, width = stdscr.getmaxyx()
        g1.resize(width, height, 0, 1)
        draw_banner(banner, devs, selected)
        g1.draw()

        # Get user input and determine new scroll position if any
        input = stdscr.getch()
        curses.flushinp()

        if(input == curses.KEY_DOWN):
            selected.scroll()
        elif(input ==  curses.KEY_UP):
            selected.scroll(-1)
        elif(input == curses.KEY_SR or input == curses.KEY_SLEFT):
            pane_index -= 1
        elif(input == curses.KEY_SF or input == curses.KEY_SRIGHT):
            pane_index += 1

        if(pane_index < 0): pane_index = 0
        elif(pane_index >= len(panes)): pane_index = len(panes) - 1

        selected.selected = False
        selected = panes[pane_index]
        selected.selected = True

    # Restore the terminal
    destruct_screen()
