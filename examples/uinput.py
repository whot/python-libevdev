#!/usr/bin/env python

from __future__ import print_function

import sys
import libevdev


def main(args):
    dev = libevdev.Libevdev()
    dev.name = "test device"
    dev.enable("EV_REL", "REL_X")
    dev.enable("EV_REL", "REL_Y")
    try:
        uinput = libevdev.UinputDevice(dev)
        print("New device at {} ({})".format(uinput.devnode, uinput.syspath))
    except OSError as e:
        print(e)

if __name__ == "__main__":
    main(sys.argv)
