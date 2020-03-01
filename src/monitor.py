import curses, time, json
from bus import Bus
from frame_table import FrameTable
from frame_data import FrameData, FrameType

def find_n(data, delim, n=0):
    pieces = data.split(delim, n + 1)
    if(len(pieces) <= (n + 1)): return -1
    return len(data) - len(pieces[-1]) - len(delim)

def delims(data, start, end='\0', n=0):
    return [ find_n(data, start, n) + 1,
             len(data) - find_n(data[::-1], end, n) - 1 ]

def app_refresh(window, scroll_pos=0):
    window.refresh(scroll_pos, 0, 1, 0, curses.LINES - 1, curses.COLS - 1)

def pad(data): return " " * (curses.COLS - len(data.expandtabs()))

def handle_interupt():
    print("Restoring the terminal to its previous state...")
    curses.nocbreak()
    curses.echo()
    curses.curs_set(1)
    curses.endwin()
    print("Done!")

def error(window, message):
    window.addstr(1, 1, "fatal error: " + message, curses.color_pair(1))
    app_refresh(window)
    while True: pass # Hang and never return

def load_config(window, filename):
    try:
        file = open(filename)
        raw_data = file.read()
        file.close()
        return json.loads(raw_data)
    except Exception as e: error(window, "malformed or non-existant file: " + filename)

def init_screen():
    screen = curses.initscr()
    screen.keypad(True)
    screen.timeout(100)
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)
    return screen

def init_devices(window, config):
    devs = []
    try:
        for name in config:
            dev = Bus(name)
            dev.start()
            devs.append(dev)
    except OSError as e: error(window, "failed to start device: " + name)
    return devs

def init_tables(window, config):
    tables = []
    try:
        for c in config:
            tables.append(FrameTable(c['name'], c['capacity'], c['stale_node_timeout'], c['dead_node_timeout']))
    except KeyError as e: error(window, "malformed config: " + str(c) + "\n\t\texpected field: " + str(e))
    return tables

def disp_banner(window, devices):
    window.erase() # Clear the banner

    # Display raw data
    data = "Time: (" + time.ctime() + ") | Devices: "
    window.addstr(data)

    for dev in devices:
        if(dev.is_dead()): pair = 1
        else: pair = 3
        window.addstr(str(dev) + " ", curses.color_pair(pair))

    # Reformat the printed data
    t_delims = delims(data, '(', ')', 0)
    window.chgat(0, t_delims[0], t_delims[1] - t_delims[0], curses.color_pair(1))

def disp_heartbeats(window, table):
    if(len(table) > 0):
        data = str(table)+ ":"
        if(table.max_table_size is not None): data += "(" + str(len(table)) + "/" + str(table.max_table_size) + ")"
        data += pad(data)
        window.addstr(data, curses.color_pair(5))

        data = "Id/Name:\t\tBus:\tStatus:"
        data += pad(data)
        window.addstr(data, curses.color_pair(6))

        # Display raw data
        for id in table.ids():
            frame = table[id]

            # Padding node name
            if(len(frame.name) <= 8): name_padding = "\t\t\t"
            elif(len(frame.name) <= 12): name_padding = "\t\t"
            else: name_padding = "\t"

            window.addstr(frame.name + name_padding + frame.ndev + "\t")
            if(frame.is_dead()): window.addstr("DEAD", curses.color_pair(1))
            elif(frame.is_stale()): window.addstr("STALE", curses.color_pair(2))
            else: status = window.addstr(str(frame), curses.color_pair(3))
            window.addstr("\n")
        window.addstr("\n")

def disp_table(window, table):
    if(len(table) > 0):
        data = str(table) + ":"
        if(table.max_table_size is not None): data += "(" + str(len(table)) + "/" + str(table.max_table_size) + ")"
        data += pad(data)
        window.addstr(data, curses.color_pair(5))

        data = "Id/Name:\t\tBus:\tType:\tData:"
        data += pad(data)
        window.addstr(data, curses.color_pair(6))

        # Display raw data
        for id in table.ids():
            frame = table[id]

            # Padding node name
            if(len(frame.name) <= 8): name_padding = "\t\t\t"
            elif(len(frame.name) <= 12): name_padding = "\t\t"
            else: name_padding = "\t"

            window.addstr(frame.name + name_padding + frame.ndev + "\t")
            window.addstr(str(frame.type), curses.color_pair(frame.type.value + 1))
            window.addstr("\t[ ")
            window.addstr(str(frame) + " ", curses.color_pair(4))
            window.addstr("]\n")
        window.addstr("\n")

def main(window):
    # Init scroll posiotion + default app window size
    scroll_pos = 0
    app_size = curses.LINES

    # Init curses color pairs
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_GREEN)
    curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_CYAN)

    stdscr = init_screen() # Open the standard output

    # UI setup
    app = curses.newwin(curses.LINES, curses.COLS)
    banner = app.subwin(1, curses.COLS, 0, 0)
    t_data = curses.newpad(app_size, curses.COLS)

    # Init config
    dev_config = load_config(t_data, "configs/devices.json")
    table_config = load_config(t_data, "configs/tables.json")

    # Refresh the screen
    app.refresh()
    banner.refresh()
    app_refresh(t_data)

    # Init the devices and tables
    devs = init_devices(t_data, dev_config)
    tables = init_tables(t_data, table_config)

    disp_banner(banner, devs) # Display banner

    # Event loop
    while True:
        # Update the table(s) per device
        for dev in devs:
            try:
                new_frame = FrameData(dev.recv(), dev.ndev)
                dev.reset()

                # Add to the correct table based on type
                if(new_frame == FrameType.HEARBEAT): tables[0].add(new_frame)
                elif(new_frame >= FrameType.SDO): tables[1].add(new_frame)
            except OSError as e:
                dev.incr()
                continue

        # Determine if the app window needs to grow
        #       (if 4/5ths the app window is being used)
        table_size = 0;
        for table in tables: table_size += len(table)

        if(table_size >= ((4 * app_size) / 5)):
            app_size *= 2
            t_data = curses.newpad(app_size, curses.COLS)

        # Display things
        disp_banner(banner, devs)
        t_data.erase()
        disp_heartbeats(t_data, tables[0])
        disp_table(t_data, tables[1])

        # Get user input and determine new scroll position if any
        input = stdscr.getch()
        curses.flushinp()
        if(input == curses.KEY_DOWN): scroll_pos += 5
        elif(input ==  curses.KEY_UP): scroll_pos -= 5

        # Check scroll overflow/underflow
        if(scroll_pos < 0): scroll_pos = 0
        elif(scroll_pos > app_size): scroll_pos = app_size

        # Refresh the screen
        app.refresh()
        banner.refresh()
        app_refresh(t_data, scroll_pos)
    stdscr.keypad(False) # Close the standard output

if __name__ == "__main__":
    try: curses.wrapper(main)
    except OSError as e: print("fatal error: " + str(e))
    except KeyboardInterrupt as e: handle_interupt()
