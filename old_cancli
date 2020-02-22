#!/usr/bin/env python3
import curses, time, sys
from canard.hw import socketcan
from frame_data import FrameData
from frame_table import FrameTable, FrameType

DEBUG = True

def usage(screen):
    screen.addstr("Error: No devices specified!\n\tusage: " + sys.argv[0].split('/')[-1] + " <devices>\n", curses.color_pair(3))
    screen.refresh()

def data_to_hexstr(data):
    res = "[ "
    for i in data:
        res += str(hex(i)) + " "
    res += "]"
    return res

def display_banner(screen, table, banner):
    # Determine if the table has a max size to display
    table_header = str(table.name) + ": " + "(" + str(len(table))
    if(table.max_table_size is not None): table_header += "/" + str(table.max_table_size)
    table_header += " nodes)"

    # Display the header + banner
    screen.addstr(table_header, curses.color_pair(5))
    screen.chgat(-1, curses.color_pair(5))
    screen.addstr(banner, curses.color_pair(6))
    screen.chgat(-1, curses.color_pair(6))
    return 2

def display_heartbeat(screen, table, budget):
    lcount = display_banner(screen, table, "Id\tDevice\tStatus")

    for k in sorted(table.table.keys()): # Get list of sorted keys
        lcount += 1
        if(lcount < budget):
            frame = table.table[k]

            # Display the node with color
            screen.addstr(str(hex(frame.id)) + "\t" + str(frame.ndev) + "\t")
            if(frame.is_dead()): screen.addstr("DEAD", curses.color_pair(3))
            elif(frame.is_stale()): screen.addstr("STALE", curses.color_pair(2))
            else: screen.addstr(str(hex(frame.data[0])), curses.color_pair(1))
            screen.addstr("\n")
        else: break
    return lcount

def display_rdo(screen, table, budget):
    lcount = display_banner(screen, table, "Id\tDevice\tStatus\tData")

    for k in sorted(table.table.keys()): # Get list of sorted keys
        lcount += 1
        if(lcount < budget):
            frame = table.table[k]

            # Display the node with color
            screen.addstr(str(hex(frame.id)) + "\t" + str(frame.ndev) + "\t")
            if(frame.is_dead()): screen.addstr("DEAD", curses.color_pair(3))
            elif(frame.is_stale()): screen.addstr("STALE", curses.color_pair(2))
            else: screen.addstr("ALIVE", curses.color_pair(1))
            screen.addstr("\t" + data_to_hexstr(frame.data) + "\n", curses.color_pair(4))
        else: break
    return lcount

def display_pdo(screen, table, budget):
    lcount = display_banner(screen, table, "Id\tDevice\tPDO\tTx\tRx")

    for k in sorted(table.table.keys()): # Get list of sorted keys
        lcount += 1
        if(lcount < budget):
            frame = table.table[k]

            # Display the node with color
            screen.addstr(str(hex(frame.id)) + "\t" + str(frame.ndev) + "\t")
            if(frame.is_dead()): screen.addstr("DEAD", curses.color_pair(3))
            elif(frame.is_stale()): screen.addstr("STALE", curses.color_pair(2))
            else: screen.addstr("ALIVE", curses.color_pair(1))
            screen.addstr("\t" + data_to_hexstr(frame.data) + "\n", curses.color_pair(4))
        else: break
    return lcount

def display_misc(screen, table, budget):
    lcount = display_banner(screen, table, "Id\tDevice\tStatus\tData")

    for k in sorted(table.table.keys()): # Get list of sorted keys
        lcount += 1
        if(lcount < budget):
            frame = table.table[k]

            # Display the node with color
            screen.addstr(str(hex(frame.id)) + "\t" + str(frame.ndev) + "\t")
            if(frame.is_dead()): screen.addstr("DEAD", curses.color_pair(3))
            elif(frame.is_stale()): screen.addstr("STALE", curses.color_pair(2))
            else: screen.addstr("ALIVE", curses.color_pair(1))
            screen.addstr("\t" + data_to_hexstr(frame.data) + "\n", curses.color_pair(4))
        else: break
    return lcount

def main(window=None):
    # Init the colors
    # Color pair 0: Default White/Black
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_GREEN)
    curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_CYAN)

    # Table Setup
    tables = [ FrameTable("Heartbeat", FrameType.HEARBEAT),
               FrameTable("SDO's", FrameType.RDO),
               FrameTable("PDO's", FrameType.PDO),
               FrameTable("Miscellaneous", FrameType.MISC, 32) ]

    # Open the standard output
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)

    # Check for command line arguments
    if(len(sys.argv) < 2): usage(stdscr)
    dev_names = sys.argv[1:]

    # Open the sockets
    try:
        devs = []
        for name in dev_names:
            dev = socketcan.SocketCanDev(name)
            dev.start()
            devs.append([True, dev])
    except OSError as e:
        stdscr.addstr("Error: device does not exist: " + name, curses.color_pair(3))
        stdscr.refresh()

    # UI Setup
    banner = curses.newwin(0, curses.COLS, 1, 0)
    banner.addstr(0, 0, "Time: ")
    banner.addstr(time.ctime(), curses.color_pair(3))
    banner.addstr("\tDevices: [ ")
    for dev in devs: banner.addstr(str(dev[1].ndev) + " ", curses.color_pair(1))
    stdscr.addstr("]")

    t_screen = curses.newwin(curses.LINES, curses.COLS, 1, 0)

    # Event loop
    while True:
        used_height = 1
        height, width = stdscr.getmaxyx() # Get screen height/width

        # Recieve messages from the CAN bus devices in a round-robin fashion
        for dev in devs:
            try:
                raw_frame = dev[1].recv()
                dev[0] = True
            except OSError as e:
                dev[0] = False
                continue

            new_frame = None
            id = raw_frame.id
            new_frame = FrameData(raw_frame, dev[1].ndev)

            # Determine the right table, adjust the ID, and insert
            if(id >= 0x701 and id <= 0x7FF): # Heartbeats
                new_frame.id -= 0x700
                tables[0].add(new_frame)
            elif(id >= 0x581 and id <= 0x5FF): # SDO tx
                new_frame.id -= 0x580
                tables[1].add(new_frame)
            elif(id >= 0x601 and id <= 0x67F): # SDO rx
                new_frame.id -= 0x600
                tables[1].add(new_frame)
            elif(id >= 0x181 and id <= 0x57F): # PDO
                new_frame.id -= 0x181
                tables[2].add(new_frame)
            else: tables[3].add(new_frame) # Other

            # Display the tables
            for table in tables:
                if(len(table) > 0):
                    if((height - used_height > 2) and (table.type == FrameType.HEARBEAT)): used_height += display_heartbeat(t_screen, table, height - used_height)
                    elif((height - used_height > 2) and (table.type == FrameType.RDO)): used_height += display_rdo(t_screen, table, height - used_height)
                    elif((height - used_height > 2) and (table.type == FrameType.PDO)): used_height += display_pdo(t_screen, table, height - used_height)
                    elif(height - used_height > 2): used_height += display_misc(t_screen, table, height - used_height)
        stdscr.refresh()
        banner.refresh()
        t_screen.refresh()
        curses.doupdate()

    # Close the standard input
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.curs_set(1)
    curses.endwin()

if __name__ == "__main__":
    try: curses.wrapper(main)
    except OverflowError as e: print("fatal error: " + str(e))
