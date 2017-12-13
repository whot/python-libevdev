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

from .const import EventType, EventCode


class InputEvent(object):
    """
    Represents one input event of type struct input_event as defined in
    ``linux/input.h`` and returned by ``libevdev_next_event()``.

    Comparison between events can be done via the :func:`matches()` function
    or by comparing two input events. Two events match when their most
    precise attribute match and all other attributes are None::

        >>> e = InputEvent(libevdev.EV_REL.REL_X, value=1)
        >>> e == InputEvent(libevdev.EV_REL)
        True
        >>> e == InputEvent(libevdev.EV_ABS)
        True
        >>> e == InputEvent(libevdev.EV_REL.REL_X)
        True
        >>> e == InputEvent(libevdev.EV_REL.REL_Y)
        False
        >>> e == InputEvent(libevdev.EV_REL.REL_X, value=1)
        True
        >>> e == InputEvent(libevdev.EV_REL.REL_X, value=2)
        False

    .. attribute:: code

        The :class:`EventCode` or :class:`EventType` for this input event

    .. attribute:: value

        The (optional) value for the event's axis

    .. attribute:: sec

        The timestamp, seconds

    .. attribute:: usec

        The timestamp, microseconds
    """

    def __init__(self, code, value=None, sec=0, usec=0):
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
        :return: the EventCode for this event or None
        :rtype: EventCode
        """
        return self._code

    @property
    def type(self):
        """
        :return: the event type for this event
        :rtype: EventType
        """
        return self._type

    def matches(self, code, value=None):
        """
        :param code: the event type or code
        :type code: EventType or EventCode
        :param value: optional, the event value
        :return: True if the type matches this event's type and this event's
                 code matches the given code (if any) and this event's value
                 matches the given value (if any)

        Check if an event matches a given event type and/or code. The
        following invocations show how to match on an event type, an event
        code and an event code with a specific value::


                if ev.matches(libevdev.EV_REL):
                        pass

                if ev.matches(libevdev.EV_REL.REL_X):
                        pass

                if ev.matches(libevdev.EV_REL.REL_X, 1):
                        pass
        """

        if value is not None and self.value is not None and self.value != value:
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
