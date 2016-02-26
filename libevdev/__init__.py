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

import ctypes
from ctypes import c_char_p, c_int, c_uint, c_void_p, c_long, c_int32, c_uint16

class _InputAbsinfo(ctypes.Structure):
    _fields_ = [("value", c_int32),
                ("minimum", c_int32),
                ("maximum", c_int32),
                ("fuzz", c_int32),
                ("flat", c_int32),
                ("resolution", c_int32)]

class _LibraryWrapper(object):
    """
    Base class for wrapping a shared library. Do not use directly.
    """
    _lib = None # The shared library, shared between instances of the class

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
    The API is modelled closely after the C API, use the C library
    documentation for details on the API.
    https://www.freedesktop.org/software/libevdev/doc/latest/
    """

    @staticmethod
    def _cdll():
        return ctypes.CDLL("libevdev.so.2", use_errno=True)

    _api_prototypes = {
        #const char *libevdev_event_type_get_name(unsigned int type);
        "libevdev_event_type_get_name": {
            "argtypes": (c_uint,),
            "restype": c_char_p
            },
        #int libevdev_event_type_from_name(const char *name);
        "libevdev_event_type_from_name": {
            "argtypes": (c_char_p,),
            "restype": c_int
            },
        #const char *libevdev_event_code_get_name(unsigned int type, unsigned int code);
        "libevdev_event_code_get_name": {
            "argtypes": (c_uint, c_uint,),
            "restype": c_char_p
            },
        #int libevdev_event_code_from_name(unsigned int type, const char *name);
        "libevdev_event_code_from_name": {
            "argtypes": (c_uint, c_char_p,),
            "restype": c_int
            },
        #const char *libevdev_property_get_name(unsigned int prop);
        "libevdev_property_get_name": {
            "argtypes": (c_uint,),
            "restype": c_char_p,
            },
        #int libevdev_property_from_name(const char *name);
        "libevdev_property_from_name": {
            "argtypes": (c_char_p,),
            "restype": c_int
            },
        #struct libevdev *libevdev_new(void);
        "libevdev_new": {
            "argtypes": (),
            "restype": c_void_p,
            },
        #struct libevdev *libevdev_free(struct libevdev *);
        "libevdev_free": {
            "argtypes": (c_void_p,),
            "restype": None,
            },
        ###############################
        # Simple getters and setters  #
        ###############################
        #const char * libevdev_get_name(struct libevdev *);
        "libevdev_get_name": {
            "argtypes": (c_void_p,),
            "restype": c_char_p,
            },
        #void libevdev_set_name(struct libevdev *, const char*);
        "libevdev_set_name": {
            "argtypes": (c_void_p, c_char_p),
            "restype": None,
            },
        #const char * libevdev_get_phys(struct libevdev *);
        "libevdev_get_phys": {
            "argtypes": (c_void_p,),
            "restype": c_char_p,
            },
        #void libevdev_set_phys(struct libevdev *, const char*);
        "libevdev_set_phys": {
            "argtypes": (c_void_p, c_char_p),
            "restype": None,
            },
        #const char * libevdev_get_uniq(struct libevdev *);
        "libevdev_get_uniq": {
            "argtypes": (c_void_p,),
            "restype": c_char_p,
            },
        #void libevdev_set_uniq(struct libevdev *, const char*);
        "libevdev_set_uniq": {
            "argtypes": (c_void_p, c_char_p),
            "restype": None,
            },
        #int libevdev_get_driver_version(struct libevdev *);
        "libevdev_get_driver_version": {
            "argtypes": (c_void_p, ),
            "restype": c_int,
            },
        #void libevdev_set_clock_id(struct libevdev *, int)
        "libevdev_set_clock_id": {
            "argtypes": (c_void_p, c_int),
            "restype": c_int,
            },
        ###############################
        # Custom getters and setters  #
        ###############################
        #int libevdev_get_id_bustype(struct libevdev *)
        "libevdev_get_id_bustype": {
            "argtypes": (c_void_p,),
            "restype": c_int,
            },
        #int libevdev_get_id_vendor(struct libevdev *)
        "libevdev_get_id_vendor": {
            "argtypes": (c_void_p,),
            "restype": c_int,
            },
        #int libevdev_get_id_product(struct libevdev *)
        "libevdev_get_id_product": {
            "argtypes": (c_void_p,),
            "restype": c_int,
            },
        #int libevdev_get_id_version(struct libevdev *)
        "libevdev_get_id_version": {
            "argtypes": (c_void_p,),
            "restype": c_int,
            },
        #void libevdev_set_id_bustype(struct libevdev *, int)
        "libevdev_set_id_bustype": {
            "argtypes": (c_void_p, c_int),
            "restype": None,
            },
        #void libevdev_set_id_vendor(struct libevdev *, int)
        "libevdev_set_id_vendor": {
            "argtypes": (c_void_p, c_int),
            "restype": None,
            },
        #void libevdev_set_id_product(struct libevdev *, int)
        "libevdev_set_id_product": {
            "argtypes": (c_void_p, c_int),
            "restype": None,
            },
        #void libevdev_set_id_version(struct libevdev *, int)
        "libevdev_set_id_version": {
            "argtypes": (c_void_p, c_int),
            "restype": None,
            },
        # int libevdev_set_fd(struct libevdev *, int)
        "libevdev_set_fd" : {
            "argtypes" : (c_void_p, c_int),
            "restype" : c_int,
        },
        # int libevdev_change_fd(struct libevdev *, int)
        "libevdev_change_fd" : {
            "argtypes" : (c_void_p, c_int),
            "restype" : c_int,
        },
        # int libevdev_get_fd(struct libevdev *)
        "libevdev_get_fd" : {
            "argtypes" : (c_void_p, ),
            "restype" : c_int,
        },
        # int libevdev_grab(struct libevdev *)
        "libevdev_grab": {
            "argtypes" : (c_void_p, c_int),
            "restype" : c_int,
        },
        # const struct input_absinfo *libevdev_get_abs_info(struct libevdev*,  int code)
        "libevdev_get_abs_info" : {
            "argtypes" : (c_void_p, c_int),
            "restype" : ctypes.POINTER(_InputAbsinfo),
        },
        # We don't need to wrap libevdev_set_abs_info(), we get the same
        # using get_abs_info and overwrite the values.
        #
        # const struct input_absinfo *libevdev_get_abs_info(struct libevdev*,  int code)
        "libevdev_kernel_set_abs_info" : {
            "argtypes" : (c_void_p, ctypes.POINTER(_InputAbsinfo)),
            "restype" : (c_int)
        },
        ##########################
        # Various has_ functions #
        ##########################
        "libevdev_has_property" : {
            "argtypes" : (c_void_p, c_int),
            "restype" : (c_int)
        },
        "libevdev_has_event_type" : {
            "argtypes" : (c_void_p, c_int),
            "restype" : (c_int)
        },
        "libevdev_has_event_code" : {
            "argtypes" : (c_void_p, c_int, c_int),
            "restype" : (c_int)
        },
        }

    def __init__(self, fd=None):
        """
        :param fd: A file-like object

        Create a new libevdev instance. If a file is given this call is
        equivalent to ``libevdev_new_from_fd()``, otherwise it is equivalent
        to ``libevdev_new()``.
        """
        super(Libevdev, self).__init__()
        self._ctx = self._new()
        self._file = None
        if fd != None:
            self.fd = fd

    def __del__(self):
        if hasattr(self, "_ctx"):
            self._free(self._ctx)

    @property
    def name(self):
        """
        A string with the device's kernel name.
        """
        return self._get_name(self._ctx).decode("iso8859-1")

    @name.setter
    def name(self, name):
        if name == None:
            name = ''
        return self._set_name(self._ctx, name.encode("iso8859-1"))

    @property
    def phys(self):
        """
        A string with the device's kernel phys.
        """
        phys = self._get_phys(self._ctx)
        if not phys:
            return None
        return phys.decode("iso8859-1")

    @phys.setter
    def phys(self, phys):
        # libevdev issue: phys may be NULL, but can't be set to NULL
        if phys == None:
            phys = ''
        return self._set_phys(self._ctx, phys.encode("iso8859-1"))

    @property
    def uniq(self):
        """
        A string with the device's kernel uniq.
        """
        uniq = self._get_uniq(self._ctx)
        if not uniq:
            return None
        return uniq.decode("iso8859-1")

    @uniq.setter
    def uniq(self, uniq):
        # libevdev issue: uniq may be NULL, but can't be set to NULL
        if uniq == None:
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
        A dict with the keys 'bustype', 'vendor', 'product', 'version'.
        When used as a setter, only existing keys are applied to the device.

        This is a combined version of the libevdev calls
        ``libevdev_get_id_busytype()``, ``libevdev_get_id_vendor()``,
        ``libevdev_get_id_product()``, ``libevdev_get_id_version()`` and the
        respective setters.

        """
        bus = self._get_id_bustype(self._ctx)
        vdr = self._get_id_vendor(self._ctx)
        pro = self._get_id_product(self._ctx)
        ver = self._get_id_version(self._ctx)
        return { "bustype" : bus,
                 "vendor" : vdr,
                 "product" : pro,
                 "version" : ver }
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
        The file-like object used during constructor or in the most recent
        assignment to self.fd.

        When assigned the first time and no file has been passed to the
        constructor, the assignment is equivalent to ``libevdev_set_fd()``.

        Subsequently, any assignments are equivalent to
        ``libevdev_change_fd``.

        :note: libevdev uses the fileno() of the object.
        """
        return self._file

    @fd.setter
    def fd(self, fileobj):
        fd = fileobj.fileno()
        if self._file == None:
            r = self._set_fd(self._ctx, fd)
        else:
            r = self._change_fd(self._ctx, fd)

        if r != 0:
            print("FIXME: this should be an exception")

        # sanity check:
        if self._get_fd(self._ctx) != fd:
            print("FIXME: fileno() != get_fd()")

        self._file = fileobj

    def grab(self, enable_grab = True):
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
        return r

    def absinfo(self, code, new_values=None, kernel=False):
        """
        :param new_values: a dict with the same keys as the return values.
        :param kernel: If true, assigning new values corresponds to ``libevdev_kernel_set_abs_info``
        :return: a dictionary with the keys "value", "min", "max",
                 "resolution", "fuzz", "flat"; ``None`` if the code does not exist on
                 this device

        :note: The returned value is a copy of the value returned by
               libevdev. Changing a value in the dictionary does not change the
               matching property. To change the device, reassign the
               dictionary to the absinfo code.
               This is different to the libevdev behavior.
        """
        absinfo = self._get_abs_info(self._ctx, code)
        if new_values != None:
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
                self._kernel_set_abs_info(self._ctx, absinfo)

        if not absinfo:
            return None

        return { "value" : absinfo.contents.value,
                 "minimum" : absinfo.contents.minimum,
                 "maximum" : absinfo.contents.maximum,
                 "fuzz" : absinfo.contents.fuzz,
                 "flat" : absinfo.contents.flat,
                 "flat" : absinfo.contents.resolution }

    def property_name(self, prop):
        """
        :param prop: the numerical property value
        :returns: A string with the property name or None

        This function is the equivalent to ``libevdev_property_get_name()``
        """
        name = self._property_get_name(prop)
        if not name:
            return None
        return name.decode("iso8859-1")

    def property_value(self, prop):
        """
        :param prop: the property name as string
        :returns: The numerical property value or None

        This function is the equivalent to ``libevdev_property_from_name()``
        """
        v = self._property_from_name(prop)
        if v == -1:
            return None
        return v

    def event_name(self, event_type, event_code=None):
        """
        :param event_type: the numerical event type value
        :param event_code: optional, the numerical event code value
        :return: the event code name if a code is given otherwise the event
                 type name.

        This function is the equivalent to ``libevdev_event_code_get_name()``
        and ``libevdev_event_type_get_name()``
        """
        if event_code != None:
            name = self._event_code_get_name(event_type, event_code)
        else:
            name = self._event_type_get_name(event_type)
        if not name:
            return None
        return name.decode("iso8859-1")

    def event_value(self, event_type, event_code=None):
        """
        :param event_type: the event type as string
        :param event_code: optional, the event code as string
        :return: the event code value if a code is given otherwise the event
                 type value.

        This function is the equivalent to ``libevdev_event_code_from_name()``
        and ``libevdev_event_type_from_name()``
        """
        if event_code != None:
            if not isinstance(event_type, int):
                event_type = self.event_value(event_type)
            v = self._event_code_from_name(event_type, event_code.encode("iso8859-1"))
        else:
            v = self._event_type_from_name(event_type.encode("iso8859-1"))
        if v == -1:
            return None
        return v

    def has_property(self, prop):
        """
        :param prop: a property, either as integer or string
        :return: True if the device has the property, False otherwise
        """
        if not isinstance(prop, int):
            prop = self.property_value(prop)
        r = self._has_property(self._ctx, prop)
        return bool(r)

    def has_event(self, event_type,  event_code=None):
        """
        :param event_type: the event type, either as integer or as string
        :param event_code: optional, the event code, either as integer or as
                           string
        :return: True if the device has the type and/or code, False otherwise
        """
        if not isinstance(event_type, int):
            event_type = self.event_value(event_type)

        if event_code == None:
            r = self._has_event_type(self._ctx, event_type)
        else:
            if not isinstance(event_code, int):
                event_code = self.event_value(event_type, event_code)
            r = self._has_event_code(self._ctx, event_type, event_code)
        return bool(r)
