#!/usr/bin/env python3
import curses, sys
from pane import Pane
from enum import Enum

class Split(Enum):
    HORIZONTAL = 0
    VERTICAL = 1

    horizontal = HORIZONTAL
    vertical = VERTICAL

class Grid:
    def __init__(self, width, height, x_off = 0, y_off = 0, split = Split.VERTICAL):
        self.width = width
        self.height = height
        self.x_off = x_off
        self.y_off = y_off
        self.split = split
        self.items = []

    def resize(self, width, height, x_off, y_off):
        self.width = width
        self.height = height
        self.x_off = x_off
        self.y_off = y_off

    def add_pannel(self, pannel): self.items.append(pannel)

    def add_item(self, name, item):
        for i in self.items:
            if(type(i) == Grid): i.add_item(name, item)
            else:
                if(i.name == name): i.add(item)

    def draw(self):
        if(self.split == Split.HORIZONTAL):
            width = int(self.width / len(self.items))
            height = self.height
            h_off = 0
            w_off = width
        elif(self.split == Split.VERTICAL):
            width = self.width
            height = int(self.height / len(self.items))
            h_off = height
            w_off = 0

        for i, item in enumerate(self.items):
            if(type(item) == Pane): item.draw(width, height, i * w_off + self.x_off, i * h_off + self.y_off)
            else:
                item.resize(width, height, i * w_off + self.x_off, i * h_off + self.y_off)
                item.draw()

def construct_screen():
    # Init color pairs
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_GREEN)
    curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_CYAN)

    # Init screen
    screen = curses.initscr()
    screen.keypad(True)
    screen.timeout(100)
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)
    return screen

def destruct_screen():
    curses.nocbreak()
    curses.echo()
    curses.curs_set(1)
    curses.endwin()

def main(window):
    stdscr = construct_screen()
    height, width = stdscr.getmaxyx()
    fields = ["PID", "Name", "Data"]

    g1 = Grid(width, height)
    g2 = Grid(0, 0, split = Split.HORIZONTAL)
    g3 = Grid(0, 0)

    g1.add_pannel(g2)
    g1.add_pannel(Pane("D", fields))

    g2.add_pannel(g3)
    g2.add_pannel(Pane("C", fields))

    g3.add_pannel(Pane("A", fields))
    g3.add_pannel(Pane("B", fields))

    g1.add_item("D", True)
    g1.add_item("B", 420)
    g1.add_item("C", "Blaze it!")

    while True:
        height, width = stdscr.getmaxyx()
        g1.resize(width, height, 0, 1)
        g1.draw()

    destruct_screen()

if __name__ == '__main__': curses.wrapper(main)
