# -*- coding: latin-1 -*-
# Copyright © 2017 Red Hat, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice (including the next
# paragraph) shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import time
import os

import libevdev
from ._clib import Libevdev, UinputDevice
from ._clib import READ_FLAG_SYNC, READ_FLAG_NORMAL, READ_FLAG_FORCE_SYNC, READ_FLAG_BLOCKING
from .event import InputEvent


class InvalidFileError(Exception):
    """
    A file provided is not a valid file descriptor for libevdev or this
    device must not have a file descriptor
    """
    pass

class InvalidArgumentException(Exception):
    pass

class EventsDroppedException(Exception):
    """
    Notification that the device has dropped events, raised in response to a
    EV_SYN SYN_DROPPED event.

    This exception is raised AFTER the EV_SYN, SYN_DROPPED event has been
    passed on. If SYN_DROPPED events are processed manually, then this
    exception can be ignored.

    Once received (or in response to a SYN_DROPPED event) a caller should
    call device.sync() and process the events accordingly (if any).

    Example::

            fd = open("/dev/input/event0", "rb")
            ctx = libevdev.Device(fd)

            while True:
                try:
                    for e in ctx.events():
                        print(e):
                except EventsDroppedException:
                    print('State lost, re-synching:')
                    for e in ctx.sync():
                        print(e)
    """
    pass

class InputAbsInfo(object):
    """
    A class representing the struct input_absinfo for a given EV_ABS code.

    Any of the attributes may be set to None, those that are None are simply
    ignored by libevdev.

    .. attribute:: minimum

        the minimum value of this axis

    :property minimum: the minimum value for this axis
    :property maximum: the maximum value for this axis
    :property fuzz: the fuzz value for this axis
    :property flat: the flat value for this axis
    :property resolution: the resolution for this axis
    :property value: the current value of this axis
    """
    def __init__(self, minimum=None, maximum=None, fuzz=None, flat=None,
                 resolution=None, value=None):
        self.minimum = minimum
        self.maximum = maximum
        self.fuzz = fuzz
        self.flat = flat
        self.resolution = resolution
        self.value = value

