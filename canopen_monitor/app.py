from __future__ import annotations
import curses
from .can import MessageTable, MessageType
from .ui import MessagePane


class App:
    """The User Interface
    """

    def __init__(self: App, message_table: MessageTable):
        self.table = message_table

    def __enter__(self: App):
        # Monitor setup, take a snapshot of the terminal state
        self.screen = curses.initscr()  # Initialize standard out
        self.screen.scrollok(True)      # Enable window scroll
        self.screen.keypad(True)        # Enable special key input
        self.screen.nodelay(True)       # Disable user-input blocking
        curses.curs_set(False)          # Disable the cursor
        self.__init_color_pairs()       # Enable colors and create pairs

        # Don't initialize any sub-panes or grids until standard io screen has
        #   been initialized
        self.misc_pane = MessagePane(cols={'COB ID': ('arb_id', 0, hex),
                                           'Node ID': ('node_name', 0, hex),
                                           'Type': ('type', 0),
                                           'Message': ('message', 0)},
                                     types=[MessageType.NMT,
                                            MessageType.SYNC,
                                            MessageType.TIME,
                                            MessageType.EMER,
                                            MessageType.SDO,
                                            MessageType.PDO],
                                     parent=self.screen,
                                     name='Miscellaneous',
                                     message_table=self.table)
        self.hb_pane = MessagePane(cols={'COB ID': ('arb_id', 0, hex),
                                         'Node ID': ('node_name', 0, hex),
                                         'State': ('state', 0)},
                                   types=[MessageType.HEARTBEAT],
                                   parent=self.screen,
                                   name='Heartbeats',
                                   message_table=self.table)
        return self

    def _handle_keyboard_input(self: App) -> None:
        """This is only a temporary implementation

        .. deprecated::

            Soon to be removed
        """
        # Grab user input
        input = self.screen.getch()
        curses.flushinp()

        if(input == curses.KEY_UP):
            self.misc_pane.scroll_up()
        elif(input == curses.KEY_DOWN):
            self.misc_pane.scroll_down()
        elif(input == 567 or input == 546):  # Ctrl+Up or Ctrl+Left
            self.misc_pane.scroll_up(rate=16)
        elif(input == 526 or input == 561):  # Ctrl+Down or Ctrl+Right
            self.misc_pane.scroll_down(rate=16)
        elif(input == curses.KEY_LEFT):
            self.misc_pane.scroll_left(rate=4)
        elif(input == curses.KEY_RIGHT):
            self.misc_pane.scroll_right(rate=4)
        elif(input == curses.KEY_RESIZE):
            self.misc_pane._reset_scroll_positions()
            self.screen.clear()
            # self.misc_pane.clear()

    def __init_color_pairs(self: App) -> None:
        curses.start_color()
        # Implied: color pair 0 is standard black and white
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)

    def __exit__(self: App, type, value, traceback) -> None:
        # Monitor destruction, restore terminal state
        curses.nocbreak()       # Re-enable line-buffering
        curses.echo()           # Enable user-input echo
        curses.curs_set(True)   # Enable the cursor
        curses.resetty()        # Restore the terminal state
        curses.endwin()         # Destroy the virtual screen

    def __draw_header(self: App) -> None:
        ...

    def draw(self: App):
        self.misc_pane.draw()

    def refresh(self: App):
        self.screen.refresh()
