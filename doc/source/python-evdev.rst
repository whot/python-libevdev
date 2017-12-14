Difference between libevdev-python and python-evdev
===================================================

python-evdev is an existing package that provides python access to the evdev
protocol. It's documentation is found here: https://python-evdev.readthedocs.io/en/latest/

They both wrap the same kernel protocol, so there is a large overlap
between the two projects.

The biggest difference and motivation for libevdev-python was that it wraps
libevdev rather than just using the kernel directly. This provides a number
of advantages:

* access to the state of the device (rather than just the events)
* correct handling of fake multitouch devices
* synching of slots and per-slot state
* transparent generation of missing tracking ids after SYN_DROPPED
* disabling/enabling events on a per-context basis, so one can disable/enable ABS_FOO and then not care about quirks in the client-side code.
* transparent handling of the UI_GET_SYSNAME ioctl
* transparent handling of the UI_DEV_SETUP ioctl

The above are all features that were added to libevdev (the C library) over
time because of a need for it in projects like the Xorg drivers, libinput,
evemu and others.

Unfortunately, the evdev kernel API is very simple, but getting the behavior
of the API correct is hard. Even kernel drivers frequently do it wrong.
libevdev (the C library) does hide a lot of that and thus makes consuming
evdev safer.

From an API perspective, libevdev-python and python-evdev have two slightly
different approaches. For example,

* python-evdev opens the device directly and provides multiple ways of
  reading events from that device (using
  ``asyncore``, ``select``, ``selectors``, ``asyncio``, etc.).
  libevdev-python requires that the caller opens the file descriptor and
  monitors it, it merely pulls the events off when requested to do so.
* libevdev-python requires the conversion into `EventCode` and
  `EventType` early on, the rest of the API only deals with those.
  python-evdev largely sticks to integers instead (e.g. `dev.leds()` returns
  an integer array). This makes python-evdev less type-safe than
  libevdev-python.

There are other differences as well, but, unsurprisingly, we think that
libevdev-python is the better API and the safer choice. YMMV :)
