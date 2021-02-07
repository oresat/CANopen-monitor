#!/usr/bin/env python3
import can
import time
import random
import argparse
import subprocess

_FAILURE_STRING = 'Device "{}" does not exist.'
_BUS_TYPE = 'socketcan'


def create_vdev(name: str) -> bool:
    rc_create = subprocess.call(['sudo', 'ip', 'link', 'add',
                                 'dev', name, 'type', 'vcan'])
    created = rc_create == 0 or rc_create == 2

    if(created):
        rc_netup = subprocess.call(['sudo', 'ip', 'link', 'set', name, 'up'])
        netup = rc_netup == 0 or rc_netup == 2
    else:
        netup = False

    return created and netup


def destroy_vdev(name: str) -> bool:
    rc_destroy = subprocess.call(['sudo', 'ip', 'link', 'del', 'dev', name])
    destroyed = rc_destroy == 0 or rc_destroy == 1
    return destroyed


def send(channel: str, id: int, message: [int]):
    """:param id: Spam the bus with messages including the data id."""
    bus = can.interface.Bus(channel=channel, bustype=_BUS_TYPE)
    msg = can.Message(arbitration_id=id,
                      data=message,
                      is_extended_id=False)
    bus.send(msg)


def main():
    parser = argparse.ArgumentParser(prog='socketcan-dev',
                                     description='A simple SocketCan wrapper'
                                                 ' for testing'
                                                 ' canopen-monitor',
                                     allow_abbrev=False)
    parser.add_argument('-c', '--channels',
                        type=str,
                        nargs="+",
                        default=['vcan0'],
                        help='The channel to create and send CAN messages on')
    parser.add_argument('-d', '--delay',
                        type=float,
                        default=1,
                        help='Adjust the message-send delay time, used in'
                             ' conjunction with `-r`')
    parser.add_argument('-i', '--id',
                        type=str,
                        default='10',
                        help='The COB ID to use for the messages')
    parser.add_argument('-n', '--no-destroy',
                        dest='destroy',
                        action='store_false',
                        default=True,
                        help='Stop socketcan-dev from destroying the channel'
                             ' at the end of life')
    parser.add_argument('-m', '--message',
                        type=str,
                        nargs=8,
                        default=['0', '0', '0', '1', '3', '1', '4', '1'],
                        help='The 7 bytes to send as the CAN message')
    parser.add_argument('-r', '--repeat',
                        dest='repeat',
                        action='store_true',
                        default=False,
                        help='Repeat sending the message indefinitely, every'
                             ' given seconds, used in conjunction with `-d`')
    parser.add_argument('--random-id',
                        dest='random_id',
                        action='store_true',
                        default=False,
                        help='Use a randomly generated ID (this disables -i)')
    args = parser.parse_args()

    # Interpret ID as hex
    if(args.random_id):
        args.id = random.randint(0x0, 0x7ff)
    else:
        args.id = int(args.id, 16)

    # Interpret message as hex
    args.message = list(map(lambda x: int(x, 16), args.message))

    try:
        up = []
        # Create the channels
        for c in args.channels:
            up.append(create_vdev(c))

        while(args.repeat):
            if(args.random_id):
                args.id = random.randint(0x0, 0x7ff)

            for i, c in enumerate(args.channels):
                if(up[i]):
                    id = args.id + i
                    send(c, id, args.message)
                    print(f'[{time.time()}]:'.ljust(22, ' ')
                          + f'Sent {args.message} to {c} as'
                          f' {hex(id)}')
                    time.sleep(args.delay)
    except KeyboardInterrupt:
        print('Goodbye!')
    finally:
        if(args.destroy):
            for channel in args.channels:
                destroy_vdev(channel)


if __name__ == '__main__':
    main()
