from __future__ import annotations
import curses


class App:
    """The User Interface"""

    def __init__(self: App):
        pass

    def __enter__(self: App):
        # Monitor setup, take a snapshot of the terminal state
        self.screen = curses.initscr()  # Initialize standard out
        self.screen.scrollok(True)      # Enable window scroll
        self.screen.keypad(True)        # Enable special key input
        self.screen.nodelay(True)       # Disable user-input blocking
        curses.curs_set(False)          # Disable the cursor
        return self

    def __exit__(self: App, type, value, traceback) -> None:
        # Monitor destruction, restore terminal state
        curses.nocbreak()       # Re-enable line-buffering
        curses.echo()           # Enable user-input echo
        curses.curs_set(True)   # Enable the cursor
        curses.resetty()        # Restore the terminal state
        curses.endwin()         # Destroy the virtual screen

    def write(self: App, msg: str, x: int = 0, y: int = 0) -> None:
        self.screen.addstr(y, x, msg)

    def clear_line(self: App, y: int):
        self.screen.addstr(y, 0, "")
        self.screen.clrtoeol()

    def refresh(self: App):
        self.screen.refresh()

    def __str__(self: App) -> str:
        return "App<>"
