#!/usr/bin/python3

import libevdev
import sys


def toggle(path, ledstr):
    ledmap = {
        'numlock': (libevdev.EV_LED.LED_NUML, libevdev.EV_KEY.KEY_NUMLOCK),
        'capslock': (libevdev.EV_LED.LED_CAPSL, libevdev.EV_KEY.KEY_CAPSLOCK),
        'scrolllock': (libevdev.EV_LED.LED_SCROLLL, libevdev.EV_KEY.KEY_SCROLLLOCK),
    }

    if ledstr not in ledmap:
        print('Unknown LED: "{}". Use one of "{}".'.format(ledstr, '", "'.join(ledmap.keys())))
        sys.exit(1)

    led, key = ledmap[ledstr]

    with open(path, 'r+b', buffering=0) as fd:
        d = libevdev.Device(fd)
        if not d.has(led):
            print('Device does not have a {} LED'.format(ledstr))
            sys.exit(0)

        if not d.has(key):
            print('Device does not have a {} key'.format(ledstr))
            sys.exit(0)

        state = d.value[key]
        print('{} {}'.format(ledstr, 'on' if state else 'off'))

        while True:
            for e in d.events():
                if not e.matches(key):
                    continue

                if not e.value:
                    continue

                state = not state
                d.set_leds([(led, state)])
                print('{} {}'.format(ledstr, 'on' if state else 'off'))


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: {} /dev/input/eventX {{numlock|capslock|scrolllock}}".format(sys.argv[0]))
        sys.exit(1)

    path = sys.argv[1]
    ledstr = sys.argv[2]

    try:
        toggle(path, ledstr)
    except KeyboardInterrupt:
        pass
    except IOError as e:
        import errno
        if e.errno == errno.EACCES:
            print("Insufficient permissions to access {}".format(path))
        elif e.errno == errno.ENOENT:
            print("Device {} does not exist".format(path))
        else:
            raise e
