import canopen_monitor as cm


def main():
    try:
        table = {}

        # Start the can bus and the curses app
        with cm.MagicCANBus(['vcan0', 'vcan1', 'vcan2']) as bus, \
             cm.App() as app:
            while True:
                # Mock bus updates
                for message in bus:
                    if message is not None:
                        table[message.node_id] = message

                # Mock draw update
                app.write(str(bus))
                for i, id in enumerate(table.keys()):
                    pos = 3 + (5 * i)
                    message = table[id]
                    app.write(f'{hex(id + 1)} : {message}', x=2, y=pos)
                    pos += 1
                    app.write(f'Age: {message.age}', x=4, y=pos)
                    pos += 1
                    app.write(f'State: {message.state}', x=4, y=pos)
                    pos += 1
                    app.write(f'Type: {message.type}', x=4, y=pos)
                    pos += 1
                    app.write(f'Interface: {message.interface}', x=4, y=pos)
                app.clear_line(1)
                # import time; time.sleep(1)
                app.refresh()

    except KeyboardInterrupt:
        print('Goodbye!')
