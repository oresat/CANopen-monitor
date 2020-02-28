import curses, time, json
from canard.hw import socketcan
from frame_table import FrameTable
from frame_data import FrameData, FrameType

def find_n(data, delim, n=0):
    pieces = data.split(delim, n + 1)
    if(len(pieces) <= (n + 1)): return -1
    return len(data) - len(pieces[-1]) - len(delim)

def delims(data, start, end='\0', n=0):
    return [ find_n(data, start, n) + 1,
             len(data) - find_n(data[::-1], end, n) - 1 ]

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
            dev.socket.settimeout(0.5)
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
    window.clear() # Clear the banner

    # Display raw data
    data = "Time: (" + time.ctime() + ") | Devices: " + str(devices)
    window.addstr(data)

    # Reformat the printed data
    t_delims = delims(data, '(', ')', 0)
    d_delims = delims(data, '[', ']', 0)
    window.chgat(0, t_delims[0], t_delims[1] - t_delims[0], curses.color_pair(1))
    window.chgat(0, d_delims[0], d_delims[1] - d_delims[0], curses.color_pair(2))

def disp_heartbeats(window, table):
    if(len(table) > 0):
        window.addstr("\n " + table.name + ": ")
        if(table.max_table_size is not None): window.addstr("(" + str(len(table)) + "/" + str(table.max_table_size) + ")")
        window.addstr("\n Id:\tDevice:\tStatus:\n")

        # Display raw data
        for id in table.ids():
            frame = table[id]
            if(frame.is_dead()): status = "DEAD"
            elif(frame.is_stale()): status = "STALE"
            else: status = str(hex(frame.data[0]))

            data = str(hex(frame.id)) + "\t" + str(frame.ndev) + "\t" + status
            window.addstr(" " + data + "\n")

def disp_table(window, table):
    if(len(table) > 0):
        window.addstr("\n " + table.name + ": ")
        if(table.max_table_size is not None): window.addstr("(" + str(len(table)) + "/" + str(table.max_table_size) + ")")
        window.addstr("\n Id:\tDevice:\tType:\tData:\n")

        # Display raw data
        for frame in table.table.values():
            data = str(hex(frame.id)) + "\t" + str(frame.ndev) + "\t" + str(frame.type) + "\t" + str(frame.hex_data_str())
            window.addstr(" " + data + "\n")

            # Reformat the printed data
            # d_delims = delims(data, '[', ']', 0)
            # window.chgat(d_delims[0], d_delims[1] - d_delims[0], curses.color_pair(2))

def main(window):
    # Init color pairs
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_GREEN)

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
    t_data = app.subwin(curses.LINES - 1, curses.COLS, 1, 0)

    # Init config
    dev_config = load_config(t_data, "configs/devices.json")
    table_config = load_config(t_data, "configs/tables.json")

    # Display bcanner
    disp_banner(banner, dev_config)

    # Refresh the screen
    app.refresh()
    banner.refresh()
    t_data.refresh()
    curses.doupdate()

    # Init the devices and tables
    devs = init_devices(t_data, dev_config)
    tables = init_tables(t_data, table_config)

    # Event loop
    while True:
        # Update the table(s)
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

        # Display things
        t_data.clear() # Clear the table window
        disp_banner(banner, dev_config)
        disp_heartbeats(t_data, tables[0])
        disp_table(t_data, tables[1])
        t_data.box()

        # Refresh the screen
        app.refresh()
        banner.refresh()
        t_data.refresh()
        # curses.doupdate()

    # Close the standard output
    stdscr.keypad(False)
    curses.nocbreak()
    curses.echo()
    curses.curs_set(1)
    curses.endwin()

if __name__ == "__main__":
    try: curses.wrapper(main)
    except OSError as e: print("fatal error: " + str(e))
