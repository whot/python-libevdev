# -*- coding: latin-1 -*-
# Copyright © 2016 Red Hat, Inc.
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

import libevdev

import os
import ctypes
import errno
from ctypes import c_char_p
from ctypes import c_int
from ctypes import c_uint
from ctypes import c_void_p
from ctypes import c_long
from ctypes import c_int32
from ctypes import c_uint16

READ_FLAG_SYNC = 0x1
READ_FLAG_NORMAL = 0x2
READ_FLAG_FORCE_SYNC = 0x4
READ_FLAG_BLOCKING = 0x8


class _InputAbsinfo(ctypes.Structure):
    _fields_ = [("value", c_int32),
                ("minimum", c_int32),
                ("maximum", c_int32),
                ("fuzz", c_int32),
                ("flat", c_int32),
                ("resolution", c_int32)]


class _InputEvent(ctypes.Structure):
    _fields_ = [("sec", c_long),
                ("usec", c_long),
                ("type", c_uint16),
                ("code", c_uint16),
                ("value", c_int32)]


class _LibraryWrapper(object):
    """
    Base class for wrapping a shared library. Do not use directly.
    """
    _lib = None  # The shared library, shared between instances of the class

    # List of API prototypes, must be set by the subclass
    _api_prototypes = {
        # "function_name" : {
        #   "argtypes": [c_void_p, c_char_p, etc. ], # arguments
        #   "restype": c_void_p, # return type
        #   "restype": c_void_p, # return type
        # }
    }

    def __init__(self):
        super(_LibraryWrapper, self).__init__()
        self._load()

    @classmethod
    def _load(cls):
        if cls._lib is not None:
            return cls._lib

        cls._lib = cls._cdll()
        for (name, attrs) in cls._api_prototypes.items():
            func = getattr(cls._lib, name)
            func.argtypes = attrs["argtypes"]
            func.restype = attrs["restype"]

            # default name is the libevdev name minus the libevdev prefix
            # This makes all functions hidden and require
            # one-by-one-mapping
            prefix = len("libevdev")
            pyname = dict.get(attrs, "name", name[prefix:])
            setattr(cls, pyname, func)

        return cls._lib

    @staticmethod
    def _cdll():
        """Override in subclass"""
        raise NotImplementedError


