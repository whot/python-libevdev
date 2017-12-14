#!/usr/bin/env python3
#
# This example shows how to update a kernel device's axis range
# This can be useful to e.g. change the resolution on a touchpad.
# Note that this is an example only, there are a lot of race conditions to
# be considered when using this as a proper solution.

import sys
import libevdev

def main(args):
    path = args[1]
    axis = args[2]
    field = args[3]
    value = int(args[4])

    assert field in ['minimum', 'maximum', 'resolution']
    axis = libevdev.evbit(axis)
    assert axis is not None

    fd = open(path, 'rb')
    d = libevdev.Device(fd)
    if not d.has(axis):
        print('Device does not have axis {}'.format(axis))
        sys.exit(1)

    a = d.absinfo[axis]
    setattr(a, field, value)
    d.absinfo[axis] = a
    d.sync_absinfo_to_kernel(axis)


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: {} /dev/input/eventX <axis> <field> <value>".format(sys.argv[0]))
        print("   <axis> ... an EV_ABS event code, e.g. ABS_X")
        print("   <field> .. one of 'minimum', 'maximum', 'resolution'")
        print("   <value> .. the numeric value to set the axis field to")
        sys.exit(1)
    main(sys.argv)

