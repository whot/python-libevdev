#!/usr/bin/env python3

import sys
import libevdev
from libevdev import InputEvent


def main(args):
    dev = libevdev.Device()
    dev.name = "test device"
    dev.enable(libevdev.EV_REL.REL_X)
    dev.enable(libevdev.EV_REL.REL_Y)
    try:
        dev.create()
        print("New device at {} ({})".format(dev.devnode, dev.syspath))

        events = [InputEvent(libevdev.EV_REL.REL_X, -1),
                  InputEvent(libevdev.EV_REL.REL_Y, 1),
                  InputEvent(libevdev.EV_SYN.SYN_REPORT, 0)]
        dev.send_events(events)
    except OSError as e:
        print(e)


if __name__ == "__main__":
    main(sys.argv)
