Tutorial
========

This is a tutorial on using libevdev's Python wrapper. It is not a tutorial
on the evdev protocol, basic knowledge of how evdev works is assumed.
Specifically, you're expected to know what an event type and an event code
is. If you don't, read
`Understanding evdev
<https://who-t.blogspot.com.au/2016/09/understanding-evdev.html/>`_ first.

The basic building blocks
-------------------------

The most important building blocks are the :class:`Device <libevdev.device.Device>`,
:class:`InputEvent <libevdev.event.InputEvent>` and the :func:`evbit()
<libevdev.const.evbit>` function.  A :class:`Device
<libevdev.device.Device>` object refers to any libevdev device, whether
it's backed by a real device or not. :class:`InputEvent
<libevdev.event.InputEvent>` represents an event from that device. libevdev
relies on the caller using wrapped event code objects rather than just
strings and numbers, :func:`evbit() <libevdev.const.evbit()>` converts from
one to the other.

Event types and codes 
---------------------

In raw evdev, each event has an event type and an event code. These are just
numbers with overlapping ranges, so it's possible to mix them up. libevdev
takes this away by providing objects for both types and codes. These
objects are required in all API calls, so the chances of mixing things up
are reduced.

All event codes and types are exposed in the libevdev module namespace::

        >>> t = libevdev.EV_ABS
        >>> print(t)
        EV_ABS:3
        >>> print(t.value)
        3
        >>> print(t.name)
        EV_ABS

        >>> c = libevdev.EV_ABS.ABS_X
        >>> print(c)
        ABS_X:0
        >>> print(c.value)
        0
        >>> print(c.name)
        ABS_X

As you can see, each type or code has a ``value`` and ``name`` attribute.
Each type and code also references each other, so you can go from one to the
other easily::

        >>> c = libevdev.EV_ABS.ABS_X
        >>> print(c.type)
        EV_ABS:3
        >>> c.type == libevdev.EV_ABS
        True

        >>> t = libevdev.EV_ABS
        >>> print(t.codes[:3])
        [ABS_X:0, ABS_Y:1, ABS_Z:2]
        >>> t.codes[0] == libevdev.EV_ABS.ABS_X
        True

Converting to and from a event code
-----------------------------------

When parsing text files with device descriptions, the data is usually in the
form of numeric values or text strings for each event type or event code.
The :func:`evbit() <libevdev.const.evbit>` function is the conversion
function to get the real event types and codes from that data.
Using it is easy: just pass the numbers or strings in and use the object
that comes out::

        >>> print(libevdev.evbit(3))
        EV_ABS:3
        >>> libevdev.evbit(3) == libevdev.EV_ABS
        True

        >>> print(libevdev.evbit(3, 0))
        ABS_X:0
        >>> libevdev.evbit(3, 0) == libevdev.EV_ABS.ABS_X
        True

For the cases where the data is strings, it works much in the same way::

        >>> print(libevdev.evbit('EV_ABS'))
        EV_ABS:3
        >>> libevdev.evbit('EV_ABS') == libevdev.EV_ABS
        True

        >>> print(libevdev.evbit('EV_ABS', 'ABS_X'))
        ABS_X:0
        >>> libevdev.evbit('EV_ABS', 'ABS_X') == libevdev.EV_ABS.ABS_X
        True

        >>> print(libevdev.evbit('ABS_X'))
        ABS_X:0
        >>> libevdev.evbit('ABS_X') == libevdev.EV_ABS.ABS_X
        True

Most of the event code strings are unique, so as you can see in the third
example above, the event type isn't needed when converting from string.

Ok, now that we know how to deal with event codes and types, we can move on
to actually using those.

.. _opening_a_device:

Opening a device
----------------

Opening and closing devices is left to the caller. libevdev merely makes use
of any file objects that it is given. It also relies on the caller to figure
out when events are available on the file object - all libevdev does is use
the file descriptor when asked to do so. libevdev doesn't give you a list of
devices either - you can easily figure that out yourself by looping through
the file system or using libudev.

The simplest case (and good enough for most applications) is a mere call to
``open``, optionally followed by a call to ``fcntl`` to switch the file
descriptor into non-blocking mode::

        >>> fd = open("/dev/input/event0", "rb")
        >>> fcntl.fcntl(fd, fcntl.F_SETFL, os.O_NONBLOCK)
        >>> device = libevdev.Device(fd)
        >>> print(device.name)
        Lid Switch

This creates a device that is backed by a file descriptior - we can read
events from it later or even modify the kernel device.

That's it. libevdev doesn't really care how you opened the device, as long
as ``fileno()`` works on it it'll take it. Now we can move on to actually
handling the device.

Querying and modifying device capabilities
------------------------------------------

The :func:`has <libevdev.device.Device.has>` function returns True when a
device has a given event type or event code. So let's check whether this
device is a mouse::

        if not device.has(libevdev.EV_REL):
            print('I expected relative axes from a mouse...')
            sys.exit(0)

        if device.has(libevdev.EV_KEY.BTN_MIDDLE):
            print('Fancy, a mouse with a middle button!')
            device.disable(libevdev.EV_KEY.BTN_MIDDLE)
            print('... but you do not get to use it')

The :func:`has <libevdev.device.Device.has>` calls are self-explanatory. The
call to :func:`disable <libevdev.device.Device.disable>` disables the
given event code or event type. When disabled, no events from this code or
type are forwarded to the caller and future calls to
:func:`has <libevdev.device.Device.has>` return ``False``.

The inverse is possible too, enabling a non-existing event code::

        if not device.has(libevdev.EV_KEY.BTN_MIDDLE):
            device.enable(libevdev.EV_KEY.BTN_MIDDLE)
            print('Free middle buttons for everyone!')

Unsurprisingly, the physical device won't generate events for axes it
doesn't have. Enabling event codes is generally only useful to fix
device-specific quirks in one place and then assume that devices are
behaving correctly.

.. note::

        Enabling absolute axes requires extra data. See 
        :func:`disable <libevdev.device.Device.enable>` for details.

Reading events
--------------

libevdev does not have a concept of an event loop, it relies on the caller
to monitor the file descriptor for events. Thus, the concept of
"availablable events" means "events available right now" and the
:func:`events <libevdev.device.Device.events>` function returns exactly
that::

        while True:
            for e in device.events():
                print(e)
            # now do some other stuff, like rendering things

The events returned are of class :class:`InputEvent
<libevdev.event.InputEvent>` and represent the C ``struct input_event``,
but they're type-safer. Every event has a :func:`type
<libevdev.event.InputEvent.type>` and a :func:`code
<libevdev.event.InputEvent.code>` representing its event type and code.
And of course a :func:`value <libevdev.event.InputEvent.value>`.

The most useful method on the input events is :func:`matches
<libevdev.event.InputEvent.matches>` which can be used to compare for
types, codes and/or values::

        for e in device.events():
            if e.matches(libevdev.EV_MSC):
                continue  # don't care about those

            if e.matches(libevdev.EV_REL.REL_X):
                move_by(e.value, 0)
            elif e.matches(libevdev.EV_REL.REL_Y):
                move_by(0, e.value)
            elif e.matches(libevdev.EV_KEY.BTN_MIDDLE, value=1):
                printf('How did we manage to get a middle button press?')

Alternatively, you can create input events and use those for
comparisons::

        btn = InputEvent(libevdev.EV_KEY.BTN_MIDDLE, value=1)

        if btn in device.events():
            print('There is a button event in there')

The above examples all depened on whether ``os.O_NONBLOCK`` was set on the
file descriptor after the initial ``open`` call:

- ``os.O_NONBLOCK`` is set: :func:`events <libevdev.device.Device.events>`
  returns immediately when no events are available.
- ``os.O_NONBLOCK`` is **not** set: :func:`events
  <libevdev.device.Device.events>` blocks until events become available

See :ref:`opening_a_device` for an example on setting ``os.O_NONBLOCK``.

Creating uinput devices
-----------------------

.. note::

   Creating uinput devices requires root access.

Creating virtual devices through uinput is a common case for users that want
to inject input events into the system. libevdev makes this easy by creating
a device from an existing libevdev context::

        device = libevdev.Device()
        device.name = 'my fake device'
        device.enable(libevdev.EV_KEY.BTN_LEFT)
        device.enable(libevdev.EV_KEY.BTN_MIDDLE)
        device.enable(libevdev.EV_KEY.BTN_RIGHT)

        uinput = device.create_uinput_device()
        print('device is now at {}'.format(uinput.devnode))

        press = [libevdev.InputEvent(libevdev.EV_KEY.BTN_MIDDLE, value=1)
                 libevdev.InputEvent(libevdev.EV_SYN.SYN_REPORT, value=0)]
        uinput.send_events(press)

        release = [libevdev.InputEvent(libevdev.EV_KEY.BTN_MIDDLE, value=0)
                   libevdev.InputEvent(libevdev.EV_SYN.SYN_REPORT, value=0)]
        uinput.send_events(release)

In the example above, we create an empty uinput device, set a name and
enable a few event codes. Then we create the uinput device and write a
middle click press, followed by a release.

.. warning::

        An event sequence must always be terminated by with a
        ``libevdev.EV_SYN.SYN_REPORT`` event or the kernel may not process
        the events.

That's really it. The uinput device can be created from any context. By
using a real device as source context it's easy to duplicate an existing
device with exactly the same attributes. The resulting uinput device is a
libevdev context too, so all the previously mentioned methods work on it -
it just won't ever send events. Usually you'd create a new libevdev context
from the device at the uinput's device node::

        uinput = device.create_uinput_device()
        fd = open(uinput.devnode, 'rb')
        newdev = libevdev.Device(fd)
        ...


Summary
-------

This tutorial provided an overview on how to initialize libevdev and handle
basic properties and events. Full examples for some use-cases are available
on the :doc:`examples` page. The :doc:`API documentation <modules>` explains
all functions available to the caller.
