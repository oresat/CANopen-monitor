#!/usr/bin/env python3
import sys
import curses
import time


def setup():
    screen = curses.initscr()
    curses.savetty()
    curses.cbreak()
    # curses.raw()
    curses.noecho()
    curses.curs_set(False)

    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)

    return screen


def teardown():
    curses.echo()
    curses.resetty()
    curses.endwin()


def main(args):
    options = args
    scroll_pos = 0
    selection = None
    running = True

    try:
        stdscr = setup()
        menu = curses.newwin(0, 0)
        menu.keypad(True)
        menu.nodelay(True)

        while running:
            key = menu.getch()
            curses.flushinp()

            if(key == curses.KEY_UP and scroll_pos > 0):
                scroll_pos -= 1
            elif(key == curses.KEY_DOWN and scroll_pos < (len(options) - 1)):
                scroll_pos += 1
            elif(key == curses.KEY_ENTER):
                selection = scroll_pos
            elif(key == curses.KEY_RESIZE):
                stdscr.clear()
                menu.clear()
            elif(key == ord('q')):
                running = False
            elif(curses.has_key(key)):
                cmd = str(curses.keyname(key))
                stdscr.addstr(3, 3, cmd)

            height, width = stdscr.getmaxyx()
            stdscr.addstr(0, 0, str(time.thread_time_ns()))
            if(selection is not None and len(options) > 0):
                stdscr.clear()
                stdscr.addstr(int(height / 2), int(width / 2) - 5,
                              "Selected: " + options[selection])
                selection = None
            stdscr.refresh()

            menu.attron(curses.color_pair(1))
            menu.resize(len(options) + 2, int(2 * width / 3))
            menu.mvwin(int((height - len(options)) / 2), int(width / 6))
            menu.box()
            menu.addstr(0, 0, 'Menu:', curses.A_UNDERLINE | curses.color_pair(1))
            menu.attroff(curses.color_pair(1))

            for i, o in enumerate(options):
                if(scroll_pos == i):
                    menu.attron(curses.A_BOLD)
                menu.addstr(1 + i, 1, o)
                menu.attroff(curses.A_BOLD)
            menu.refresh()
    finally:
        teardown()


if __name__ == "__main__":
    main(sys.argv[1:])
