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
from .clib import Libevdev
from .clib import READ_FLAG_SYNC, READ_FLAG_NORMAL, READ_FLAG_FORCE_SYNC, READ_FLAG_BLOCKING
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
    A class representing the struct InputAbsinfo for a given EV_ABS code.

    Any of the attributes may be set to None, those that are None are simply
    ignored by libevdev.
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
    This class represents an evdev device backed by libevdev.

    The device may represent a real device in the system or a constructed
    device where the caller supplies all properties of the device.
    """

    def __init__(self, fd=None):
        """
        :param fd: A file-like object

        Create a new libevdev device. If a file is given, the device
        initializes from that file, otherwise the device is uninitialized
        and needs to be set up by the caller. ::

                fd = open("/dev/input/event0", "rb")
                l = libevdev.Device(fd)
                # l now represents the device on event0

        Note that the device is always set to CLOCK_MONOTONIC.

                l2 = libevdev.Device()
                l2.name = "test device"
                l2.enable("EV_REL", "REL_X")
                # l2 is an unbound device with the REL_X bit set

        Note that if a device is constructed manually, the fd of the device
        is always None.
        """
        self._libevdev = Libevdev(fd)
        if fd is not None:
            try:
                self._libevdev.set_clock_id(time.CLOCK_MONOTONIC)
            except AttributeError:
                self._libevdev.set_clock_id(1)

    @property
    def name(self):
        """
        :return: the device name
        """
        return self._libevdev.name

    @name.setter
    def name(self, name):
        self._libevdev.name = name

    @property
    def phys(self):
        """
        :return: the device's kernel phys or None.
        """
        return self._libevdev.phys

    @phys.setter
    def phys(self, phys):
        self._libevdev.phys = phys

    @property
    def uniq(self):
        """
        :return: the device's uniq string or None
        """
        return self._libevdev.uniq

    @uniq.setter
    def uniq(self, uniq):
        self._libevdev.uniq = uniq

    @property
    def driver_version(self):
        """
        :return: the device's driver version
        """
        return self._libevdev.driver_version

    @property
    def id(self):
        """
        :return: A dict with the keys 'bustype', 'vendor', 'product', 'version'.

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
        :return: the fd to this device

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
    def codes(self):
        """
        Returns a dict with all supported event types and event codes, in
        the form of { type : [ code, ...]
        """
        types = {}
        for t in libevdev.EV_BITS:
            if not self.has_event(t):
                continue

            codes = []
            for c in range(t.max):
                if not self.has_event(t, c):
                    continue
                codes.append(c)
            types[t] = codes

        return types

    def has_property(self, prop):
        """
        :param prop: a property
        :return: True if the device has the property, False otherwise
        """
        return self._libevdev.has_property(prop)

    def has_event(self, evtype, evcode = None):
        """
        :param evtype: the event type
        :param evcode: optional, the event code
        :return: True if the device has the type and/or code, False otherwise
        """
        return self._libevdev.has_event(evtype, evcode)

    @property
    def num_slots(self):
        """
        :return: the number of slots on this device or ``None`` if this device
                 does not support slots

        :note: Read-only
        """
        s = self._libevdev.num_slots
        return s if s >= 0 else None

    @property
    def current_slot(self):
        """
        :return: the current of slots on this device or ``None`` if this device
                 does not support slots

        :note: Read-only
        """
        s = self._libevdev.current_slot
        return s if s >= 0 else None

    def absinfo(self, code, new_values=None, kernel=False):
        """
        Query the device's absinfo for the given event code. This function
        both queries and sets the absinfo - if new value is supplied that
        value is now the value of the device.

        :param code: the ABS_<*> code
        :param new_values: an InputAbsInfo struct or None
        :param kernel: If True, assigning new values corresponds to ``libevdev_kernel_set_abs_info``
        :return: an InputAbsInfo struct or None if the device does not have
        the event code
        """

        if new_values is None and kernel:
            raise InvalidArgumentException()

        r = self._libevdev.absinfo(code, new_values, kernel)
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

        :return: an iterator with the currently pending events
        """
        if os.get_blocking(self._libevdev.fd.fileno()):
            flags = READ_FLAG_BLOCKING
        else:
            flags = READ_FLAG_NORMAL

        ev = self._libevdev.next_event(flags)
        while ev is not None:
            yield InputEvent(ev.type, ev.code, ev.value, ev.sec, ev.usec)
            if ev.type == libevdev.EV_BITS.EV_SYN and ev.code == libevdev.EV_SYN.SYN_DROPPED:
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
        if force:
            flags = READ_FLAG_FORCE_SYNC
        else:
            flags = READ_FLAG_SYNC

        ev = self._libevdev.next_event(flags)
        while ev is not None:
            yield InputEvent(ev.type, ev.code, ev.value, ev.sec, ev.usec)
            ev = self._libevdev.next_event(flags)

    def event_value(self, event_type, event_code, new_value=None):
        """
        :param event_type: the event type, either as integer or as string
        :param event_code: the event code, either as integer or as string
        :param new_value: optional, the value to set to
        :return: the current value of type + code, or ``None`` if it doesn't
                 exist on this device
        """
        return self._libevdev.event_value(event_type, event_code, new_value)

    def slot_value(self, slot, event_code, new_value=None):
        """
        :param slot: the numeric slot number
        :param event_code: the ABS_<*> event code, either as integer or string
        :param new_value: optional, the value to set this slot to
        :return: the current value of the slot's code, or ``None`` if it doesn't
                 exist on this device
        """
        return self._libevdev.slot_value(slot, event_code, new_value)
