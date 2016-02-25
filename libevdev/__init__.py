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
            # default name is the libevdev name minus the libevdev_ prefix
            pyname = dict.get_default(attrs, "name", name[len("libevdev_")])
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
            "restype": c_char_p
            },
        #int libevdev_property_from_name(const char *name);
        "libevdev_property_from_name": {
            "argtypes": (c_char_p,),
            "restype": c_int
            },
        }
