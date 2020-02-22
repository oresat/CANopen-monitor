#!/usr/bin/env python3
import curses, time, sys

devs = [ 'vcan0', 'vcan1' ]

t1 = [
    100,
    21,
    1234123,
    2134
]

t2 = [
    103550,
    223451,
    1234156723,
    2235134
]

t3 = [
    178900,
    21,
    1209078934123,
    2789134
]

tables = [
    { 'name': 'table 1', 'data': t1},
    { 'name': 'table 2', 'data': t2},
    { 'name': 'table 3', 'data': t3} ]

def find_n(data, delim, n=0):
    pieces = data.split(delim, n + 1)
    if(len(pieces) <= (n + 1)): return -1
    return len(data) - len(pieces[-1]) - len(delim)

def delims(data, start, end='\0', n=0):
    return [ find_n(data, start, n) + 1,
             len(data) - find_n(data[::-1], end, n) - 1 ]

def disp_banner(window):
    window.clear() # Clear the banner

    # Display raw data
    data = "Time: (" + time.ctime() + ") | Devices: " + str(devs)
    window.addstr(data)

    # Reformat the printed data
    t_delims = delims(data, '(', ')', 0)
    d_delims = delims(data, '[', ']', 0)
    window.chgat(0, t_delims[0], t_delims[1] - t_delims[0], curses.color_pair(1))
    window.chgat(0, d_delims[0], d_delims[1] - d_delims[0], curses.color_pair(2))

def disp_table(window, table):
    window.clear() # Clear the table window

    # Display raw data
    data = table['name'] + ": " + str(table['data']) + str(window.getyx())
    window.addstr(data)

    # Reformat the printed data
    d_delims = delims(data, '[', ']', 0)
    window.chgat(d_delims[0], d_delims[1] - d_delims[0], curses.color_pair(2))

def main(window):
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_GREEN)

    # Open the standard output
    stdscr = curses.initscr()
    stdscr.keypad(True)
    stdscr.timeout(500)
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)

    # UI setup
    app = curses.newpad(curses.LINES - 1, curses.COLS)
    banner = app.subpad(1, curses.COLS, 0, 0)
    t_data = app.subpad(curses.LINES - 2, curses.COLS, 1, 0)

    disp_banner(banner)
    t_data.box()

    # Refresh the screen
    app.refresh(curses.LINES - 1, curses.COLS, 0, 0, 0, 0)
    banner.refresh(0, 0, 0, curses.COLS, 0, curses.COLS)
    t_data.refresh(0, 0, curses.LINES - 1, curses.COLS, curses.LINES - 1, curses.COLS)
    curses.doupdate()

    # Event loop
    while True:
        disp_banner(banner)
        for table in tables: disp_table(t_data, table)

        time.sleep(1)
        # stdscr.scroll(1)

        # Refresh the screen
        app.refresh(curses.LINES - 1, curses.COLS, 0, 0, 0, 0)
        banner.refresh(0, 0, 0, curses.COLS, 0, curses.COLS)
        t_data.refresh(0, 0, curses.LINES - 1, curses.COLS, curses.LINES - 1, curses.COLS)
        curses.doupdate()

    # Close the standard output
    stdscr.keypad(False)
    curses.nocbreak()
    curses.echo()
    curses.curs_set(1)
    curses.endwin()

if __name__ == "__main__":
    try: curses.wrapper(main)
    except OverflowError as e: print("fatal error: " + str(e))
