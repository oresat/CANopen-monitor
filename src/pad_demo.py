#!/usr/bin/env python3
import curses, random, time

def get_random_number():
    time.sleep(1)
    return str(random.randint(1000000,1000000000))

def main(window):
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)

    # Open the standard output
    stdscr = curses.initscr()
    stdscr.keypad(True)
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)

    # UI Setup
    stdscr.timeout(500)
    stdscr.addstr(0, 0, "RANDOM NUMBER GENERATOR", curses.A_REVERSE)
    stdscr.chgat(-1, curses.A_REVERSE)

    stdscr.addstr(curses.LINES - 1, 0, "Press (R) to request a new random number, (Q) to quit")
    stdscr.chgat(curses.LINES - 1, 7, 1, curses.A_BOLD | curses.color_pair(2))
    stdscr.chgat(curses.LINES - 1, 43, 1, curses.A_BOLD | curses.color_pair(1))

    quote_window = curses.newwin(curses.LINES - 2, curses.COLS, 1, 0)
    text_window = quote_window.subwin(curses.LINES - 6, curses.COLS - 4, 3, 2)
    text_window.addstr(1, 0, "Press R to get your first random number!")
    quote_window.box()

    stdscr.noutrefresh()
    quote_window.noutrefresh()
    text_window.noutrefresh()
    curses.doupdate()

    # Event loop
    while True:
        input = stdscr.getch()
        if(input == ord('r')):
            text_window.clear()
            text_window.addstr(0, 0, "Getting random number...", curses.color_pair(3))
            text_window.refresh()
            text_window.clear()
            text_window.addstr(get_random_number())
        elif(input == ord('q')):
            break
        else:
            text_window.refresh()
            text_window.clear()

        text_window.addstr(0,0, "Date: " + time.ctime())

        stdscr.noutrefresh()
        quote_window.noutrefresh()
        text_window.noutrefresh()
        curses.doupdate()

    # Close the standard output
    stdscr.keypad(False)
    curses.nocbreak()
    curses.echo()
    curses.curs_set(1)
    curses.endwin()

if __name__ == "__main__": curses.wrapper(main)