class Libevdev(_LibraryWrapper):
    """
    This class provides a wrapper around the libevdev C library.

    The API is modelled closely after the C API. API documentation in this
    document only lists the specific behavior of the Phython API. For
    information on the behavior of libevdev itself, see

    https://www.freedesktop.org/software/libevdev/doc/latest/

    Properties in this class are read-write unless specified otherwise.

    .. warning::

        Do not use this class directly
    """

    @staticmethod
    def _cdll():
        return ctypes.CDLL("libevdev.so.2", use_errno=True)

    _api_prototypes = {
        # const char *libevdev_event_type_get_name(unsigned int type);
        "libevdev_event_type_get_name": {
            "argtypes": (c_uint,),
            "restype": c_char_p
        },
        # int libevdev_event_type_from_name(const char *name);
        "libevdev_event_type_from_name": {
            "argtypes": (c_char_p,),
            "restype": c_int
        },
        # const char *libevdev_event_code_get_name(unsigned int type, unsigned int code);
        "libevdev_event_code_get_name": {
            "argtypes": (c_uint, c_uint,),
            "restype": c_char_p
        },
        # int libevdev_event_code_from_name(unsigned int type, const char *name);
        "libevdev_event_code_from_name": {
            "argtypes": (c_uint, c_char_p,),
            "restype": c_int
        },
        # const char *libevdev_property_get_name(unsigned int prop);
        "libevdev_property_get_name": {
            "argtypes": (c_uint,),
            "restype": c_char_p,
        },
        # int libevdev_property_from_name(const char *name);
        "libevdev_property_from_name": {
            "argtypes": (c_char_p,),
            "restype": c_int
        },
        # void libevdev_event_type_get_max(int)
        "libevdev_event_type_get_max": {
            "argtypes": (c_int, ),
            "restype": c_int,
        },
        # struct libevdev *libevdev_new(void);
        "libevdev_new": {
            "argtypes": (),
            "restype": c_void_p,
        },
        # struct libevdev *libevdev_free(struct libevdev *);
        "libevdev_free": {
            "argtypes": (c_void_p,),
            "restype": None,
        },
        ###############################
        # Simple getters and setters  #
        ###############################
        # const char * libevdev_get_name(struct libevdev *);
        "libevdev_get_name": {
            "argtypes": (c_void_p,),
            "restype": c_char_p,
        },
        # void libevdev_set_name(struct libevdev *, const char*);
        "libevdev_set_name": {
            "argtypes": (c_void_p, c_char_p),
            "restype": None,
        },
        # const char * libevdev_get_phys(struct libevdev *);
        "libevdev_get_phys": {
            "argtypes": (c_void_p,),
            "restype": c_char_p,
        },
        # void libevdev_set_phys(struct libevdev *, const char*);
        "libevdev_set_phys": {
            "argtypes": (c_void_p, c_char_p),
            "restype": None,
        },
        # const char * libevdev_get_uniq(struct libevdev *);
        "libevdev_get_uniq": {
            "argtypes": (c_void_p,),
            "restype": c_char_p,
        },
        # void libevdev_set_uniq(struct libevdev *, const char*);
        "libevdev_set_uniq": {
            "argtypes": (c_void_p, c_char_p),
            "restype": None,
        },
        # int libevdev_get_driver_version(struct libevdev *);
        "libevdev_get_driver_version": {
            "argtypes": (c_void_p, ),
            "restype": c_int,
        },
        # void libevdev_set_clock_id(struct libevdev *, int)
        "libevdev_set_clock_id": {
            "argtypes": (c_void_p, c_int),
            "restype": c_int,
        },
        ###############################
        # Custom getters and setters  #
        ###############################
        # int libevdev_get_id_bustype(struct libevdev *)
        "libevdev_get_id_bustype": {
            "argtypes": (c_void_p,),
            "restype": c_int,
        },
        # int libevdev_get_id_vendor(struct libevdev *)
        "libevdev_get_id_vendor": {
            "argtypes": (c_void_p,),
            "restype": c_int,
        },
        # int libevdev_get_id_product(struct libevdev *)
        "libevdev_get_id_product": {
            "argtypes": (c_void_p,),
            "restype": c_int,
        },
        # int libevdev_get_id_version(struct libevdev *)
        "libevdev_get_id_version": {
            "argtypes": (c_void_p,),
            "restype": c_int,
        },
        # void libevdev_set_id_bustype(struct libevdev *, int)
        "libevdev_set_id_bustype": {
            "argtypes": (c_void_p, c_int),
            "restype": None,
        },
        # void libevdev_set_id_vendor(struct libevdev *, int)
        "libevdev_set_id_vendor": {
            "argtypes": (c_void_p, c_int),
            "restype": None,
        },
        # void libevdev_set_id_product(struct libevdev *, int)
        "libevdev_set_id_product": {
            "argtypes": (c_void_p, c_int),
            "restype": None,
        },
        # void libevdev_set_id_version(struct libevdev *, int)
        "libevdev_set_id_version": {
            "argtypes": (c_void_p, c_int),
            "restype": None,
        },
        # int libevdev_set_fd(struct libevdev *, int)
        "libevdev_set_fd": {
            "argtypes": (c_void_p, c_int),
            "restype": c_int,
        },
        # int libevdev_change_fd(struct libevdev *, int)
        "libevdev_change_fd": {
            "argtypes": (c_void_p, c_int),
            "restype": c_int,
        },
        # int libevdev_get_fd(struct libevdev *)
        "libevdev_get_fd": {
            "argtypes": (c_void_p, ),
            "restype": c_int,
        },
        # int libevdev_grab(struct libevdev *)
        "libevdev_grab": {
            "argtypes": (c_void_p, c_int),
            "restype": c_int,
        },
        # const struct input_absinfo *libevdev_get_abs_info(struct libevdev*,  int code)
        "libevdev_get_abs_info": {
            "argtypes": (c_void_p, c_int),
            "restype": ctypes.POINTER(_InputAbsinfo),
        },
        # We don't need to wrap libevdev_set_abs_info(), we get the same
        # using get_abs_info and overwrite the values.
        #
        # const struct input_absinfo *libevdev_get_abs_info(struct libevdev*,  int code)
        "libevdev_kernel_set_abs_info": {
            "argtypes": (c_void_p, c_int, ctypes.POINTER(_InputAbsinfo)),
            "restype": (c_int)
        },
        ##########################
        # Various has_ functions #
        ##########################
        "libevdev_has_property": {
            "argtypes": (c_void_p, c_int),
            "restype": (c_int)
        },
        "libevdev_has_event_type": {
            "argtypes": (c_void_p, c_int),
            "restype": (c_int)
        },
        "libevdev_has_event_code": {
            "argtypes": (c_void_p, c_int, c_int),
            "restype": (c_int)
        },
        ##########################
        # Other functions        #
        ##########################
        "libevdev_set_event_value": {
            "argtypes": (c_void_p, c_int, c_int, c_int),
            "restype": (c_int)
        },
        "libevdev_get_event_value": {
            "argtypes": (c_void_p, c_int, c_int),
            "restype": (c_int),
        },
        "libevdev_enable_event_type": {
            "argtypes": (c_void_p, c_int),
            "restype": (c_int),
        },
        "libevdev_enable_event_code": {
            "argtypes": (c_void_p, c_int, c_int, c_void_p),
            "restype": (c_int),
        },
        "libevdev_disable_event_type": {
            "argtypes": (c_void_p, c_int),
            "restype": (c_int),
        },
        "libevdev_disable_event_code": {
            "argtypes": (c_void_p, c_int, c_int),
            "restype": (c_int),
        },
        "libevdev_enable_property": {
            "argtypes": (c_void_p, c_int),
            "restype": (c_int),
        },
        "libevdev_next_event": {
            "argtypes": (c_void_p, c_uint, ctypes.POINTER(_InputEvent)),
            "restype": c_int,
        },
        "libevdev_get_num_slots": {
            "argtypes": (c_void_p,),
            "restype": c_int,
        },
        "libevdev_get_current_slot": {
            "argtypes": (c_void_p,),
            "restype": c_int,
        },
        "libevdev_get_slot_value": {
            "argtypes": (c_void_p, c_uint, c_uint),
            "restype": c_int,
        },
        "libevdev_set_slot_value": {
            "argtypes": (c_void_p, c_uint, c_uint, c_int),
            "restype": c_int,
        },
        "libevdev_has_event_pending": {
            "argtypes": (c_void_p,),
            "restype": c_int,
        },
    }

    def __init__(self, fd=None):
        """
        :param fd: A file-like object

        Create a new libevdev instance. If a file is given this call is
        equivalent to ``libevdev_new_from_fd()``, otherwise it is equivalent
        to ``libevdev_new()``::

                fd = open("/dev/input/event0", "rb")
                l = libevdev.Libevdev(fd)
                # l now represents the device on event0

                l2 = libevdev.Libevdev()
                l2.name = "test device"
                l2.enable("EV_REL", "REL_X")
                # l2 is an unbound device with the REL_X bit set

        """
        super(Libevdev, self).__init__()
        self._ctx = self._new()
        self._file = None
        if fd is not None:
            self.fd = fd

    def __del__(self):
        if hasattr(self, "_ctx"):
            self._free(self._ctx)

    @property
    def name(self):
        """
        :return: A string with the device's kernel name.
        """
        return self._get_name(self._ctx).decode("iso8859-1")

    @name.setter
    def name(self, name):
        if name is None:
            name = ''
        return self._set_name(self._ctx, name.encode("iso8859-1"))

    @property
    def phys(self):
        """
        :return: A string with the device's kernel phys or None.
        """
        phys = self._get_phys(self._ctx)
        if not phys:
            return None
        return phys.decode("iso8859-1")

    @phys.setter
    def phys(self, phys):
        # libevdev issue: phys may be NULL, but can't be set to NULL
        if phys is None:
            phys = ''
        return self._set_phys(self._ctx, phys.encode("iso8859-1"))

    @property
    def uniq(self):
        """
        :return: A string with the device's kernel uniq or None.
        """
        uniq = self._get_uniq(self._ctx)
        if not uniq:
            return None
        return uniq.decode("iso8859-1")

    @uniq.setter
    def uniq(self, uniq):
        # libevdev issue: uniq may be NULL, but can't be set to NULL
        if uniq is None:
            uniq = ''
        return self._set_uniq(self._ctx, uniq.encode("iso8859-1"))

    @property
    def driver_version(self):
        """
        :note: Read-only
        """
        return self._get_driver_version(self._ctx)

    @property
    def id(self):
        """
        :return: A dict with the keys 'bustype', 'vendor', 'product', 'version'.

        When used as a setter, only existing keys are applied to the
        device. For example, to update the product ID only::

                ctx = Libevdev()
                id["property"] = 1234
                ctx.id = id

        This is a combined version of the libevdev calls
        ``libevdev_get_id_busytype()``, ``libevdev_get_id_vendor()``,
        ``libevdev_get_id_product()``, ``libevdev_get_id_version()`` and the
        respective setters.

        """
        bus = self._get_id_bustype(self._ctx)
        vdr = self._get_id_vendor(self._ctx)
        pro = self._get_id_product(self._ctx)
        ver = self._get_id_version(self._ctx)
        return {"bustype": bus,
                "vendor": vdr,
                "product": pro,
                "version": ver}

    @id.setter
    def id(self, vals):
        if "bustype" in vals:
            self._set_id_bustype(self._ctx, vals["bustype"])
        if "vendor" in vals:
            self._set_id_vendor(self._ctx, vals["vendor"])
        if "product" in vals:
            self._set_id_product(self._ctx, vals["product"])
        if "version" in vals:
            self._set_id_version(self._ctx, vals["version"])

    def set_clock_id(self, clock):
        """
        :param clock: time.CLOCK_MONOTONIC
        :return: a negative errno on failure or 0 on success.
        """
        return self._set_clock_id(self._ctx, clock)

    @property
    def fd(self):
        """
        :return: The file-like object used during constructor or in the most
                 recent assignment to self.fd.

        When assigned the first time and no file has been passed to the
        constructor, the assignment is equivalent to ``libevdev_set_fd()``.
        Subsequently, any assignments are equivalent to
        ``libevdev_change_fd``::

                fd = open("/dev/input/event0", "rb")
                l = libevdev.Libevdev(fd)
                assert(l.fd == fd)

                fd2 = open("/dev/input/event0", "rb")
                l.fd = fd2
                assert(l.fd == fd2)

                l = libevdev.Libevdev()
                l.fd = fd
                assert(l.fd == fd)
                l.fd = fd2
                assert(l.fd == fd2)

        :note: libevdev uses the ``fileno()`` of the object.
        """
        return self._file

    @fd.setter
    def fd(self, fileobj):
        try:
            fd = fileobj.fileno()
        except AttributeError:
            raise libevdev.InvalidFileError

        if self._file is None:
            r = self._set_fd(self._ctx, fd)
        else:
            r = self._change_fd(self._ctx, fd)

        if r != 0:
            raise OSError(-r, os.strerror(-r))

        # sanity check:
        if self._get_fd(self._ctx) != fd:
            print("FIXME: fileno() != get_fd()")

        self._file = fileobj

    def grab(self, enable_grab=True):
        """
        :param enable_grab: True to grab, False to ungrab
        :return: 0 on success or a negative errno on failure
        """
        # libevdev doesn't use 0/1 here but numbered values
        if enable_grab:
            mode = 3
        else:
            mode = 4
        r = self._grab(self._ctx, mode)
        if r != 0:
            raise OSError(-r, os.strerror(-r))

    def absinfo(self, code, new_values=None, kernel=False):
        """
        :param code: the ABS_<*> code as integer or as string
        :param new_values: a dict with the same keys as the return values.
        :param kernel: If True, assigning new values corresponds to ``libevdev_kernel_set_abs_info``
        :return: a dictionary with the keys "value", "min", "max",
                 "resolution", "fuzz", "flat"; ``None`` if the code does not exist on
                 this device

        :note: The returned value is a copy of the value returned by
               libevdev. Changing a value in the dictionary does not change the
               matching property. To change the device, reassign the
               dictionary to the absinfo code.
               This is different to the libevdev behavior.
        """
        if not isinstance(code, int):
            if not code.startswith("ABS_"):
                raise ValueError()
            code = self.event_to_value("EV_ABS", code)
        absinfo = self._get_abs_info(self._ctx, code)

        if not absinfo:
            return None

        if new_values is not None:
            if "minimum" in new_values:
                absinfo.contents.minimum = new_values["minimum"]
            if "maximum" in new_values:
                absinfo.contents.maximum = new_values["maximum"]
            if "value" in new_values:
                absinfo.contents.value = new_values["value"]
            if "fuzz" in new_values:
                absinfo.contents.fuzz = new_values["fuzz"]
            if "flat" in new_values:
                absinfo.contents.flat = new_values["flat"]
            if "resolution" in new_values:
                absinfo.contents.resolution = new_values["resolution"]

            if kernel:
                rc = self._kernel_set_abs_info(self._ctx, code, absinfo)
                if rc != 0:
                    raise OSError(-rc, os.strerror(-rc))

        return {"value": absinfo.contents.value,
                "minimum": absinfo.contents.minimum,
                "maximum": absinfo.contents.maximum,
                "fuzz": absinfo.contents.fuzz,
                "flat": absinfo.contents.flat,
                "resolution": absinfo.contents.resolution}

    @classmethod
    def property_to_name(cls, prop):
        """
        :param prop: the numerical property value
        :return: A string with the property name or ``None``

        This function is the equivalent to ``libevdev_property_get_name()``
        """
        name = cls._property_get_name(prop)
        if not name:
            return None
        return name.decode("iso8859-1")

    @classmethod
    def property_to_value(cls, prop):
        """
        :param prop: the property name as string
        :return: The numerical property value or ``None``

        This function is the equivalent to ``libevdev_property_from_name()``
        """
        v = cls._property_from_name(prop.encode("iso8859-1"))
        if v == -1:
            return None
        return v

    @classmethod
    def type_max(cls, type):
        """
        :param type: the EV_<*> event type
        :return: the maximum code for this type or ``None`` if the type is
                 invalid
        """
        if not isinstance(type, int):
            type = cls.event_to_value(type)
        m = cls._event_type_get_max(type)
        return m if m > -1 else None

    @classmethod
    def event_to_name(cls, event_type, event_code=None):
        """
        :param event_type: the numerical event type value
        :param event_code: optional, the numerical event code value
        :return: the event code name if a code is given otherwise the event
                 type name.

        This function is the equivalent to ``libevdev_event_code_get_name()``
        and ``libevdev_event_type_get_name()``
        """
        if event_code is not None:
            name = cls._event_code_get_name(event_type, event_code)
        else:
            name = cls._event_type_get_name(event_type)
        if not name:
            return None
        return name.decode("iso8859-1")

    @classmethod
    def event_to_value(cls, event_type, event_code=None):
        """
        :param event_type: the event type as string
        :param event_code: optional, the event code as string
        :return: the event code value if a code is given otherwise the event
                 type value.

        This function is the equivalent to ``libevdev_event_code_from_name()``
        and ``libevdev_event_type_from_name()``
        """
        if event_code is not None:
            if not isinstance(event_type, int):
                event_type = cls.event_to_value(event_type)
            v = cls._event_code_from_name(event_type, event_code.encode("iso8859-1"))
        else:
            v = cls._event_type_from_name(event_type.encode("iso8859-1"))
        if v == -1:
            return None
        return v

    def has_property(self, prop):
        """
        :param prop: a property, either as integer or string
        :return: True if the device has the property, False otherwise
        """
        if not isinstance(prop, int):
            prop = self.property_to_value(prop)
        r = self._has_property(self._ctx, prop)
        return bool(r)

    def has_event(self, event_type, event_code=None):
        """
        :param event_type: the event type, either as integer or as string
        :param event_code: optional, the event code, either as integer or as
                           string
        :return: True if the device has the type and/or code, False otherwise
        """
        if not isinstance(event_type, int):
            event_type = self.event_to_value(event_type)

        if event_code is None:
            r = self._has_event_type(self._ctx, event_type)
        else:
            if not isinstance(event_code, int):
                event_code = self.event_to_value(event_type, event_code)
            r = self._has_event_code(self._ctx, event_type, event_code)
        return bool(r)

    def _code(self, t, c):
        """
        Resolves a type+code tuple, either of which could be integer or
        string. Returns a (t, c) tuple in integers
        """
        if not isinstance(t, int):
            t = self.event_to_value(t)
        if c is not None and not isinstance(c, int):
            c = self.event_to_value(t, c)
        return (t, c)

    def event_value(self, event_type, event_code, new_value=None):
        """
        :param event_type: the event type, either as integer or as string
        :param event_code: the event code, either as integer or as string
        :param new_value: optional, the value to set to
        :return: the current value of type + code, or ``None`` if it doesn't
                 exist on this device
        """
        t, c = self._code(event_type, event_code)

        if not self.has_event(t, c):
            return None

        if new_value is not None:
            self._set_event_value(self._ctx, t, c, new_value)

        v = self._get_event_value(self._ctx, t, c)
        return v

    @property
    def num_slots(self):
        """
        :return: the number of slots on this device or ``None`` if this device
                 does not support slots

        :note: Read-only
        """
        s = self._get_num_slots(self._ctx)
        return s if s >= 0 else None

    @property
    def current_slot(self):
        """
        :return: the current of slots on this device or ``None`` if this device
                 does not support slots

        :note: Read-only
        """
        s = self._get_current_slot(self._ctx)
        return s if s >= 0 else None

    def slot_value(self, slot, event_code, new_value=None):
        """
        :param slot: the numeric slot number
        :param event_code: the ABS_<*> event code, either as integer or string
        :param new_value: optional, the value to set this slot to
        :return: the current value of the slot's code, or ``None`` if it doesn't
                 exist on this device
        """
        t, c = self._code("EV_ABS", event_code)

        if new_value is not None:
            self._set_slot_value(self._ctx, slot, c, new_value)

        v = self._get_slot_value(self._ctx, slot, c)
        return v

    def enable(self, event_type, event_code=None, data=None):
        """
        :param event_type: the event type, either as integer or as string
        :param event_code: optional, the event code, either as integer or as string
        :param data: if event_code is not ``None``, data points to the
                     code-specific information.

        If event_type is EV_ABS, then data must be a dictionary as returned
        from absinfo. Any keys missing are replaced with 0, i.e. the
        following example is valid and results in a fuzz/flat/resolution of
        zero::

                ctx = Libevdev()
                abs = { "minimum" : 0,
                        "maximum" : 100 }
                ctx.enable("EV_ABS", "ABS_X", data)

        If event_type is EV_REP, then data must be an integer.
        """
        t, c = self._code(event_type, event_code)
        if c is None:
            self._enable_event_type(self._ctx, t)
        else:
            if t == 0x03:  # EV_ABS
                data = _InputAbsinfo(data.get("value", 0),
                                     data.get("minimum", 0),
                                     data.get("maximum", 0),
                                     data.get("fuzz", 0),
                                     data.get("flat", 0),
                                     data.get("resolution", 0))
                data = ctypes.pointer(data)
            elif t == 0x14:  # EV_REP
                data = ctypes.pointer(c_int(data))
            self._enable_event_code(self._ctx, t, c, data)

    def disable(self, event_type, event_code=None):
        """
        :param event_type: the event type, either as integer or as string
        :param event_code: optional, the event code, either as integer or as string
        """
        t, c = self._code(event_type, event_code)
        if c is None:
            self._disable_event_type(self._ctx, t)
        else:
            self._disable_event_code(self._ctx, t, c)

    def enable_property(self, prop):
        """
        :param prop: the property as integer or string
        """
        if not isinstance(prop, int):
            prop = self.property_to_value(prop)

        self._enable_property(self._ctx, prop)

    def set_led(self, led, on):
        """
        :param led: the LED_<*> name
        :on: True to turn the LED on, False to turn it off
        """
        t, c = self._code("EV_LED", led)
        which = 3 if on else 4
        self._set_led_value(self._ctx, c, which)

    def next_event(self, flags=READ_FLAG_NORMAL):
        """
        :param flags: a set of libevdev read flags. May be omitted to use
                      the normal mode.
        :return: the next event or ``None`` if no event is available

        Event processing should look like this::

            fd = open("/dev/input/event0", "rb")
            ctx = libevdev.Libevdev(fd)
            ev = ctx.next_event()
            if ev is None:
                print("no event available right now")
            elif ev.matches("EV_SYN", "SYN_DROPPED"):
                sync_ev = ctx.next_event(libevdev.READ_FLAG_SYNC)
                while ev is not None:
                    print("First event in sync sequence")
                    sync_ev = ctx.next_event(libevdev.READ_FLAG_SYNC)
                print("sync complete")

        """
        ev = _InputEvent()
        rc = self._next_event(self._ctx, flags, ctypes.byref(ev))
        if rc == -errno.EAGAIN:
            return None

        return ev


