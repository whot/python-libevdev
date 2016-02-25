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
            #   "name" : "foo", # override default name taken from libevdev
            # If a type is specified, it can be:
            #   "getter" ... automatically makes the function an attribute
            #   "setter" ... automatically makes the function setable attribute
            #   "type" : <type>
            # }
    }

    # List of all API calls starting with libevdev_get_. These are mapped
    # into attributes (see __getattr__), libevdev_get_name becomes
    # foo = Libevdev().name
    _getters = {
            # name : func
    }

    # List of all API calls starting with libevdev_set_. These are mapped
    # into attributes (see __setattr__), libevdev_set_name becomes
    # foo = Libevdev()
    # foo.name = somename
    _setters = {
            # name : func
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
            # getters and setters have special treatment
            # http://stackoverflow.com/questions/412951/how-to-implement-property-with-dynamic-name-in-python
            t = attrs.get("type", None)
            if t == "getter":
                pyname = name.split("libevdev_get_")[1]
                cls._getters[pyname] = func
            elif t == "setter":
                pyname = name.split("libevdev_set_")[1]
                cls._setters[pyname] = func
            else:
                # default name is the libevdev name minus the libevdev_ prefix
                pyname = dict.get(attrs, "name", name[len("libevdev_"):])
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
            "name" : "_new",
            },
        #struct libevdev *libevdev_free(struct libevdev *);
        "libevdev_free": {
            "argtypes": (c_void_p,),
            "restype": None,
            "name" : "_free",
            },
        #const char * libevdev_get_name(struct libevdev *);
        "libevdev_get_name": {
            "argtypes": (c_void_p,),
            "restype": c_char_p,
            "type" : "getter",
            },
        #void libevdev_set_name(struct libevdev *, const char*);
        "libevdev_set_name": {
            "argtypes": (c_void_p, c_char_p),
            "restype": None,
            "type" : "setter",
            },
        #const char * libevdev_get_phys(struct libevdev *);
        "libevdev_get_phys": {
            "argtypes": (c_void_p,),
            "restype": c_char_p,
            "type" : "getter",
            },
        #void libevdev_set_phys(struct libevdev *, const char*);
        "libevdev_set_phys": {
            "argtypes": (c_void_p, c_char_p),
            "restype": None,
            "type" : "setter",
            },
        #const char * libevdev_get_uniq(struct libevdev *);
        "libevdev_get_uniq": {
            "argtypes": (c_void_p,),
            "restype": c_char_p,
            "type" : "getter",
            },
        #void libevdev_set_uniq(struct libevdev *, const char*);
        "libevdev_set_uniq": {
            "argtypes": (c_void_p, c_char_p),
            "restype": None,
            "type" : "setter",
            },
        #int libevdev_get_driver_version(struct libevdev *);
        "libevdev_get_driver_version": {
            "argtypes": (c_void_p, ),
            "restype": c_int,
            "type" : "getter",
            },
        #void libevdev_set_clock_id(struct libevdev *, int)
        "libevdev_set_clock_id": {
            "argtypes": (c_void_p, c_int),
            "restype": None,
            "type" : "setter",
            },
        }

    def __init__(self):
        super(Libevdev, self).__init__()
        self._ctx = self._new()

    def __del__(self):
        if hasattr(self, "_ctx"):
            self._free(self._ctx)

    def __getattr__(self, name):
        try:
            return self._getters[name](self._ctx)
        except KeyError:
            msg = "'{0}' object has no attribute '{1}'"
            raise AttributeError(msg.format(type(self).__name__, name))

    def __setattr__(self, name, value):
        # Try calling the setter function first if we have any. If that
        # fails, call into the base class, this magically calls our actual
        # @property hooks or just assigns the attribute as a normal
        # self.foo = bar would. See __setattr__ documentation.
        try:
            self._setters[name](self._ctx, value)
        except KeyError:
            _LibraryWrapper.__setattr__(self, name, value)
