#!/usr/bin/env python3

from __future__ import print_function

import sys
import libevdev


def print_capabilities(l):
    v = l.driver_version
    print("Input driver version is {}.{}.{}".format(v >> 16, (v >> 8) & 0xff, v & 0xff))
    id = l.id
    print("Input device ID: bus {:#x} vendor {:#x} product {:#x} version {:#x}".format(
        id["bustype"],
        id["vendor"],
        id["product"],
        id["version"],
    ))
    print("Input device name: {}".format(l.name))
    print("Supported events:")

    for t, cs in l.codes.items():
        evtype = libevdev.e(t)
        print("  Event type {} ({})".format(evtype.value, evtype.name))


        for c in cs:
            evcode = libevdev.e(evtype, c)

            if evtype in [libevdev.EV_BIT.EV_LED, libevdev.EV_BIT.EV_SND, libevdev.EV_BIT.EV_SW]:
                v = l.event_value(t, c)
                print("    Event code {} ({}) state {}".format(evcode.value, evcode.name, v))
            else:
                print("    Event code {} ({})".format(evcode.value, evcode.name))

            if evtype == libevdev.EV_BIT.EV_ABS:
                a = l.absinfo(evcode)
                print("       {:10s} {:6d}".format('Value', a.value))
                print("       {:10s} {:6d}".format('Minimum', a.minimum))
                print("       {:10s} {:6d}".format('Maximum', a.maximum))
                print("       {:10s} {:6d}".format('Fuzz', a.fuzz))
                print("       {:10s} {:6d}".format('Flat', a.flat))
                print("       {:10s} {:6d}".format('Resolution', a.resolution))

    print("Properties:")
    for p in range(libevdev.INPUT_PROP.INPUT_PROP_MAX):
        if l.has_property(p):
            p = libevdev.p(p)
            print("  Property type {} ({})".format(p.value, p.name))


def print_event(e):
        print("Event: time {}.{:06d}, ".format(e.sec, e.usec), end='')
        if e.matches("EV_SYN"):
            if e.matches("EV_SYN", "SYN_MT_REPORT"):
                print("++++++++++++++ {} ++++++++++++".format(e.code_name))
            elif e.matches("EV_SYN", "SYN_DROPPED"):
                print(">>>>>>>>>>>>>> {} >>>>>>>>>>>>".format(e.code_name))
            else:
                print("-------------- {} ------------".format(e.code_name))
        else:
            print("type {} ({}) code {} ({}), value {}".format(e.type, e.type_name, e.code, e.code_name, e.value))


def main(args):
    path = args[1]
    try:
        with open(path, "rb") as fd:
            l = libevdev.Device(fd)
            print_capabilities(l)
            print("################################\n"
                  "#      Waiting for events      #\n"
                  "################################")

            while True:
                try:
                    for e in l.events():
                        print_event(e)
                except libevdev.EventsDroppedException:
                    for e in l.sync():
                        print_event(e)

    except IOError as e:
        import errno
        if e.errno == errno.EACCES:
            print("Insufficient permissions to access {}".format(path))
        elif e.errno == errno.ENOENT:
            print("Device {} does not exist".format(path))
        else:
            raise e

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: {} /dev/input/eventX".format(sys.argv[0]))
        sys.exit(1)
    main(sys.argv)
