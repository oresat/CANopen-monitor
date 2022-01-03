from __future__ import annotations
from .parse import CANOpenParser
from os.path import exists
import datetime as dt
from .can import MessageTable, \
                 MessageType, \
                 MagicCANBus
from .meta import Meta, FeatureConfig
from oresat_tpane.datagrid import DataGrid
from oresat_tpane.pane import Pane, VSplit, HSplit, TextFill
from urwid import MainLoop

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


def handle_undefined_input(key:chr):
    log_path = 'error.log'

    if(not exists(log_path)):
        with open(log_path, 'w+') as file:
            file.write(f'----CANOpen-Monitor [{ dt.datetime.now().ctime()}]----\n')

    with open(log_path, 'a') as file:
        file.write(f'Unhandled io: {key}\n')

def pad_hex(value: int, pad: int = 3) -> str:
    '''
    Convert integer value to a hex string with padding

    :param value: number of spaces to pad hex value
    :type value: int

    :param pad: the ammount of padding to add
    :type pad: int

    :return: padded string
    :rtype: str
    '''
    return '0x' + hex(value).upper()[2:].rjust(pad, '0')


def trunc_timedelta(value: dt.timedelta, pad: int = 0):
    TIME_UNITS = {'d': 86400, 'h': 3600, 'm': 60, 's': 1, 'ms': 0.1}
    time_str = ''
    seconds = value.total_seconds()

    for name, unit_len in TIME_UNITS.items():
        if(name == 'ms' and time_str != ''):
            continue
        res = int(seconds // unit_len)
        seconds -= (res * unit_len)

        if(res > 0):
            time_str += f'{res}{name}'

    return time_str


class App:
    '''
    The User Interface Container
    :param table: The table of CAN messages
    :type table: MessageTable

    :param selected_pane_pos: index of currently selected pane
    :type selected_pane_pos: int

    :param selected_pane: A reference to the currently selected Pane
    :type selected_pane: MessagePane
    '''

    def __init__(self: App,
                 eds_configs: dict,
                 bus: MagicCANBus,
                 meta: Meta,
                 features: FeatureConfig,
                 input_timeout: int = 1):
        '''
        App Initialization function
        :param message_table: Reference to shared message table object
        :type MessageTable
        :param features: Application feature settings
        :type features: FeatureConfig
        '''
        self.__eds_configs = eds_configs
        self.__message_parser = CANOpenParser(self.__eds_configs)
        MessageTable.PARSER = self.__message_parser
        self.bus = bus
        self.input_timeout = input_timeout

        # Heartbeat Data Grid setup
        self.__hb_table = MessageTable(('node_id', 'age', 'state'))
        self.__hb_ui_table = DataGrid([],
                                      self.__hb_table.headers,
                                      (True, False, False, False))

        # Misc Data Grid setup
        self.__misc_table = MessageTable(('arb_id', 'node_id', 'age', 'message'))
        self.__misc_ui_table = DataGrid([],
                                        self.__misc_table.headers,
                                        (True, False, False, False))

        # Monitor setup
        self.__hb_pane = Pane(self.__hb_ui_table, True, 'Heartbeats')
        self.__info_pane = Pane(TextFill('info', 'top'), True, 'Bus Statistics')
        self.__misc_pane = Pane(self.__misc_ui_table, True, 'Miscellaneous Messages')

        # Create the layout
        top_ui = VSplit([self.__hb_pane, self.__info_pane])
        parent_ui = HSplit([top_ui, self.__misc_pane])
        self.__palette = [('text', 'black', 'light green')]

        self.window = Pane(parent_ui,
                           border=False,
                           title=f'{dt.datetime.now().ctime()}',
                           title_attr='text',
                           footer='<F1: Info> <F2: Hotkeys>')

        self.__event_loop = MainLoop(self.window,
                                     self.__palette,
                                     unhandled_input=handle_undefined_input)

        # Establish asynchroous watchdog events
        self.__event_loop.set_alarm_in(self.input_timeout, self.__update_headers)
        self.__event_loop.set_alarm_in(self.input_timeout, self.__mcb_handler)

    def __mcb_handler(self: App, event_loop: MainLoop, data: object = None) -> None:
        # Bus updates
        for message in self.bus:
            if message is not None:
                if(message.type == MessageType.HEARTBEAT):
                    self.__hb_table.add(message)

                    for message in self.__hb_table:
                        self.__hb_ui_table += message.to_tuple(self.__hb_table.headers)
                else:
                    self.__misc_table.add(message)

                    for message in self.__misc_table:
                        self.__misc_ui_table += message.to_tuple(self.__misc_table.headers)

        event_loop.set_alarm_in(self.input_timeout, self.__mcb_handler)

    def __update_headers(self: App, event_loop: MainLoop, data: object = None):
        self.window.set_title(f'{dt.datetime.now().ctime()}')
        self.window.set_title(dt.datetime.now().ctime())

        self.__hb_pane.set_title(f'Heartbeats ({len(self.__hb_table)} messages, {len(self.__hb_table.undrawn_messages)} undrawn)')
        self.__misc_pane.set_title(f'Heartbeats ({len(self.__misc_table)} messages, {len(self.__misc_table.undrawn_messages)} undrawn)')

        event_loop.set_alarm_in(self.input_timeout, self.__update_headers)

    def run(self: App) -> None:
        self.__event_loop.run()
