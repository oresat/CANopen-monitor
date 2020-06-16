#!/usr/bin/env python3
import sys
import curses
import time
from enum import Enum


class Split(Enum):
    HORIZONTAL = 0
    VERTICAL = 1


class Grid:
    def __init__(self, parent=None, split=Split.VERTICAL):
        if(parent is None):
            self.parent = curses.newwin(0, 0, 0, 0)
        else:
            height, width = parent.getmaxyx()
            self.parent = curses.newwin(height - 1, width, 1, 0)

        self.split = split
        self.pannels = []

    def draw(self):
        for pannel in self.pannels:
            pannel.draw()

    def clear(self):
        for pannel in self.pannels:
            pannel.clear()
        self.parent.clear()

    def add_pannel(self, pannel):
        self.pannels.append(pannel)
        self.resize()

    def resize(self, parent=None):
        if(parent is not None):
            height, width = parent.getmaxyx()
            self.parent = curses.newwin(height - 1, width, 1, 0)

        p_height, p_width = self.parent.getmaxyx()
        py_offset, px_offset = self.parent.getbegyx()
        p_count = len(self.pannels)

        for i, pannel in enumerate(self.pannels):
            if(self.split == Split.HORIZONTAL):
                width = int(p_width / p_count)
                height = p_height
                x_offset = i * width + px_offset
                y_offset = 0 + py_offset
            else:
                width = p_width
                height = int(p_height / p_count)
                x_offset = 0 + px_offset
                y_offset = i * height + py_offset
            pannel.parent.resize(height, width)
            pannel.parent.mvwin(y_offset, x_offset)

            if(type(pannel) is Grid):
                pannel.resize()


class Pane:
    def __init__(self, name):
        self.name = name
        self.parent = curses.newwin(0, 0)

    def draw(self):
        height, width = self.parent.getmaxyx()
        self.parent.box()
        self.parent.addstr(0, 1, self.name + ":0(" + str(width) + ", " + str(height) + ")")
        self.parent.refresh()

    def clear(self):
        self.parent.clear()


def setup():
    screen = curses.initscr()
    curses.savetty()
    curses.cbreak()
    curses.noecho()
    curses.curs_set(False)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_RED)

    return screen


def teardown():
    curses.echo()
    curses.resetty()
    curses.endwin()


def main(args):
    try:
        stdscr = setup()
        height, width = stdscr.getmaxyx()

        g1 = Grid(stdscr)
        g2 = Grid(split=Split.HORIZONTAL)
        g3 = Grid()

        g3.add_pannel(Pane("A"))
        g3.add_pannel(Pane("B"))

        g2.add_pannel(g3)

        g2.add_pannel(Pane("C"))
        g2.add_pannel(Pane("D"))

        g1.add_pannel(g2)
        g1.add_pannel(Pane("E"))

        stdscr.nodelay(True)
        stdscr.keypad(True)

        while True:
            key = stdscr.getch()

            if(key == curses.KEY_RESIZE):
                stdscr.clear()
                g1.clear()
                g1.resize(stdscr)
            stdscr.addstr(0, 0, time.ctime())
            try:
                g1.draw()
            except curses.error as e:
                _, width = stdscr.getmaxyx()
                msg = str(e)
                offset = width - len(msg)
                stdscr.addstr(0, offset, msg, curses.color_pair(2))
    finally:
        teardown()


if __name__ == "__main__":
    main(sys.argv[1:])
