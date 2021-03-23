import os

MAJOR = 3
MINOR = 2
PATCH = 3

APP_NAME = 'canopen-monitor'
APP_DESCRIPTION = 'An NCurses-based TUI application for tracking activity' \
                  ' over the CAN bus and decoding messages with provided' \
                  ' EDS/OD files.'
APP_VERSION = f'{MAJOR}.{MINOR}.{PATCH}'
APP_AUTHOR = 'Dmitri McGuckin'
APP_EMAIL = 'dmitri3@pdx.edu'
APP_URL = 'https://github.com/oresat/CANopen-monitor'
APP_LICENSE = 'GPL-3.0'

MAINTAINER_NAME = 'Portland State Aerospace Society'
MAINTAINER_EMAIL = 'oresat@pdx.edu'

CONFIG_DIR = os.path.expanduser(f'~/.config/{APP_NAME}')
CACHE_DIR = os.path.expanduser(f'~/.cache/{APP_NAME}')

CONFIG_FORMAT_VERSION = 2