class Device(object):
    """
    This class represents an evdev device backed by libevdev. The device may
    represent a real device in the system or a constructed device where the
    caller supplies all properties of the device.

    Create a new libevdev device. If a file is given, the device
    initializes from that file, otherwise the device is uninitialized
    and needs to be set up by the caller::

            fd = open("/dev/input/event0", "rb")
            l = libevdev.Device(fd)
            # l now represents the device on event0

            l2 = libevdev.Device()
            l2.name = "test device"
            l2.enable(libevdev.EV_REL.REL_X)
            # l2 is an unbound device with the REL_X bit set

    Note that if a device is constructed manually, the fd of the device
    is always None.

    .. note:: The device is always set to CLOCK_MONOTONIC.

    :param fd: fd pointing to a ``/dev/input/eventX`` event node
    :type fd: A file-like object

    """
    def __init__(self, fd=None):
        self._libevdev = Libevdev(fd)
        self._uinput = None
        if fd is not None:
            try:
                self._libevdev.set_clock_id(time.CLOCK_MONOTONIC)
            except AttributeError:
                self._libevdev.set_clock_id(1)

    @property
    def name(self):
        """
        :returns: the device name
        """
        return self._libevdev.name

    @name.setter
    def name(self, name):
        self._libevdev.name = name

    @property
    def phys(self):
        """
        :returns: the device's kernel phys or None.
        """
        return self._libevdev.phys

    @phys.setter
    def phys(self, phys):
        self._libevdev.phys = phys

    @property
    def uniq(self):
        """
        :returns: the device's uniq string or None
        """
        return self._libevdev.uniq

    @uniq.setter
    def uniq(self, uniq):
        self._libevdev.uniq = uniq

    @property
    def driver_version(self):
        """
        :returns: the device's driver version
        """
        return self._libevdev.driver_version

    @property
    def id(self):
        """
        :returns: A dict with the keys 'bustype', 'vendor', 'product', 'version'.

        When used as a setter, only existing keys are applied to the
        device. For example, to update the product ID only::

                ctx = Device()
                id["property"] = 1234
                ctx.id = id

        """
        return self._libevdev.id

    @id.setter
    def id(self, vals):
        self._libevdev.id = vals

    @property
    def fd(self):
        """
        :returns: the fd to this device

        This fd represents the file descriptor to this device, if any. If no
        fd was provided in the constructor.
        """
        return self._libevdev.fd

    @fd.setter
    def fd(self, fileobj):
        """
        Set the fd of the device to the file object given.

        This call overwrites the file given in the constructor or
        a previous call to this function. The new file object becomes the
        object referencing this device, futher events are polled from that
        file.

        Note that libevdev does not synchronize the device and relies on the
        caller to ensure that the new file object points to the same device
        as this context.

        :raises: InvalidFileError - the file is invalid or this device does
        not allow a file to be set
        """
        if self._libevdev.fd is None:
            raise InvalidFileError()
        self._libevdev.fd = fileobj

    @property
    def bits(self):
        """
        Returns a dict with all supported event types and event codes, in
        the form of::

            {
              libevdev.EV_ABS: [libevdev.EV_ABS.ABS_X, ...],
              libevdev.EV_KEY: [libevdev.EV_KEY.BTN_LEFT, ...],
            }
        """
        types = {}
        for t in libevdev.types:
            if not self.has_event(t):
                continue

            codes = []
            for c in t.codes:
                if not self.has_event(c):
                    continue
                codes.append(c)
            types[t] = codes

        return types

    @property
    def properties(self):
        """
        Returns a list of all supported input properties
        """
        return [p for p in libevdev.props if self.has_property(p)]

    def has_property(self, prop):
        """
        :param prop: a property
        :returns: True if the device has the property, False otherwise
        """
        return self._libevdev.has_property(prop.value)

    def has_event(self, evcode):
        """
        :param evcode: the event type or event code
        :type evcode: EventType or EventCode
        :returns: True if the device has the type and/or code, False otherwise
        """
        try:
            return self._libevdev.has_event(evcode.type.value, evcode.value)
        except AttributeError:
            return self._libevdev.has_event(evcode.value)

    @property
    def num_slots(self):
        """
        :returns: the number of slots on this device or ``None`` if this device
                 does not support slots

        :note: Read-only
        """
        return self._libevdev.num_slots

    @property
    def current_slot(self):
        """
        :returns: the current slot on this device or ``None`` if this device
                 does not support slots

        :note: Read-only
        """
        return self._libevdev.current_slot

    def absinfo(self, code, new_values=None, kernel=False):
        """
        Query the device's absinfo for the given event code. This function
        can both query and modify the :class:`InputAbsInfo` values of this
        device - if new_values is not None its contents become the new
        contents of this device axis::

            >>> ai = d.absinfo(libevdev.EV_ABS.ABS_X)
            >>> print(f'Resolution is {ai.resolution}')
            Resolution is 33
            >>> ai.resolution = 45
            >>> d.absinfo(libevdev.EV_ABS.ABS_X, new_values=ai)
            >>> ai = d.absinfo(libevdev.EV_ABS.ABS_X)
            >>> print(f'Resolution is now {ai.resolution}')
            Resolution is now 45

        Any attribute of :class:`InputAbsInfo` that is None is
        ignored::

            >>> ai = InputAbsInfo(resolution=72)
            >>> d.absinfo(libevdev.EV_ABS.ABS_X, new_values=ai)
            >>> ai = d.absinfo(libevdev.EV_ABS.ABS_X)
            >>> print(f'Resolution is now {ai.resolution}')
            Resolution is now 72

        :param code: the ABS_<*> code
        :type code: EventCode
        :param new_values: an InputAbsInfo struct or None
        :param kernel: If True, assigning new values corresponds to
            ``libevdev_kernel_set_abs_info`` and makes the changes permanent on
            the underlying kernel device.
        :returns: an InputAbsInfo struct or None if the device does not have
                 the event code
        """

        if new_values is None and kernel:
            raise InvalidArgumentException()

        r = self._libevdev.absinfo(code.value, new_values, kernel)
        if r is None:
            return r

        return InputAbsInfo(r['minimum'], r['maximum'],
                            r['fuzz'], r['flat'],
                            r['resolution'], r['value'])

    def events(self):
        """
        Returns an iterator with currently pending events.

        Event processing should look like this::

            fd = open("/dev/input/event0", "rb")
            ctx = libevdev.Device(fd)

            while True:
                for e in ctx.events():
                    print(e):

        :returns: an iterator with the currently pending events
        """
        if self._libevdev.fd is None:
            return []

        if os.get_blocking(self._libevdev.fd.fileno()):
            flags = READ_FLAG_BLOCKING
        else:
            flags = READ_FLAG_NORMAL

        ev = self._libevdev.next_event(flags)
        while ev is not None:
            code = libevdev.evbit(ev.type, ev.code)
            yield InputEvent(code, ev.value, ev.sec, ev.usec)
            if code == libevdev.EV_SYN.SYN_DROPPED:
                raise EventsDroppedException()
            ev = self._libevdev.next_event(flags)

    def sync(self, force=False):
        """
        Returns an iterator with events pending to re-sync the caller's
        view of the device with the one from libevdev.

        :param force: if set, the device forces an internal sync. This is
            required after changing the fd of the device when the device state
            may have changed while libevdev was not processing events.
        """
        if self._libevdev.fd is None:
            return []

        if force:
            flags = READ_FLAG_FORCE_SYNC
        else:
            flags = READ_FLAG_SYNC

        ev = self._libevdev.next_event(flags)
        while ev is not None:
            code = libevdev.evbit(ev.type, ev.code)
            yield InputEvent(code, ev.value, ev.sec, ev.usec)
            ev = self._libevdev.next_event(flags)

    def event_value(self, event_code, new_value=None):
        """
        :param event_code: the event code
        :type event_code: EventCode
        :param new_value: optional, the value to set to
        :returns: the current value of the event code, or ``None`` if it doesn't
                 exist on this device

        .. warning::

            If a new_value is given, the event_code must not be a pure event
            type
        """
        return self._libevdev.event_value(event_code.type.value, event_code.value, new_value)

    def slot_value(self, slot, event_code, new_value=None):
        """
        Retrieve the current value of the given event code for the given
        slot. If the event code is not a valid slot event code or the slot
        exceeds the value of :func:`num_slots`, an
        InvalidArgumentException is raised.

        :param slot: the numeric slot number
        :param event_code: the ``libevdev.EV_ABS.ABS_MT_*`` event code
        :param new_value: optional, the value to set this slot to
        :returns: the current value of the slot's code, or ``None`` if it doesn't
                 exist on this device
        :raises: InvalidArgumentException
        """
        if self.num_slots is None or self.num_slots < slot:
            raise InvalidArgumentException()

        if event_code.value <= libevdev.EV_ABS.ABS_MT_SLOT.value:
            raise InvalidArgumentException()

        return self._libevdev.slot_value(slot, event_code.value, new_value)

    def enable(self, event_code, data=None):
        """
        Enable an event type or event code on this device, even if not
        supported by this device.
        If event_code is an :class:`EventType`, that type is enabled and data
        is ignored.

        If event_code is one of ``libevdev.EV_ABS.ABS_*``, then data must be
        a :class:`InputAbsInfo`. Any unset fields of the
        :class:`InputAbsInfo` are replaced with
        0, i.e. the following example is valid and results in a
        fuzz/flat/resolution of zero::

                ctx = libevdev.Device()
                abs = InputAbsInfo(minimum=0, maximum=100)
                ctx.enable(libevdev.EV_ABS.ABS_X, data)

        If event_code is one of ``libevdev.EV_REP.REP_``, then data must be
        an integer.

        :param event_code: the event code
        :type event_code: EventCode or EventType
        :param data: if event_code is not ``None``, data points to the
                     code-specific information.

        """
        if data is not None:
            data = {
                    "minimum": data.minimum,
                    "maximum": data.maximum,
                    "fuzz": data.fuzz,
                    "flat": data.flat,
                    "resolution": data.resolution,

            }
        try:
            self._libevdev.enable(event_code.type.value, event_code.value, data)
        except AttributeError:
            self._libevdev.enable(event_code.value)

    def disable(self, event_code):
        """
        Disable the given event type or event code on this device. If the
        device does not support this type or code, this function does
        nothing. Otherwise, all future events from this device that match
        this type or code will be discarded::

            >>> d.disable(libevdev.EV_ABS)
            # All EV_ABS events are filtered now
            >>> d.disable(libevdev.EV_KEY.BTN_LEFT)
            # All BTN_LEFt events are filtered now

        To re-enable an event type or code, use :func:`enable()`

        :param event_code: the event type or code
        :type event_code: EventType or EventCode
        """
        try:
            self._libevdev.disable(event_code.type.value, event_code.value);
        except AttributeError:
            self._libevdev.disable(event_code.value)

    @property
    def devnode(self):
        """
        Returns the device node for this device. The device node is None if
        this device has not been created as uinput device.
        """
        if not self._uinput:
            return None
        return self._uinput.devnode

    @property
    def syspath(self):
        """
        Returns the syspath for this device. The syspath is None if this
        device has not been created as uinput device.
        """
        if not self._uinput:
            return None
        return self._uinput.syspath

    def create(self, uinput_fd=None):
        """
        Creates a new uinput device from this libevdev device. When created,
        the device's fd now points to the new uinput device::

            fd = open('/dev/input/event0', 'rb')
            d = libevdev.Device(fd)
            d.name = 'duplicated device'
            d.create()
            # d is now a duplicate of the event0 device with a custom name

        Or to create a new device from scratch::

            d = libevdev.Device()
            d.name = 'test device'
            d.enable(libevdev.EV_KEY.BTN_LEFT)
            d.create()
            # d is now a device with a single button

        :param uinput_fd: A file descriptor to the /dev/input/uinput device. If None, the device is opened and closed automatically.
        :raises: OSError
        """

        self._uinput = UinputDevice(self._libevdev, uinput_fd)
