#!/usr/bin/env python3
import argparse
import datetime
import time
import psutil


def main():
    parser = argparse.ArgumentParser(prog='interface-status',
                                     description='Simple script to display'
                                                 ' current status of a'
                                                 ' device interface',
                                     allow_abbrev=False)
    parser.add_argument('-i', '--interface',
                        dest='interface',
                        type=str,
                        nargs='?',
                        default='vcan0',
                        help='The interface whose status is to be displayed.')

    parser.add_argument('-d', '--delay',
                        type=int,
                        default=1,
                        help='Adjust the status update delay time')

    args = parser.parse_args()

    while True:
        interface = psutil.net_if_stats().get(args.interface)
        exists = "EXISTS" if interface is not None else "DOES NOT EXIST"
        status = "IS UP" if (interface is not None and interface.isup) else "IS NOT UP"
        print("Interface " + args.interface + " " + exists + " and " + status + " | " + str(datetime.datetime.now()))
        time.sleep(args.delay)


if __name__ == '__main__':
    main()
