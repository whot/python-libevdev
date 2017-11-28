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

class InputEvent(object):
    """
    Represents one input event of type struct input_event as defined in
    linux/input.h and returned by libevdev_next_event().
    """

    def __init__(self, sec, usec, type, code, value):
        self.sec = sec
        self.usec = usec
        self.type = type
        self.code = code
        self.value = value

    def matches(self, type, code=None, value=None):
        """
        Check if an event matches a given event type and/or event code. The
        following invocations are all accepted::

                if ev.matches("EV_REL"):
                        pass

                if ev.matches(0x02):
                        pass

                if ev.matches("EV_REL", "REL_X"):
                        pass

                if ev.matches(0x02, "REL_X"):
                        pass

                if ev.matches(0x02, 0):
                        pass

                if ev.matches("EV_REL", "REL_X", 1):
                        pass

        :param type: the event type, one of EV_<*> as string or integer
        :param code: optional, the event code as string or integer
        :param value: optional, the event value
        :return: True if the type matches this event's type and this event's
                 code matches the given code (if any) and this event's value
                 matches the given value (if any)
        """
        if not isinstance(type, int):
            type = Libevdev.event_to_value(type)

        if type != self.type:
            return False
        elif code is None:
            return True

        if not isinstance(code, int):
            code = Libevdev.event_to_value(type, code)

        if code != self.code:
            return None
        elif value is None:
            return True

        return value == self.value

    @property
    def type_name(self):
        """
        :return: The type name as string, e.g. "EV_REL"
        """
        return Libevdev.event_to_name(self.type)

    @property
    def code_name(self):
        """
        :return: The code name as string, e.g. "REL_X"
        """
        return Libevdev.event_to_name(self.type, self.code)

    def __eq__(self, other):
        return self.matches(other.type, other.code, other.value)

