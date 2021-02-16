import os
from .app import App
from .can import MagicCANBus, MessageTable
from .parse import CANOpenParser, load_eds_file


def load_eds_files(filepath: str =
                   os.path.expanduser('~/.cache/canopen-monitor')) -> dict:
    configs = {}
    for file in os.listdir(filepath):
        full_path = f'{filepath}/{file}'
        config = load_eds_file(full_path)
        configs[config.node_id] = config
    return configs


def main():
    try:
        eds_configs = load_eds_files()
        mt = MessageTable(CANOpenParser(eds_configs))

        # Start the can bus and the curses app
        with MagicCANBus(['vcan0']) as bus, \
             App(mt) as app:
            while True:
                # Bus updates
                for message in bus:
                    if message is not None:
                        mt += message

                # User Input updates
                app._handle_keyboard_input()

                # Draw update
                app.draw()
    except KeyboardInterrupt:
        print('Goodbye!')


if __name__ == '__main__':
    main()
