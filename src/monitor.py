import curses, time, json
from canard.hw import socketcan
from frame_table import FrameTable
from frame_data import FrameData, FrameType
from dictionaries import node_names, heartbeat_statuses

def find_n(data, delim, n=0):
    pieces = data.split(delim, n + 1)
    if(len(pieces) <= (n + 1)): return -1
    return len(data) - len(pieces[-1]) - len(delim)

def delims(data, start, end='\0', n=0):
    return [ find_n(data, start, n) + 1,
             len(data) - find_n(data[::-1], end, n) - 1 ]

def pad(data): return " " * (curses.COLS - len(data.expandtabs()))

def get_node_name(id):
    name = node_names.get(id)
    if(name is None): return str(hex(id))
    else: return name

def get_hb_status(code):
    state = heartbeat_statuses.get(code)
    if(state is None): return str(hex(code))
    else: return state

def error(window, message):
    window.addstr(1, 1, message, curses.color_pair(1))
    window.refresh()
    while True: pass # Hang and never return

def load_config(window, filename):
    try:
        file = open(filename)
        raw_data = file.read()
        file.close()
        return json.loads(raw_data)
    except Exception as e: error(window, "Fatal error: file does not exist " + filename)

def init_devices(window, config):
    devs = []
    try:
        for name in config:
            dev = socketcan.SocketCanDev(name)
            dev.socket.settimeout(0.1)
            dev.start()
            devs.append([True, dev])
    except OSError as e: error(window, "Fatal error: failed to open device " + name)
    return devs

def init_tables(window, config):
    tables = []
    try:
        for c in config:
            table = FrameTable(c['name'], c['capacity'], c['stale_node_timeout'], c['dead_node_timeout'])
            tables.append(table)
    except OSError as e: error(window, "Fatal error: " + str(e))
    return tables

def disp_banner(window, devices):
    window.erase() # Clear the banner

    # Display raw data
    data = "Time: (" + time.ctime() + ") | Devices: "
    window.addstr(data)

    for dev in devices:
        if(dev[0]): window.addstr(dev[1].ndev + " ", curses.color_pair(3))
        else: window.addstr(dev[1].ndev + " ", curses.color_pair(1))

    # Reformat the printed data
    t_delims = delims(data, '(', ')', 0)
    window.chgat(0, t_delims[0], t_delims[1] - t_delims[0], curses.color_pair(1))

def disp_heartbeats(window, table):
    if(len(table) > 0):
        data = table.name + ":"
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
            node_name = get_node_name(frame.id)
            if(len(node_name) <= 4): node_name += "\t\t\t"
            elif(len(node_name) <= 8): node_name += "\t\t\t"
            elif(len(node_name) <= 12): node_name += "\t\t"
            else: node_name += "\t"

            window.addstr(node_name + str(frame.ndev) + "\t")
            if(frame.is_dead()): window.addstr("DEAD", curses.color_pair(1))
            elif(frame.is_stale()): window.addstr("STALE", curses.color_pair(2))
            else: status = window.addstr(get_hb_status(frame.data[0]), curses.color_pair(3))
            window.addstr("\n")
        window.addstr("\n")

def disp_table(window, table):
    if(len(table) > 0):
        data = table.name + ":"
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
            node_name = get_node_name(frame.id)
            if(len(node_name) <= 4): node_name += "\t\t\t"
            elif(len(node_name) <= 8): node_name += "\t\t\t"
            elif(len(node_name) <= 12): node_name += "\t\t"
            else: node_name += "\t"

            window.addstr(node_name + str(frame.ndev) + "\t")
            window.addstr(str(frame.type), curses.color_pair(frame.type.value + 1))
            window.addstr("\t[ ")
            window.addstr(str(frame.hex_data_str()) + " ", curses.color_pair(4))
            window.addstr("]\n")
        window.addstr("\n")

def main(window):
    # Init scroll posiotion
    scroll_pos = 0
    app_size = curses.LINES

    # Init color pairs
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_GREEN)
    curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_CYAN)

    # Open the standard output
    stdscr = curses.initscr()
    stdscr.keypad(True)
    stdscr.timeout(100)
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)

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
    t_data.refresh(scroll_pos, 0, 1, 0, 10, 60)

    # Init the devices and tables
    devs = init_devices(t_data, dev_config)
    tables = init_tables(t_data, table_config)

    disp_banner(banner, devs) # Display banner

    # Event loop
    while True:
        # Update the table(s) per device
        for dev in devs:
            try:
                raw_frame = dev[1].recv()
                dev[0] = True

                new_frame = None
                id = raw_frame.id
                new_frame = FrameData(raw_frame, dev[1].ndev)

                # Determine the right table, adjust the ID, and insert
                if(id >= 0x701 and id <= 0x7FF): # Heartbeats
                    new_frame.id -= 0x700
                    new_frame.type = FrameType.HEARBEAT
                    tables[0].add(new_frame)
                elif(id >= 0x581 and id <= 0x5FF): # SDO tx
                    new_frame.id -= 0x580
                    new_frame.type = FrameType.SDO
                    tables[1].add(new_frame)
                elif(id >= 0x601 and id <= 0x67F): # SDO rx
                    new_frame.id -= 0x600

                    new_frame.type = FrameType.SDO
                    tables[1].add(new_frame)
                elif(id >= 0x181 and id <= 0x57F): # PDO
                    new_frame.id -= 0x181
                    new_frame.type = FrameType.PDO
                    tables[1].add(new_frame)
                else: tables[1].add(new_frame) # Other
            except OSError as e:
                dev[0] = False
                continue

        # Determine if the app window needs to grow
        table_size = 0;
        for table in tables: table_size += len(table)

        if(table_size >= ((3 * app_size) / 4)):
            app_size *= 2
            t_data = curses.newpad(app_size, curses.COLS)

        # Display things
        disp_banner(banner, devs)
        t_data.erase() # Clear the table window
        disp_heartbeats(t_data, tables[0])
        disp_table(t_data, tables[1])

        # Get user input
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
        t_data.refresh(scroll_pos, 0, 1, 0, curses.LINES - 1, curses.COLS - 1)

    # Close the standard output
    stdscr.keypad(False)
    curses.nocbreak()
    curses.echo()
    curses.curs_set(1)
    curses.endwin()

if __name__ == "__main__":
    try: curses.wrapper(main)
    except OSError as e: print("fatal error: " + str(e))
