#!/usr/bin/env python3

import sys
import libevdev
from libevdev import InputEvent
import time


def main(args):
    dev = libevdev.Device()
    dev.name = "test device"
    dev.enable(libevdev.EV_REL.REL_X)
    dev.enable(libevdev.EV_REL.REL_Y)
    dev.enable(libevdev.EV_KEY.BTN_LEFT)
    dev.enable(libevdev.EV_KEY.BTN_RIGHT)
    try:
        uinput = dev.create_uinput_device()
        print("New device at {} ({})".format(uinput.devnode, uinput.syspath))

        # Sleep for a bit so udev, libinput, Xorg, Wayland, ... all have had
        # a chance to see the device and initialize it. Otherwise the event
        # will be sent by the kernel but nothing is ready to listen to the
        # device yet.
        time.sleep(1)

        for _ in range(5):
            events = [InputEvent(libevdev.EV_REL.REL_X, -1),
                      InputEvent(libevdev.EV_REL.REL_Y, 1),
                      InputEvent(libevdev.EV_SYN.SYN_REPORT, 0)]
            time.sleep(0.012)
            uinput.send_events(events)
    except OSError as e:
        print(e)


if __name__ == "__main__":
    main(sys.argv)
