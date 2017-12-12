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
import collections

from .clib import Libevdev
import libevdev

class EventCode:
    """
    A class representing an evdev event code, e.g. ABS_X

    :property value: The numeric value of the event code
    :property name: The string name of this event code
    :property type: The EventType for this event code
    """
    __hash__ = super.__hash__

    def __eq__(self, other):
        if not isinstance(other, EventCode):
            return False

        return self.value == other.value and self.type == other.type

    def __repr__(self):
        return f'{self.name}:{self.value}'

class EventType:
    """
    A class represending an evdev event type (e.g. EV_ABS). All event codes
    within this type are available as class constants, e.g.
    libevdev.EV_ABS.ABS_X

    :property value: The numeric value of the event type
    :property name: The string name of the event type
    :property codes: A list of event codes for this type
    :property max: The maximum event code permitted in this type
    """
    __hash__ = super.__hash__

    def __eq__(self, other):
        assert isinstance(other, EventType)
        return self.value == other.value

    def __repr__(self):
        return f'{self.name}:{self.value}'

class InputProperty:
    """
    A class representing an evdev input property.

    :property value: The numeric value of the property
    :property name: The string name of the property 
    """
    __hash__ = super.__hash__

    def __eq__(self, other):
        assert isinstance(other, InputProperty)
        return self.value == other.value

def _load_consts():
    """
    Loads all event type, code and property names and makes them available
    as enums in the module. Use as e.g. libevdev.EV_SYN.SYN_REPORT.

    Available are::

    libevdev.types ... an list containing all event types, e.g.
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

    types = []

    for t in range(tmax + 1):
        tname = Libevdev.event_to_name(t)
        if tname is None:
            continue

        cmax = Libevdev.type_max(t)

        new_class = type(tname, (EventType, ),
                { 'value': t,
                  'name': tname,
                  'max' : cmax })

        type_object = new_class()
        # libevdev.EV_REL, libevdev.EV_ABS, etc.
        setattr(libevdev, tname, type_object)
        types.append(type_object)

        if cmax is None:
            continue

        codes = []
        for c in range(cmax + 1):
            cname = Libevdev.event_to_name(t, c)
            # For those without names, we just use the type name plus
            # hexcode
            if cname is None:
                cname = "{}_{:02x}".format(tname[3:], c)

            new_class = type(cname, (EventCode, ),
                    { 'type': type_object,
                      'name': cname,
                      'value': c })
            code_object = new_class()
            setattr(type_object, cname, code_object)
            codes.append(code_object)

        setattr(type_object, 'codes', codes)

    # list of all types
    setattr(libevdev, 'types', types)

    pmax = Libevdev.property_to_value("INPUT_PROP_MAX")
    assert pmax is not None
    props = []
    for p in range(pmax + 1):
        pname = Libevdev.property_to_name(p)
        if pname is None:
            continue

        new_class = type(pname, (InputProperty, ),
                         { 'value': p,
                           'name': pname, })
        prop_object = new_class()

        setattr(libevdev, pname, prop_object)
        props.append(prop_object)

    setattr(libevdev, 'props', props)

_load_consts()


def evbit(evtype, evcode=None):
    """
    Takes an event type and an (optional) event code and returns the Enum
    representing that type or code, whichever applies. For example::

        >>> print(libevdev.evbit(0))
        EV_SYN:0

        >>> print(libevdev.evbit(2))
        EV_REL:2

        >>> print(libevdev.evbit(2, 1))
        REL_Y:1

        >>> print(libevdev.evbit(3, 4))
        ABS_RY:4

    The return value can be used in the libevdev API wherever an EventCode
    or EventType is expected.

    Note that if the type name does not exist, this function returns None.
    If the code name does not exist, this function returns a usable Enum
    value nonetheless. This is intentional, while missing type names are a
    bug, missing code names are common on devices that merely enumarate a
    bunch of axes.

    :return: An event code value representing the code
    :rtype: EventCode or EventType
    """

    try:
        t = [t for t in libevdev.types if t.value == evtype or t.name == evtype][0]
    except IndexError:
        return None

    if evcode is None:
        return t

    try:
        c = [c for c in t.codes if c.value == evcode or c.name == evtype][0]
    except IndexError:
        return None

    return c

def propbit(prop):
    """
    Takes a property value and returns the Enum representing that property.

    :return: an Enum of the property or None if it does not exist
    """
    try:
        return [p for p in libevdev.props if p.value == prop or p.name == prop][0]
    except IndexError:
        return None
