import os
import canopen_monitor as cm


def load_eds_files(filepath: str =
                   os.path.expanduser('~/.cache/canopen-monitor')) -> dict:
    configs = {}
    for file in os.listdir(filepath):
        full_path = f'{filepath}/{file}'
        config = cm.load_eds_file(full_path)
        configs[config.node_id] = config
    return configs


def main():
    try:
        eds_configs = load_eds_files()
        mt = cm.MessageTable(cm.CANOpenParser(eds_configs))

        # Start the can bus and the curses app
        with cm.MagicCANBus(['vcan0']) as bus, \
             cm.App(mt) as app:
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
