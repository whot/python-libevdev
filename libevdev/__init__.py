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
            "restype": None,
            },
        ###############################
        # Custom getters and setters  #
        ###############################
        #int libevdev_get_id_bustype(struct libevdev *)
        "libevdev_get_id_bustype": {
            "argtypes": (c_void_p,),
            "restype": int,
            },
        #int libevdev_get_id_vendor(struct libevdev *)
        "libevdev_get_id_vendor": {
            "argtypes": (c_void_p,),
            "restype": int,
            },
        #int libevdev_get_id_product(struct libevdev *)
        "libevdev_get_id_product": {
            "argtypes": (c_void_p,),
            "restype": int,
            },
        #int libevdev_get_id_version(struct libevdev *)
        "libevdev_get_id_version": {
            "argtypes": (c_void_p,),
            "restype": int,
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
        return self._get_name(self._ctx)

    @name.setter
    def name(self, name):
        return self._set_name(self._ctx, name)

    @property
    def phys(self):
        """
        A string with the device's kernel phys.
        """
        return self._get_phys(self._ctx)

    @phys.setter
    def phys(self, phys):
        return self._set_phys(self._ctx, phys)

    @property
    def uniq(self):
        """
        A string with the device's kernel uniq.
        """
        return self._get_uniq(self._ctx)

    @uniq.setter
    def uniq(self, uniq):
        return self._set_uniq(self._ctx, uniq)

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
        if vals.has_key("bustype"):
            self._set_id_bustype(self._ctx, vals["bustype"])
        if vals.has_key("vendor"):
            self._set_id_vendor(self._ctx, vals["vendor"])
        if vals.has_key("product"):
            self._set_id_product(self._ctx, vals["product"])
        if vals.has_key("version"):
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
