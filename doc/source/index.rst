.. libevdev Python wrapper documentation master file, created by
   sphinx-quickstart on Fri Feb 26 08:28:42 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

libevdev Python wrapper
=======================

This package is a wrapper around the libevdev C library, with a pythonic
API. For the precise behavior of libevdev refer to the offical documentation at
http://www.freedesktop.org/software/libevdev/doc/latest/

Below are examples that cover the most common cases that need to be done
with libevdev. More specific examples can be found in the ``examples/``
directory in http://github.com/whot/libevdev-python

To read events from an existing device::

        import libevdev

        fd = open('/dev/input/event0', 'rb')
        d = libevdev.Device(fd)
        if not d.has_event(libevdev.EV_KEY.BTN_LEFT):
             print('This does not look like a mouse device')
             sys.exit(0)

        # Loop indefinitely while pulling the next few events off
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
        d.create()

        print('new uinput test device at {}'.format(d.devnode))

Contents:

.. toctree::
   :maxdepth: 1

   modules

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
