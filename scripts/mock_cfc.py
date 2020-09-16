#!/usr/bin/env python3
import sys
import can
import time
import canopen
import logging
import argparse
sys.path.insert(0, '..')
import canopen_monitor as cm


def main():
    # Deal with argument parsing
    parser = argparse.ArgumentParser(prog='mock-cfc')
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

    bus = can.interface.Bus(bustype='virtual', channel='vcan0')
    bus.connect(bustype='virtual', channel='vcan0')

    # # Setup the bus connection and mock oresat live
    # can_bus = canopen.Network()
    # oresat_live = canopen.RemoteNode(0x21, cm.EDS_DIR + 'live_OD.eds')
    # can_bus.add_node(oresat_live)
    #
    # try:
    #     # Connect to the bus then assert its connectivity
    #     can_bus.connect(bustype='socketcan',
    #                     channel=args.channel,
    #                     bitrate=args.bitrate)
    #     can_bus.check()
    #
    #     oresat_live.nmt.status = 'OPERATIONAL'
    #
    #     print("HB Rate: {}".format(oresat_live.sdo[0x1017].raw))
    #
    #
    #     # Spin
    #     while True:
    #         time.sleep(1)
    # except KeyboardInterrupt:
    #     print('Got signal to stop!')
    # finally:
    #     if(can_bus):
    #         can_bus.disconnect()


if __name__ == '__main__':
    main()
