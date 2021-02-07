import canopen_monitor as cm


def main():
    try:
        mt = cm.MessageTable()

        # Start the can bus and the curses app
        with cm.MagicCANBus(['vcan0']) as bus, \
             cm.App(mt) as app:
            while True:
                # Bus updates
                for message in bus:
                    if message is not None:
                        mt += message

                # Draw update
                app.draw()
    except KeyboardInterrupt:
        print('Goodbye!')
