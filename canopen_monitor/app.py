from __future__ import annotations
import curses
import datetime as dt
from easygui import fileopenbox
from shutil import copy
from enum import Enum
from . import APP_NAME, APP_VERSION, APP_LICENSE, APP_AUTHOR, APP_DESCRIPTION, \
    APP_URL, CACHE_DIR
from .can import MessageTable, MessageType
from .ui import MessagePane, PopupWindow
from .parse import eds

# Key Constants not defined in curses
# _UBUNTU key constants work in Ubuntu
KEY_S_UP = 337
KEY_S_DOWN = 336
KEY_C_UP = 567
KEY_C_UP_UBUNTU = 566
KEY_C_DOWN = 526
KEY_C_DOWN_UBUNTU = 525

# Additional User Interface Related Constants
VERTICAL_SCROLL_RATE = 16
HORIZONTAL_SCROLL_RATE = 4


def pad_hex(value: int, pad: int = 3) -> str:
    """
    Convert integer value to a hex string with padding

    :param value: number of spaces to pad hex value
    :type value: int

    :param pad: the ammount of padding to add
    :type pad: int

    :return: padded string
    :rtype: str
    """
    return f'0x{hex(value).upper()[2:].rjust(pad, "0")}'


class KeyMap(Enum):
    """
    Enumerator of valid keyboard input
    value[0]: input name
    value[1]: input description
    value[2]: curses input value key
    """

    F1 = {'name': 'F1', 'description': 'Toggle app info menu',
          'key': curses.KEY_F1}
    F2 = {'name': 'F2', 'description': 'Toggle this menu', 'key': curses.KEY_F2}
    F3 = {'name': 'F3', 'description': 'Toggle eds file select',
          'key': curses.KEY_F3}
    UP_ARR = {'name': 'Up Arrow', 'description': 'Scroll pane up 1 row',
              'key': curses.KEY_UP}
    DOWN_ARR = {'name': 'Down Arrow', 'description': 'Scroll pane down 1 row',
                'key': curses.KEY_DOWN}
    LEFT_ARR = {'name': 'Left Arrow', 'description': 'Scroll pane left 4 cols',
                'key': curses.KEY_LEFT}
    RIGHT_ARR = {'name': 'Right Arrow',
                 'description': 'Scroll pane right 4 cols',
                 'key': curses.KEY_RIGHT}
    S_UP_ARR = {'name': 'Shift + Up Arrow',
                'description': 'Scroll pane up 16 rows', 'key': KEY_S_UP}
    S_DOWN_ARR = {'name': 'Shift + Down Arrow',
                  'description': 'Scroll pane down 16 rows', 'key': KEY_S_DOWN}
    C_UP_ARR = {'name': 'Ctrl + Up Arrow',
                'description': 'Move pane selection up',
                'key': [KEY_C_UP, KEY_C_UP_UBUNTU]}
    C_DOWN_ARR = {'name': 'Ctrl + Down Arrow',
                  'description': 'Move pane selection down',
                  'key': [KEY_C_DOWN, KEY_C_DOWN_UBUNTU]}
    RESIZE = {'name': 'Resize Terminal',
              'description': 'Reset the dimensions of the app',
              'key': curses.KEY_RESIZE}


