#!/usr/bin/env python3
import sys
from bus import TheMagicCanBus
from ftf_utilities import log, Mode


def main(args):
    if(len(args) == 0):
        log(Mode.ERROR, 'No devices specified!')
        sys.exit(-1)

    bus = TheMagicCanBus(args)

    while True:
        running = bus.running()
        frame = bus.receive()
        log(Mode.INFO, "Buses: "
            + str(running)
            + "\n\tNew Frame: "
            + str(frame))


if __name__ == "__main__":
    main(sys.argv[1:])
