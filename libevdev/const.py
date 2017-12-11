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

import enum

from .clib import Libevdev
import libevdev

class EventCode(enum.IntEnum):
    @property
    def code(self):
        return self

def _load_consts():
    """
    Loads all event type, code and property names and makes them available
    as enums in the module. Use as e.g. libevdev.EV_SYN.SYN_REPORT.

    Available are::

    libevdev.EV_TYPES ... an enum containing all event types, e.g.
                         libevdev.EV_TYPES.EV_REL

    libevdev.EV_REL ... an enum containing all REL event types, e.g.
                        libevdev.EV_REL.REL_X. The name of each enum value
                        is the string of the code ('REL_X'), the value is the integer
                        value of that code.

    libevdev.EV_ABS ... as above, but for EV_ABS

    libevdev.EV_BITS ... libevdev.EV_FOO as an enum

    Special attributes are (an apply to all EV_foo enums):
        libevdev.EV_REL.type ... the EV_TYPES entry of the event type
        libevdev.EV_REL.max  ... the maximum code in this event type
    """
    Libevdev()  # classmethods, need to make sure it's loaded at once

    tmax = Libevdev.event_to_value("EV_MAX")
    assert tmax is not None

    types = {'EV_MAX': tmax}

    for t in range(tmax + 1):
        tname = Libevdev.event_to_name(t)
        if tname is None:
            continue

        types[tname] = t

    e = enum.IntEnum('EV_TYPES', types)
    setattr(libevdev, 'EV_TYPES', e)

    del types
    types = {}

    for t in range(tmax + 1):
        tname = Libevdev.event_to_name(t)
        cmax = Libevdev.type_max(t)
        if cmax is None:
            continue

        codes = {}

        for c in range(cmax + 1):
            cname = Libevdev.event_to_name(t, c)
            # For those without names, we just use the type name plus
            # hexcode
            if cname is None:
                cname = "{}_{:02x}".format(tname[3:], c)

            codes[cname] = c

        e = EventCode(tname, codes)
        setattr(libevdev, tname, e)
        setattr(e, 'max', cmax)
        setattr(e, 'type', libevdev.EV_TYPES(t))

        types[tname] = e

    e = enum.Enum('EV_BITS', types)
    setattr(libevdev, 'EV_BITS', e)

    props = {}
    pmax = Libevdev.property_to_value("INPUT_PROP_MAX")
    assert pmax is not None
    for p in range(pmax + 1):
        pname = Libevdev.property_to_name(p)
        if pname is None:
            continue

        props[pname] = p

    e = enum.IntEnum(pname, props)
    setattr(libevdev, 'INPUT_PROP', e)


_load_consts()


def e(evtype, evcode=None):
    """
    Takes an event type and an (optional) event code and returns the Enum
    representing that type or code, whichever applies.

    Note that if the type name does not exist, this function returns None.
    If the code name does not exist, this function returns a usable Enum
    value nonetheless. This is intentional, while missing type names are a
    bug, missing code names are common on devices that merely enumarate a
    bunch of axes.

    :return: An Enum value representing the code
    """

    try:
        t = libevdev.EV_BITS(evtype)
    except ValueError:
        return None

    if evcode is None:
        return t

    try:
        return getattr(libevdev, t.name)(evcode)
    except ValueError:
        return None


def p(prop):
    """
    Takes a property value and returns the Enum representing that property.

    :return: an Enum of the property or None if it does not exist
    """
    try:
        return libevdev.INPUT_PROP(prop)
    except ValueError:
        return None
