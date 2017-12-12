#!/usr/bin/env python3

from __future__ import print_function

import sys
import libevdev


def main(args):
    dev = libevdev.Device()
    dev.name = "test device"
    dev.enable(libevdev.EV_REL.REL_X)
    dev.enable(libevdev.EV_REL.REL_Y)
    try:
        dev.create()
        print("New device at {} ({})".format(dev.devnode, dev.syspath))
    except OSError as e:
        print(e)


if __name__ == "__main__":
    main(sys.argv)