class _UinputDevice(ctypes.Structure):
    pass


class UinputDevice(_LibraryWrapper):
    """
    This class provides a wrapper around the libevdev C library

    .. warning::

        Do not use this class directly
    """

    @staticmethod
    def _cdll():
        return ctypes.CDLL("libevdev.so.2", use_errno=True)

    _api_prototypes = {
        # int libevdev_uinput_create_from_device(const struct libevdev *, int, struct libevdev_uinput **)
        "libevdev_uinput_create_from_device": {
            "argtypes": (c_void_p, c_int, ctypes.POINTER(ctypes.POINTER(_UinputDevice))),
            "restype": c_int
        },
        # int libevdev_uinput_destroy(const struct libevdev *)
        "libevdev_uinput_destroy": {
            "argtypes": (c_void_p,),
            "restype": None,
        },
        # const char* libevdev_uinput_get_devnode(const struct libevdev *)
        "libevdev_uinput_get_devnode": {
            "argtypes": (c_void_p,),
            "restype": c_char_p,
        },
        # const char* libevdev_uinput_get_syspath(const struct libevdev *)
        "libevdev_uinput_get_syspath": {
            "argtypes": (c_void_p,),
            "restype": c_char_p,
        },
        # int libevdev_uinput_write_event(const struct libevdev *, uint, uint, int)
        "libevdev_uinput_write_event": {
            "argtypes": (c_void_p, c_uint, c_uint, c_int),
            "restype": c_int
        },
    }

    def __init__(self, source, fileobj=None):
        """
        Create a new uinput device based on the source libevdev device. The
        uinput device will mirror all capabilities from the source device.

        :param source: A libevdev device with all capabilities set.
        :param fileobj: A file-like object to the /dev/uinput node. If None,
        libevdev will open the device in managed mode. See the libevdev
        documentation for details.
        """
        super(UinputDevice, self).__init__()

        self._fileobj = fileobj
        if fileobj is None:
            fd = -2  # UINPUT_OPEN_MANAGED
        else:
            fd = fileobj.fileno()

        self._uinput_device = ctypes.POINTER(_UinputDevice)()
        rc = self._uinput_create_from_device(source._ctx, fd, ctypes.byref(self._uinput_device))
        if rc != 0:
            raise OSError(-rc, os.strerror(-rc))

    def __del__(self):
        if self._uinput_device is not None:
            self._uinput_destroy(self._uinput_device)

    @property
    def fd(self):
        """
        :return: the file-like object used in the constructor.
        """
        return self.fileobj

    def write_event(self, type, code, value):
        self._uinput_write_event(self._uinput_device, type, code, value)

    @property
    def devnode(self):
        """
        Return a string with the /dev/input/eventX device node
        """
        devnode = self._uinput_get_devnode(self._uinput_device)
        return devnode.decode("iso8859-1")

    @property
    def syspath(self):
        """
        Return a string with the /dev/input/eventX device node
        """
        syspath = self._uinput_get_syspath(self._uinput_device)
        return syspath.decode("iso8859-1")
