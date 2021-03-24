import os
import sys
import argparse
from . import APP_NAME, APP_VERSION, APP_DESCRIPTION, CONFIG_DIR, CACHE_DIR
from .app import App
from .can import MagicCANBus, MessageTable
from .parse import CANOpenParser, load_eds_file


def init_dirs():
    os.makedirs(CONFIG_DIR, exist_ok=True)
    os.makedirs(CACHE_DIR, exist_ok=True)


def load_eds_files(filepath: str = CACHE_DIR) -> dict:
    configs = {}
    for file in os.listdir(filepath):
        full_path = f'{filepath}/{file}'
        config = load_eds_file(full_path)
        configs[config.node_id] = config
    return configs


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

    if(args.version):
        print(f'{APP_NAME} v{APP_VERSION}\n\n{APP_DESCRIPTION}')
        sys.exit(0)

    try:
        if(len(args.interfaces) == 0):
            print('Warning: no interfaces config was found and you did not'
                  ' specify any interface arguments')
            print(f'\t(see {APP_NAME} -h for details)\n')
            print('This means the monitor will not be listening to anything.')
            while(True):
                answer = input('Would you like to continue anyways? [y/N]: ')
                if(answer.upper() == 'N' or answer == ''):
                    sys.exit(0)
                elif(answer.upper() == 'Y'):
                    break
                else:
                    print(f'Invalid response: {answer}')

        init_dirs()
        eds_configs = load_eds_files()
        mt = MessageTable(CANOpenParser(eds_configs))

        # Start the can bus and the curses app
        with MagicCANBus(args.interfaces, no_block=args.no_block) as bus, \
             App(mt, eds_configs) as app:
            while True:
                # Bus updates
                for message in bus:
                    if message is not None:
                        mt += message

                # User Input updates
                app._handle_keyboard_input()

                # Draw update
                app.draw(bus.statuses)
    except KeyboardInterrupt:
        print('Goodbye!')


if __name__ == '__main__':
    main()
