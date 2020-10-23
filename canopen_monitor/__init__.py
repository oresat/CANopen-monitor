import os

MAJOR = 3
MINOR = 1
PATCH = 4

APP_NAME = 'canopen-monitor'
APP_DESCRIPTION \
    = 'A utility for displaying and tracking activity over the CAN bus.'
APP_VERSION = "{}.{}.{}".format(MAJOR, MINOR, PATCH)
APP_AUTHOR = "Dmitri McGuckin"
APP_EMAIL = 'dmitri3@pdx.edu'
APP_URL = "https://github.com/oresat/CANopen-monitor"
APP_LICENSE = 'GPL-3.0'

CONFIG_DIR = os.path.expanduser('~/.config/{}'.format(APP_NAME)) + os.sep
CACHE_DIR = os.path.expanduser('~/.cache/{}'.format(APP_NAME)) + os.sep
ASSETS_DIR \
    = os.path.abspath(__path__[0] + os.sep + 'assets') + os.sep
EDS_DIR = ASSETS_DIR
DEVICES_CONFIG = CONFIG_DIR + 'devices.json'
LAYOUT_CONFIG = CONFIG_DIR + 'layout.json'
NODES_CONFIG = CONFIG_DIR + 'nodes.json'

DEBUG = False
TIMEOUT = 0.1
