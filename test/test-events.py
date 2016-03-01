import sys

from libevdev import *

def main(argv):
    device = argv[1]
    with open(device, "rb") as fd:
        print("Opened {} in blocking mode, waiting for an event.".format(device))
        l = Libevdev(fd)
        while True:
            ev = l.next_event()
            if ev.matches("EV_SYN", "SYN_REPORT"):
                break

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print("Usage: {} /dev/input/eventX".format(sys.argv[0]))
        sys.exit(1)
    main(sys.argv)
    


