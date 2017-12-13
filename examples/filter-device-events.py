#!/usr/bin/env python3
#
# This example shows how to 'filter' device events from a device node.
# While real filtering is not possible, we can duplicate the input device as
# a new virtual input device and replay all events of the input events on
# our virtual one.

import sys
import libevdev


def main(args):
    path = args[1]
    code_from = libevdev.evbit(args[2])
    code_to = libevdev.evbit(args[3])

    print('Remapping {} to {}'.format(code_from, code_to))

    fd = open(path, 'rb')
    d = libevdev.Device(fd)
    d.grab()

    # create a duplicate of our input device
    uidev = libevdev.Device(fd)
    uidev.enable(code_to)  # make sure the code we map to is available
    uidev.create()
    print('Device is at {}'.format(uidev.devnode))

    while True:
        for e in d.events():
            # change any event with our event code to
            # the one we want to map to, but pass all other events
            # through
            if e.code == code_from:
                e = libevdev.InputEvent(code_to, e.value)
            uidev.send_events([e])


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: {} /dev/input/eventX <from> <to>".format(sys.argv[0]))
        print("   where <from> and <to> are event codes, e.g. REL_X")
        sys.exit(1)
    main(sys.argv)
