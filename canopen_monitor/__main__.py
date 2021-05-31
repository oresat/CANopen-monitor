import os
import sys
import argparse
from . import APP_NAME, APP_VERSION, APP_DESCRIPTION, CONFIG_DIR, CACHE_DIR
from .app import App
from .meta import Meta
from .can import MagicCANBus, MessageTable
from .parse import CANOpenParser, load_eds_file, EDS, DataType


def init_dirs():
    os.makedirs(CONFIG_DIR, exist_ok=True)
    os.makedirs(CACHE_DIR, exist_ok=True)


def load_eds_files(filepath: str = CACHE_DIR) -> dict:
    configs = {}
    for file in os.listdir(filepath):
        full_path = f'{filepath}/{file}'
        if file.lower().endswith(".eds") or file.lower().endswith(".dcf"):
            config = load_eds_file(full_path)
            configs[config.node_id] = config
    return configs


def enable_ecss_time(configs: dict) -> None:
    for od in configs:
        if '0x2101' in od:
            od['0x2101'].data_type = DataType.ECSS_TIME.value


def main():
    parser = argparse.ArgumentParser(prog=APP_NAME,
                                     description=APP_DESCRIPTION,
                                     allow_abbrev=False)
    parser.add_argument('-i', '--interface',
                        dest='interfaces',
                        type=str,
                        nargs='+',
                        default=[],
                        help='A list of interfaces to bind to.')
    parser.add_argument('--no-block',
                        dest='no_block',
                        action='store_true',
                        default=False,
                        help='Disable block-waiting for the Magic CAN Bus.'
                             ' (Warning, this may produce undefined'
                             ' behavior).')
    parser.add_argument('-v', '--version',
                        dest='version',
                        action='store_true',
                        default=False,
                        help='Display the app version then exit.')
    args = parser.parse_args()

    if (args.version):
        print(f'{APP_NAME} v{APP_VERSION}\n\n{APP_DESCRIPTION}')
        sys.exit(0)

    try:
        init_dirs()
        meta = Meta(CONFIG_DIR, CACHE_DIR)
        features = meta.load_features()
        eds_configs = load_eds_files()
        if features.ecss_time:
            enable_ecss_time(eds_configs)
        mt = MessageTable(CANOpenParser(eds_configs))
        interfaces = meta.load_interfaces(args.interfaces)

        # Start the can bus and the curses app
        with MagicCANBus(interfaces, no_block=args.no_block) as bus, \
                App(mt, eds_configs, bus, meta) as app:
            while True:
                # Bus updates
                for message in bus:
                    if message is not None:
                        mt += message

                # User Input updates
                app.handle_keyboard_input()

                # Draw update
                app.draw(bus.statuses)
    except KeyboardInterrupt:
        print('Goodbye!')


if __name__ == '__main__':
    main()
