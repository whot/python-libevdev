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

from enum import Enum

from .clib import Libevdev
from .const import EventType, EventCode
import libevdev

class InputEvent(object):
    """
    Represents one input event of type struct input_event as defined in
    linux/input.h and returned by libevdev_next_event().
    """

    def __init__(self, code, value=None, sec=0, usec=0):
        """
        :param code: the EventCode or EventType for this input event
        :param value: an optional event value
        :param sec: the timestamp, seconds
        :param usec: the timestamp, microseconds
        """
        assert isinstance(code, EventCode) or isinstance(code, EventType)

        if isinstance(code, EventCode):
            self._type = code.type
            self._code = code
        else:
            self._type = code
            self._code = None
        self.sec = sec
        self.usec = usec
        self.value = value

    @property
    def code(self):
        """
        :return: the EventCode for this event

        It is an error to call this function for an event initialized with
        an event type only.
        """
        return self._code

    @property
    def type(self):
        """
        :return: the EventType for this event
        """
        return self._type

    def matches(self, code, value=None):
        """
        Check if an event matches a given event type and/or event code. The
        following invocations are all accepted. Matching on the enum of the
        event type or code::

                if ev.matches(libevdev.EV_BITS.EV_REL):
                        pass

                if ev.matches(libevdev.EV_REL.REL_X):
                        pass

        Matching on an event with a value::

                if ev.matches(libevdev.EV_REL.REL_X, 1):
                        pass

        :param code: the event type or code, one of EV_<*> values
        :param value: optional, the event value
        :return: True if the type matches this event's type and this event's
                 code matches the given code (if any) and this event's value
                 matches the given value (if any)
        """

        if value is not None and self.value != value:
            return False

        if isinstance(code, EventType):
            return self._type == code
        else:
            return self._code == code

    def __eq__(self, other):
        if not isinstance(other, InputEvent):
            return False

        if self.code is None or other.code is None:
            return self.matches(other.type, other.value)

        return self.matches(other.code, other.value)

    def __repr__(self):
        tname = self.type.name
        cname = None
        if self.code is not None:
            cname = self.code.name
        return 'InputEvent({}, {}, {})'.format(tname, cname, self.value)

