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

import unittest

import libevdev
from libevdev import evbit, propbit

class TestEventBits(unittest.TestCase):
    def test_ev_types(self):
        self.assertIn(libevdev.EV_SYN, libevdev.types)
        self.assertIn(libevdev.EV_REL, libevdev.types)
        self.assertIn(libevdev.EV_ABS, libevdev.types)
        self.assertEqual(len(libevdev.types), 13)

    def test_EV_REL(self):
        self.assertIn(libevdev.EV_REL.REL_X, libevdev.EV_REL.codes)
        self.assertIn(libevdev.EV_REL.REL_Y, libevdev.EV_REL.codes)
        self.assertNotIn(libevdev.EV_ABS.ABS_X, libevdev.EV_REL.codes)

    def test_type_max(self):
        self.assertEqual(libevdev.EV_REL.max, libevdev.EV_REL.REL_MAX.value)
        self.assertEqual(libevdev.EV_ABS.max, libevdev.EV_ABS.ABS_MAX.value)
        self.assertEqual(libevdev.EV_KEY.max, libevdev.EV_KEY.KEY_MAX.value)

        self.assertEqual(libevdev.EV_REL.max, 0x0f)
        self.assertEqual(libevdev.EV_ABS.max, 0x3f)
        self.assertEqual(libevdev.EV_KEY.max, 0x2ff)

    def test_evcode_compare(self):
        self.assertNotEqual(libevdev.EV_REL.REL_X, libevdev.EV_REL.REL_Y)
        self.assertNotEqual(libevdev.EV_REL.REL_X, libevdev.EV_ABS.ABS_X)
        self.assertNotEqual(libevdev.EV_REL, libevdev.EV_ABS)

        self.assertNotEqual(libevdev.EV_REL.REL_X, libevdev.EV_REL)
        self.assertNotEqual(libevdev.EV_ABS.ABS_X, libevdev.EV_ABS)

    def test_evbit(self):
        self.assertEqual(evbit(0, 0), libevdev.EV_SYN.SYN_REPORT)
        self.assertEqual(evbit(1, 30), libevdev.EV_KEY.KEY_A)
        self.assertEqual(evbit(2, 1), libevdev.EV_REL.REL_Y)

        self.assertEqual(evbit(0), libevdev.EV_SYN)
        self.assertEqual(evbit(1), libevdev.EV_KEY)
        self.assertEqual(evbit(2), libevdev.EV_REL)

        for t in libevdev.types:
            self.assertEqual(evbit(t.value), t)

    def test_propbit(self):
        self.assertEqual(propbit(0), libevdev.INPUT_PROP_POINTER)
        self.assertEqual(propbit(1), libevdev.INPUT_PROP_DIRECT)

        for p in libevdev.props:
            self.assertEqual(propbit(p.value), p)

    def test_evbit_string(self):
        self.assertEqual(evbit('EV_SYN'), libevdev.EV_SYN)
        self.assertEqual(evbit('EV_KEY'), libevdev.EV_KEY)
        self.assertEqual(evbit('EV_REL'), libevdev.EV_REL)
        self.assertEqual(evbit('EV_REP'), libevdev.EV_REP)

        for t in libevdev.types:
            self.assertEqual(evbit(t.name), t)

    def test_evcode_string(self):
        self.assertEqual(evbit('ABS_X'), libevdev.EV_ABS.ABS_X)
        self.assertEqual(evbit('REL_X'), libevdev.EV_REL.REL_X)
        self.assertEqual(evbit('SYN_REPORT'), libevdev.EV_SYN.SYN_REPORT)
        self.assertEqual(evbit('REP_PERIOD'), libevdev.EV_REP.REP_PERIOD)

    def test_propbit_string(self):
        self.assertEqual(propbit('INPUT_PROP_POINTER'), libevdev.INPUT_PROP_POINTER)
        self.assertEqual(propbit('INPUT_PROP_DIRECT'), libevdev.INPUT_PROP_DIRECT)

        for p in libevdev.props:
            self.assertEqual(propbit(p.value), p)
