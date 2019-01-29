libevdev Python wrapper
=======================

**python-libevdev** is a wrapper around the libevdev C library, with a
pythonic API. libevdev makes it easy to

* read and parse events from an input device
* create a virtual input device and make it send events
* duplicate an existing device and modify the event stream

See the `Basic examples`_ section below for simple code or the :doc:`examples`
page for more detailed examples.

Source code
-----------

The source code for this project is available at
https://gitlab.freedesktop.org/libevdev/python-libevdev

Installation
------------

A requirement for **python-libevdev** to work is that the libevdev C library
is installed on your system. Install through your favourite package
managers, but you almost certainly already have it installed anyway.

The recommended way of installing **python-libevdev** is to use your
distribution's package manager (``dnf``, ``yum``, ``apt``, ``pacman``, ...).
If it isn't packaged for your distribution, you should use ``pip3``::

        sudo pip3 install libevdev

For more details on using pip and the PyPI, please see https://pypi.python.org/pypi

Otherwise, you can install it from the git repository::

        git clone https://gitlab.freedesktop.org/libevdev/python-libevdev.git
        cd python-libevdev
        sudo ./setup.py install

Finally, **python-libevdev** can be used directly from the source by simply
setting ``PYTHONPATH``::

        $> export PYTHONPATH=/path/to/source:$PYTHONPATH
        $> python3 -c 'import libevdev; print(libevdev.EV_ABS)'
        EV_ABS:3

Once installed, the ``import libevdev`` statement will work and you can go
from there.

Why libevdev?
-------------

**python-libevdev** uses libevdev for most operations. This provides a
number of advantages over direct evdev event handling, libevdev hides some
of the quirks of the evdev protocol. For example libevdev provides

* access to the state of the device (rather than just the events)
* correct handling of fake multitouch devices
* synching of slots and per-slot state
* transparent generation of missing tracking ids after SYN_DROPPED
* disabling/enabling events on a per-context basis, so one can disable/enable ABS_FOO and then not care about quirks in the client-side code.
* transparent handling of the UI_GET_SYSNAME and UI_DEV_SETUP ioctls

The above are all features that were added to libevdev (the C library) over
time because of a need for it in projects like the Xorg drivers, libinput,
evemu and others.

Unfortunately, the evdev kernel API is very simple, but getting the
*behavior* of the API correct is hard. Even kernel drivers frequently do it
wrong. libevdev (the C library) does hide a lot of that and thus makes
consuming evdev safer.

For the precise behavior of the libevdev C library refer to the offical
documentation at
http://www.freedesktop.org/software/libevdev/doc/latest/

Basic examples
--------------

Below are examples that cover the most common cases that need to be done
with libevdev. More specific examples can be found on the :doc:`examples`
page.

To read events from an existing device::

        import libevdev
        import sys

        fd = open('/dev/input/event0', 'rb')
        d = libevdev.Device(fd)
        if not d.has(libevdev.EV_KEY.BTN_LEFT):
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

.. note::

   Reading from and writing to input devices requires root access to the
   device node. Any programs using libevdev need to run as root.


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

.. note::

   Creating uinput devices requires root access.
   Any programs using libevdev need to run as root.


It's common to read events or device descriptions from some file
(e.g. evemu recordings). libevdev makes it easy to convert numbers or
strings into a correct event code::

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

.. toctree::
   :caption: Table of Contents
   :maxdepth: 2

   tutorial
   API documentation <modules>
   examples
   python-evdev

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
