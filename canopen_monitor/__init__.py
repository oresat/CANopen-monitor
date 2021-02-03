import os
from .app import App
from .can import MagicCANBus, Interface, Message, MessageState, MessageType

MAJOR = 3
MINOR = 2
PATCH = 0

APP_NAME = 'canopen-monitor'
APP_DESCRIPTION = 'An NCurses-based TUI application for tracking activity' \
                  ' over the CAN bus and decoding messages with provided' \
                  ' EDS/OD files.'
APP_VERSION = f'{MAJOR}.{MINOR}.{PATCH}'
APP_AUTHOR = 'Dmitri McGuckin'
APP_EMAIL = 'dmitri3@pdx.edu'
APP_URL = 'https://github.com/oresat/CANopen-monitor'
APP_LICENSE = 'GPL-3.0'

CONFIG_DIR = os.path.expanduser(f'~/.config/{APP_NAME}')
CACHE_DIR = os.path.expanduser(f'~/.cache/{APP_NAME}')
ASSETS_DIR = os.path.abspath(f'{__path__[0]}/assets')
EDS_DIR = f'{ASSETS_DIR}/eds/'

TIMEOUT = 0.1
CONFIG_FORMAT_VERSION = 2

__all__ = [
    "App",
    "MagicCANBus",
    "Interface",
    "Message",
    "MessageState",
    "MessageType"
]
