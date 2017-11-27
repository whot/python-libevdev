#!/usr/bin/env python

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

    for t in range(libevdev.Libevdev.event_to_value("EV_MAX")):
        if not l.has_event(t):
            continue

        print("  Event type {} ({})".format(t, libevdev.Libevdev.event_to_name(t)))

        max = libevdev.Libevdev.type_max(t)
        if max is None:
            continue

        for c in range(max):
            if not l.has_event(t, c):
                continue

            type_name = libevdev.Libevdev.event_to_name(t)
            if type_name in ["EV_LED", "EV_SND", "EV_SW"]:
                v = l.event_value(t, c)
                print("    Event code {} ({}) state {}".format(c, libevdev.Libevdev.event_to_name(t, c), v))
            else:
                print("    Event code {} ({})".format(c, libevdev.Libevdev.event_to_name(t, c)))

            if type_name == "EV_ABS":
                a = l.absinfo(c)
                for k, v in a.items():
                    if v == 0:
                        continue
                    print("       {:10s} {:6d}".format(k, v))

    print("Properties:")
    for p in range(0x1f):  # PROP_MAX
        if l.has_property(p):
            print("  Property type {} ({})".format(p, libevdev.Libevdev.property_to_name(p)))


def print_events(l):
    while True:
        e = l.next_event()
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
    with open(path, "rb") as fd:
        l = libevdev.Libevdev(fd)
        print_capabilities(l)
        print("################################\n"
              "#      Waiting for events      #\n"
              "################################")

        print_events(l)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: {} /dev/input/eventX".format(sys.argv[0]))
        sys.exit(1)
    main(sys.argv)
