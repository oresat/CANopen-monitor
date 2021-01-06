import os

MAJOR = 3
MINOR = 2
PATCH = 0

APP_NAME = 'canopen-monitor'
APP_DESCRIPTION = 'A utility for displaying and tracking activity over the' \
                  ' CAN bus.'
APP_VERSION = f'{MAJOR}.{MINOR}.{PATCH}'
APP_AUTHOR = 'Dmitri McGuckin'
APP_EMAIL = 'dmitri3@pdx.edu'
APP_URL = 'https://github.com/oresat/CANopen-monitor'
APP_LICENSE = 'GPL-3.0'

CONFIG_DIR = os.path.expanduser(f'~/.config/{APP_NAME}')
CACHE_DIR = os.path.expanduser(f'~/.cache/{APP_NAME}')
ASSETS_DIR = os.path.abspath(f'{__path__[0]}/assets')
EDS_DIR = f'{ASSETS_DIR}/eds/'

DEBUG = False
TIMEOUT = 0.1
CONFIG_FORMAT_VERSION = 2
