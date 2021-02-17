import os
from . import CONFIG_DIR, CACHE_DIR
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
    try:
        init_dirs()
        eds_configs = load_eds_files()
        mt = MessageTable(CANOpenParser(eds_configs))

        # Start the can bus and the curses app
        with MagicCANBus(['vcan0', 'vcan1']) as bus, \
             App(mt) as app:
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
