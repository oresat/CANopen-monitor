import canopen_monitor as cm


def main():
    try:
        mt = cm.MessageTable()

        # Start the can bus and the curses app
        with cm.MagicCANBus(['vcan0']) as bus, \
             cm.App() as app:
            while True:
                # Mock bus updates
                for message in bus:
                    if message is not None:
                        mt += message

                # Mock draw update
                app.clear_line(0)
                app.write(str(bus))
                app.write(f'Stored Messages: {len(mt)}', x=2, y=2)

                for i, message in enumerate(mt):
                    pos = 3 + (5 * i)
                    app.write(f'{hex(message.arb_id)}: {message.data}',
                              x=2,
                              y=pos)
                    # pos += 1
                    # app.write(f'Age: {message.age}', x=4, y=pos)
                    pos += 1
                    app.clear_line(pos)
                    app.write(f'State: {message.state.name}', x=4, y=pos)
                    pos += 1
                    app.write(f'Type: {message.type}', x=4, y=pos)
                    pos += 1
                    app.write(f'Interface: {message.interface}', x=4, y=pos)
                app.refresh()

    except KeyboardInterrupt:
        print('Goodbye!')
