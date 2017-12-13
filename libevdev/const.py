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

import os
from functools import total_ordering

from ._clib import Libevdev
import libevdev


@total_ordering
class EvdevBit:
    """
    Base class representing an evdev bit, comprised of a name and a value.
    These two properties are guaranteed to exist on anything describing an
    event code, event type or input property that comes out of libevdev::

        >>> print(libevdev.EV_ABS.name)
        EV_ABS
        >>> print(libevdev.EV_ABS.value)
        3
        >>> print(libevdev.EV_SYN.SYN_REPORT.name)
        SYN_REPORT
        >>> print(libevdev.EV_SYN.SYN_REPORT.value)
        0
        >>> print(libevdev.INPUT_PROP_DIRECT.name)
        INPUT_PROP_DIRECT
        >>> print(libevdev.INPUT_PROP_DIRECT.value)
        1

    .. attribute:: value

        The numeric value of the event code

    .. attribute:: name

        The string name of this event code
    """

    def __repr__(self):
        return '{}:{}'.format(self.name, self.value)

    def __eq__(self, other):
        return self.value == other.value

    def __lt__(self, other):
        return self.value < other.value


class EventCode(EvdevBit):
    """
    .. warning ::

        Do not instantiate an object of this class, all objects you'll ever need
        are already present in the libevdev namespace. Use :func:`evbit()`
        to get an :class:`EventCode` from numerical or string values.

    A class representing an evdev event code, e.g. libevdev.EV_ABS.ABS_X.
    To use a :class:`EventCode`, use the namespaced name directly::

        >>> print(libevdev.EV_ABS.ABS_X)
        ABS_X:0
        >>> print(libevdev.EV_ABS.ABS_Y)
        ABS_X:1
        >>> code = libevdev.EV_REL.REL_X
        >>> print(code.type)
        EV_REL:2

    .. attribute:: value

        The numeric value of the event code

    .. attribute:: name

        The string name of this event code

    .. attribute:: type

        The :class:`EventType` for this event code
    """
    __hash__ = super.__hash__

    def __eq__(self, other):
        if not isinstance(other, EventCode):
            return False

        return self.value == other.value and self.type == other.type


class EventType(EvdevBit):
    """
    .. warning ::

        Do not instantiate an object of this class, all objects you'll ever need
        are already present in the libevdev namespace. Use :func:`evbit()`
        to get an :class:`EventType` from numerical or string values.

    A class represending an evdev event type (e.g. EV_ABS). All event codes
    within this type are available as class constants::

        >>> print(libevdev.EV_ABS)
        EV_ABS:3
        >>> print(libevdev.EV_ABS.ABS_X)
        ABS_X:0
        >>> print(libevdev.EV_ABS.max)
        63
        >>> print(libevdev.EV_ABS.ABS_MAX)
        63
        >>> for code in libevdev.EV_ABS.codes[:3]:
        ...     print(code)
        ...
        ABS_X:0
        ABS_Y:1
        ABS_Z:2

    .. attribute:: value

        The numeric value of the event type

    .. attribute:: name

        The string name of this event type

    .. attribute:: codes

        A list of :class:`EventCode` objects for this type

    .. attribute:: max

        The maximum event code permitted in this type as integer
    """
    __hash__ = super.__hash__

    def __eq__(self, other):
        assert isinstance(other, EventType)
        return self.value == other.value


class InputProperty(EvdevBit):
    """
    .. warning ::

        Do not instantiate an object of this class, all objects you'll ever need
        are already present in the libevdev namespace. Use :func:`propbit()`
        to get an :class:`InputProperty` from numerical or string values.

    A class representing an evdev input property::

        >>> print(libevdev.INPUT_PROP_DIRECT)
        INPUT_PROP_DIRECT:1


    .. attribute:: value

        The numeric value of the property

    .. attribute:: name

        The string name of this property
    """
    __hash__ = super.__hash__

    def __eq__(self, other):
        assert isinstance(other, InputProperty)
        return self.value == other.value


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

        >>> print(libevdev.evbit('EV_ABS'))
        EV_ABS:3

        >>> print(libevdev.evbit('EV_ABS', 'ABS_X'))
        ABS_X:0

    A special case is the lookup of an string-based event code without
    the type. Where the string identifier is unique, this will return the
    right value.

        >>> print(libevdev.evbit('ABS_X'))
        ABS_X:0

    The return value can be used in the libevdev API wherever an
    :class:`EventCode` or :class:`EventType` is expected.

    Notable behavior for invalid types or names:

    * If the type does not exist, this function returns None
    * If the type exists but the event code's numeric value does not have a
      symbolic name (and is within the allowed max of the type), this
      function returns a valid event code
    * If the code is outside the allowed maximum for the given type, this
      function returns None
    * If the type name exists but the string value is not a code name, this
      function returns None

    Examples for the above behaviour::

        >>> print(libevdev.evbit(8))
        None
        >>> print(libevdev.evbit('INVALID'))
        None
        >>> print(libevdev.evbit('EV_ABS', 62))
        ABS_3E:62
        >>> print(libevdev.evbit('EV_ABS', 5000))
        None
        >>> print(libevdev.evbit('EV_ABS', 'INVALID'))
        None

    :param evtype: the numeric value or string identifying the event type
    :param evcode: the numeric value or string identifying the event code
    :return: An event code value representing the code
    :rtype: EventCode or EventType
    """
    etype = None
    for t in libevdev.types:
        if t.value == evtype or t.name == evtype:
            etype = t
            break

    if evcode is None and isinstance(evtype, str) and not evtype.startswith('EV_'):
        for t in libevdev.types:
            for c in t.codes:
                if c.name == evtype:
                    return c

    if etype is None or evcode is None:
        return etype

    ecode = None
    for c in etype.codes:
        if c.value == evcode or c.name == evcode:
            ecode = c

    return ecode


def propbit(prop):
    """
    Takes a property value and returns the :class:`InputProperty`
    representing that property::

        >>> print(libevdev.propbit(0))
        INPUT_PROP_POINTER:0
        >>> print(libevdev.propbit('INPUT_PROP_POINTER'))
        INPUT_PROP_POINTER:0
        >>> print(libevdev.propbit(1000))
        None
        >>> print(libevdev.propbit('Invalid'))
        None

    :param prop: the numeric value or string identifying the property
    :return: the converted :class:`InputProperty` or None if it does not exist
    :rtype: InputProperty
    """
    try:
        return [p for p in libevdev.props if p.value == prop or p.name == prop][0]
    except IndexError:
        return None


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
                         {'value': t,
                          'name': tname,
                          'max': cmax})

        type_object = new_class()
        # libevdev.EV_REL, libevdev.EV_ABS, etc.
        setattr(libevdev, tname, type_object)
        types.append(type_object)

        if cmax is None:
            setattr(type_object, 'codes', [])
            continue

        codes = []
        for c in range(cmax + 1):
            cname = Libevdev.event_to_name(t, c)
            # For those without names, we just use the type name plus
            # hexcode
            if cname is None:
                cname = "{}_{:02X}".format(tname[3:], c)

            new_class = type(cname, (EventCode, ),
                             {'type': type_object,
                              'name': cname,
                              'value': c})
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
                         {'value': p,
                          'name': pname})
        prop_object = new_class()

        setattr(libevdev, pname, prop_object)
        props.append(prop_object)

    setattr(libevdev, 'props', props)


if not os.environ.get('READTHEDOCS'):
    _load_consts()
