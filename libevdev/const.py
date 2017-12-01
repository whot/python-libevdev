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

def _load_consts():
    """
    Loads all event type, code and property names and makes them available
    as enums in the module. Use as e.g. libevdev.EV_SYN.SYN_REPORT.
    """
    module = __import__(__name__)

    l = Libevdev() # classmethods, need to make sure it's loaded at once

    tmax = Libevdev.event_to_value("EV_MAX")
    assert tmax is not None


    types = {'EV_MAX' : tmax}

    for t in range(tmax + 1):
        tname = Libevdev.event_to_name(t)
        cmax = Libevdev.type_max(t)
        if cmax is None:
            continue

        types[tname] = t

        codes = {}

        for c in range(cmax + 1):
            cname = Libevdev.event_to_name(t, c)
            # For those without names, we just use the type name plus
            # hexcode
            if cname is None:
                cname = "{}_{:02x}".format(tname[3:], c)

            codes[cname] = c

        e = enum.IntEnum(tname, codes)
        setattr(module, tname, e)

    e = enum.IntEnum('EV_BIT', types)
    setattr(module, 'EV_BIT', e)

    for v in e:
        setattr(v, 'max', Libevdev.type_max(t))

    props = {}
    pmax = Libevdev.property_to_value("INPUT_PROP_MAX")
    assert pmax is not None
    for p in range(pmax + 1):
        pname = Libevdev.property_to_name(p)
        if pname is None:
            continue

        props[pname] = p

    e = enum.IntEnum(pname, props)
    setattr(module, 'INPUT_PROP', e)

_load_consts()

def e(evtype, evcode=None):
    """
    Takes an event type and an (optional) event code and returns the enum
    representing that type or code, whichever applies.
    """

    module = __import__(__name__)
    try:
        t = getattr(module, 'EV_BIT')(evtype)
    except ValueError:
        return None

    if evcode is None:
        return t

    try:
        return getattr(module, t.name)(evcode)
    except ValueError:
        return None

def p(prop):
    """
    Takes a property value and returns the enum representing that property.
    """
    module = __import__(__name__)
    try:
        return getattr(module, 'INPUT_PROP')(prop)
    except ValueError:
        return None


def type_name(t):
    return Libevdev.event_to_name(t)


def type_max(t):
    return Libevdev.type_max(t)
