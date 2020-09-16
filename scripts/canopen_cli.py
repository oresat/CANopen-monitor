#!/usr/bin/env python3
import sys
import time
import canopen
import logging
import argparse
sys.path.insert(0, '..')
import canopen_monitor as cm


def on_message(msg):
    print('New Message: "{}"'.format(msg))


def main():
    # Deal with argument parsing
    parser = argparse.ArgumentParser(prog='canopen-cli')
    parser.add_argument('-v', '--verbose',
                        dest='debug',
                        action='store_true',
                        default=False)
    parser.add_argument('-c', '--channel',
                        dest='channel',
                        type=str,
                        default='vcan0')
    parser.add_argument('-b', '--bit-rate',
                        dest='bitrate',
                        type=int,
                        default=250000)
    args = parser.parse_args()

    # Setup logging
    if(args.debug):
        logging.basicConfig(level=logging.DEBUG)

    # Setup the bus connection
    can_bus = canopen.Network()

    try:
        # Connect to the bus then assert its connectivity
        can_bus.connect(bustype='socketcan',
                        channel=args.channel,
                        bitrate=args.bitrate)
        can_bus.check()

        # Start a periodic time sync
        can_bus.sync.start(0.1)
        can_bus.subscribe(0x721, on_message)

        print('Scrubbing network for active nodes...')
        can_bus.scanner.search()
        time.sleep(1)
        nodes = can_bus.scanner.nodes
        if(len(nodes) > 0):
            for node_id in nodes:
                print('Active Node at: {}'.format(node_id))
        else:
            print('No active nodes found on the network!')
    except KeyboardInterrupt:
        print('Got signal to stop!')
    finally:
        if(can_bus):
            can_bus.disconnect()


if __name__ == '__main__':
    main()