class App:
    """
    The User Interface Container
    :param table: The table of CAN messages
    :type table: MessageTable

    :param selected_pane_pos: index of currently selected pane
    :type selected_pane_pos: int

    :param selected_pane: A reference to the currently selected Pane
    :type selected_pane: MessagePane
    """

    def __init__(self: App, message_table: MessageTable, eds_configs: dict):
        """
        App Initialization function
        :param message_table: Reference to shared message table object
        :type MessageTable
        """
        self.table = message_table
        self.eds_configs = eds_configs
        self.selected_pane_pos = 0
        self.selected_pane = None
        self.key_dict = {
            KeyMap.UP_ARR.value['key']: self.up,
            KeyMap.S_UP_ARR.value['key']: self.shift_up,
            KeyMap.C_UP_ARR.value['key'][0]: self.ctrl_up,
            KeyMap.C_UP_ARR.value['key'][1]: self.ctrl_up,  # Ubuntu key
            KeyMap.DOWN_ARR.value['key']: self.down,
            KeyMap.S_DOWN_ARR.value['key']: self.shift_down,
            KeyMap.C_DOWN_ARR.value['key'][0]: self.ctrl_down,
            KeyMap.C_DOWN_ARR.value['key'][1]: self.ctrl_down,  # Ubuntu key
            KeyMap.LEFT_ARR.value['key']: self.left,
            KeyMap.RIGHT_ARR.value['key']: self.right,
            KeyMap.RESIZE.value['key']: self.resize,
            KeyMap.F1.value['key']: self.f1,
            KeyMap.F2.value['key']: self.f2,
            KeyMap.F3.value['key']: self.f3
        }

    def __enter__(self: App) -> App:
        """
        Enter the runtime context related to this object
        Create the user interface layout. Any changes to the layout should
        be done here.
        :return: self
        :type App
        """
        # Monitor setup, take a snapshot of the terminal state
        self.screen = curses.initscr()  # Initialize standard out
        self.screen.scrollok(True)  # Enable window scroll
        self.screen.keypad(True)  # Enable special key input
        self.screen.nodelay(True)  # Disable user-input blocking
        curses.curs_set(False)  # Disable the cursor
        self.__init_color_pairs()  # Enable colors and create pairs

        # Don't initialize any grids, sub-panes, or windows until standard io
        #   screen has been initialized
        height, width = self.screen.getmaxyx()
        height -= 1
        self.info_win = PopupWindow(self.screen,
                                    header=f'{APP_NAME.title()}'
                                           f' v{APP_VERSION}',
                                    content=[f'author: {APP_AUTHOR}',
                                             f'license: {APP_LICENSE}',
                                             f'respository: {APP_URL}',
                                             '',
                                             'Description:',
                                             f'{APP_DESCRIPTION}'],
                                    footer='F1: exit window',
                                    style=curses.color_pair(1))
        self.hotkeys_win = PopupWindow(self.screen,
                                       header='Hotkeys',
                                       content=list(
                                           map(lambda x:
                                               f'{x.value["name"]}: {x.value["description"]}'
                                               f' ({x.value["key"]})',
                                               list(KeyMap))),
                                       footer='F2: exit window',
                                       style=curses.color_pair(1))
        self.hb_pane = MessagePane(cols={'Node ID': ('node_name', 0, hex),
                                         'State': ('state', 0),
                                         'Status': ('message', 0)},
                                   types=[MessageType.HEARTBEAT],
                                   parent=self.screen,
                                   height=int(height / 2) - 1,
                                   width=width,
                                   y=1,
                                   x=0,
                                   name='Heartbeats',
                                   message_table=self.table)
        self.misc_pane = MessagePane(cols={'COB ID': ('arb_id', 0, pad_hex),
                                           'Node Name': ('node_name', 0, hex),
                                           'Type': ('type', 0),
                                           'Message': ('message', 0)},
                                     types=[MessageType.NMT,
                                            MessageType.SYNC,
                                            MessageType.TIME,
                                            MessageType.EMER,
                                            MessageType.SDO,
                                            MessageType.PDO],
                                     parent=self.screen,
                                     height=int(height / 2),
                                     width=width,
                                     y=int(height / 2),
                                     x=0,
                                     name='Miscellaneous',
                                     message_table=self.table)
        self.__select_pane(self.hb_pane, 0)
        return self

    def __exit__(self: App, type, value, traceback) -> None:
        """
        Exit the runtime context related to this object.
        Cleanup any curses settings to allow the terminal
        to return to normal
        :param type: exception type or None
        :param value: exception value or None
        :param traceback: exception traceback or None
        :return: None
        """
        # Monitor destruction, restore terminal state
        curses.nocbreak()  # Re-enable line-buffering
        curses.noecho()  # Enable user-input echo
        curses.curs_set(True)  # Enable the cursor
        curses.resetty()  # Restore the terminal state
        curses.endwin()  # Destroy the virtual screen

    def up(self):
        """
        Up arrow key scrolls pane up 1 row
        :return: None
        """
        self.selected_pane.scroll_up()

    def shift_up(self):
        """
        Shift + Up arrow key scrolls pane up 16 rows
        :return: None
        """
        self.selected_pane.scroll_up(rate=VERTICAL_SCROLL_RATE)

    def ctrl_up(self):
        """
        Ctrl + Up arrow key moves pane selection up
        :return: None
        """
        self.__select_pane(self.hb_pane, 0)

    def down(self):
        """
        Down arrow key scrolls pane down 1 row
        :return: None
        """
        self.selected_pane.scroll_down()

    def shift_down(self):
        """
        Shift + Down arrow key scrolls down pane 16 rows
        :return:
        """
        self.selected_pane.scroll_down(rate=VERTICAL_SCROLL_RATE)

    def ctrl_down(self):
        """
        Ctrl + Down arrow key moves pane selection down
        :return: None
        """
        self.__select_pane(self.misc_pane, 1)

    def left(self):
        """
        Left arrow key scrolls pane left 4 cols
        :return: None
        """
        self.selected_pane.scroll_left(rate=HORIZONTAL_SCROLL_RATE)

    def right(self):
        """
        Right arrow key scrolls pane right 4 cols
        :return: None
        """
        self.selected_pane.scroll_right(rate=HORIZONTAL_SCROLL_RATE)

    def resize(self):
        """
        Resets the dimensions of the app
        :return: None
        """
        self.hb_pane._reset_scroll_positions()
        self.misc_pane._reset_scroll_positions()
        self.screen.clear()

    def f1(self):
        """
        Toggle app info menu
        :return: None
        """
        if self.hotkeys_win.enabled:
            self.hotkeys_win.toggle()
            self.hotkeys_win.clear()
        self.info_win.toggle()

    def f2(self):
        """
        Toggles KeyMap
        :return: None
        """
        if self.info_win.enabled:
            self.info_win.toggle()
            self.info_win.clear()
        self.hotkeys_win.toggle()

    def f3(self):
        """
        Toggles Add File window
        :return: None
        """
        filepath = fileopenbox(title='Select Object Dictionary Files',
                               filetypes=[['*.dcf', '*.eds', '*.xdd',
                                           'Object Dictionary Files']],
                               multiple=False,
                               default='~/.cache/canopen-monitor/')

        if (filepath is not None):
            file = eds.load_eds_file(filepath)
            copy(filepath, CACHE_DIR)
            self.eds_configs[file.node_id] = file


    def _handle_keyboard_input(self: App) -> None:
        """
        Retrieves keyboard input and calls the associated key function
        """
        keyboard_input = self.screen.getch()
        curses.flushinp()

        try:
            self.key_dict[keyboard_input]()
        except KeyError:
            ...

    def __init_color_pairs(self: App) -> None:
        """
        Initialize color options used by curses
        :return: None
        """
        curses.start_color()
        # Implied: color pair 0 is standard black and white
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)

    def __select_pane(self: App, pane: MessagePane, pos: int) -> None:
        """
        Set Pane as Selected
        :param pane: Reference to selected Pane
        :param pos: Index of Selected Pane
        :return: None
        """
        # Only undo previous selection if there was any
        if (self.selected_pane is not None):
            self.selected_pane.selected = False

        # Select the new pane and change internal Pane state to indicate it
        self.selected_pane = pane
        self.selected_pane_pos = pos
        self.selected_pane.selected = True

    def __draw_header(self: App, ifaces: [tuple]) -> None:
        """
        Draw the header at the top of the interface
        :param ifaces: CAN Bus Interfaces
        :return: None
        """
        # Draw the timestamp
        date_str = f'{dt.datetime.now().ctime()},'
        self.screen.addstr(0, 0, date_str)
        pos = len(date_str) + 1

        # Draw the interfaces
        for iface in ifaces:
            color = curses.color_pair(1) if iface[1] else curses.color_pair(3)
            sl = len(iface[0])
            self.screen.addstr(0, pos, iface[0], color)
            pos += sl + 1

    def __draw__footer(self: App) -> None:
        """
        Draw the footer at the bottom of the interface
        :return: None
        """
        height, width = self.screen.getmaxyx()
        footer = '<F1>: Info, <F2>: Hotkeys, <F3>: Add OD File'
        self.screen.addstr(height - 1, 1, footer)

    def draw(self: App, ifaces: [tuple]) -> None:
        """
        Draw the entire interface
        :param ifaces: CAN Bus Interfaces
        :return: None
        """
        window_active = self.info_win.enabled or self.hotkeys_win.enabled
        self.__draw_header(ifaces)  # Draw header info

        # Draw panes
        if (not window_active):
            self.hb_pane.draw()
            self.misc_pane.draw()

        # Draw windows
        self.info_win.draw()
        self.hotkeys_win.draw()

        self.__draw__footer()

    def refresh(self: App) -> None:
        """
        Refresh entire screen
        :return: None
        """
        self.screen.refresh()
