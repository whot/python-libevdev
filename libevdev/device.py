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

import libevdev

class Device(object):
    """
    This class represents an evdev device backed by libevdev.

    The device may represent a real device in the system or a constructed
    device where the caller supplies all properties of the device.
    """

    def __init__(self, fd=None):
        """
        :param fd: A file-like object

        Create a new libevdev device. If a file is given, the device
        initializes from that file, otherwise the device is uninitialized
        and needs to be set up by the caller. ::

                fd = open("/dev/input/event0", "rb")
                l = libevdev.Device(fd)
                # l now represents the device on event0

                l2 = libevdev.Device()
                l2.name = "test device"
                l2.enable("EV_REL", "REL_X")
                # l2 is an unbound device with the REL_X bit set

        """
        self._libevdev = libevdev.Libevdev(fd)

    @property
    def name(self):
        """
        :return: the device name
        """
        return self._libevdev.name

    @name.setter
    def name(self, name):
        self._libevdev.name = name

    @property
    def phys(self):
        """
        :return: the device's kernel phys or None.
        """
        return self._libevdev.phys

    @phys.setter
    def phys(self, phys):
        self._libevdev.phys = phys

    @property
    def uniq(self):
        """
        :return: the device's uniq string or None
        """
        return self._libevdev.uniq

    @uniq.setter
    def uniq(self, uniq):
        self._libevdev.uniq = uniq

    @property
    def driver_version(self):
        """
        :return: the device's driver version
        """
        return self._libevdev.driver_version

