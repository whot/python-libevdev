libevdev Python wrapper
=======================

This package is a wrapper around the libevdev C library, with a pythonic
API. This provides a number of advantages over 'raw' evdev event handling,
libevdev hides some of the quirks of the evdev protocol. For the precise
behavior of the libevdev C library refer to the offical documentation at
http://www.freedesktop.org/software/libevdev/doc/latest/ For the rest of
this document, "libevdev" refers to this Python wrapper.

The source code for this project is available at
http://github.com/whot/libevdev-python

libevdev makes it easy to

* read and parse events from an input device
* create a virtual input device and make it send events
* duplicate an existing device and modify the event stream

Below are examples that cover the most common cases that need to be done
with libevdev. More specific examples can be found on the :doc:`examples`
page.

To read events from an existing device::

        import libevdev

        fd = open('/dev/input/event0', 'rb')
        d = libevdev.Device(fd)
        if not d.has_event(libevdev.EV_KEY.BTN_LEFT):
             print('This does not look like a mouse device')
             sys.exit(0)

        # Loop indefinitely while pulling the currently available events off
        # the file descriptor
        while True:
            for e in d.events():
                if not e.matches(libevdev.EV_KEY):
                    continue

                if e.matches(libevdev.EV_KEY.BTN_LEFT):
                    print('Left button event')
                elif e.matches(libevdev.EV_KEY.BTN_RIGHT):
                    print('Right button event')


To create a new uinput device with a specific set of events::

        import libevdev
        d = libevdev.Device()
        d.name = 'some test device'
        d.enable(libevdev.EV_REL.REL_X)
        d.enable(libevdev.EV_REL.REL_Y)
        d.enable(libevdev.EV_KEY.BTN_LEFT)
        d.enable(libevdev.EV_KEY.BTN_MIDDLE)
        d.enable(libevdev.EV_KEY.BTN_RIGHT)

        uinput = d.create_uinput_device()
        print('new uinput test device at {}'.format(uinput.devnode))
        events = [InputEvent(libevdev.EV_REL.REL_X, 1),
                  InputEvent(libevdev.EV_REL.REL_Y, 1),
                  InputEvent(libevdev.EV_SYN.SYN_REPORT, 0)]
        uinput.send_events(events)


To compare a textual or binary representation of events to a device::

        >>> import libevdev
        >>> print(libevdev.evbit(0))
        EV_SYN:0
        >>> print(libevdev.evbit(2))
        EV_REL:2
        >>> print(libevdev.evbit(3, 4))
        ABS_RY:4
        >>> print(libevdev.evbit('EV_ABS'))
        EV_ABS:3
        >>> print(libevdev.evbit('EV_ABS', 'ABS_X'))
        ABS_X:0
        >>> print(libevdev.evbit('ABS_X'))
        ABS_X:0

.. note::

   Reading from and writing to input devices requires root access to the
   device node. Any programs using libevdev need to run as root.

Contents:

.. toctree::
   :maxdepth: 1

   modules
   examples
   python-evdev

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
