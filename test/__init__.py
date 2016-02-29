import unittest
import ctypes
from libevdev import *

# Note: these tests test for the correct functioning of the python bindings,
# not of libevdev underneath. Some ranges are hardcoded for simplicity, e.g.
# if properties 1-4 work the others will work too if libevdev works
# correctly

class TestNameConversion(unittest.TestCase):
    def test_prop_name(self):
        name = Libevdev.property_to_name(0)
        self.assertEqual(name, "INPUT_PROP_POINTER")

        prevname = None
        for i in range(0, 5):
            name = Libevdev.property_to_name(i)
            self.assertIsNotNone(name)
            self.assertTrue(name.startswith("INPUT_PROP_"))
            self.assertNotEqual(prevname, name)
            prevname = name

    def test_prop_to_name_invalid(self):
        name = Libevdev.property_to_name(-1)
        self.assertIsNone(name)
        name = Libevdev.property_to_name(100)
        self.assertIsNone(name)
        with self.assertRaises(ctypes.ArgumentError):
            name = Libevdev.property_to_name("foo")

    def test_type_to_name(self):
        name = Libevdev.event_to_name(1)
        self.assertEqual(name, "EV_KEY")

        prevname = None
        for i in range(0, 5):
            name = Libevdev.event_to_name(i)
            self.assertIsNotNone(name)
            self.assertTrue(name.startswith("EV_"))
            self.assertNotEqual(prevname, name)
            prename = name

    def test_type_to_name_invalid(self):
        name = Libevdev.event_to_name(-1)
        self.assertIsNone(name)
        name = Libevdev.event_to_name(100)
        self.assertIsNone(name)
        with self.assertRaises(ctypes.ArgumentError):
            name = Libevdev.event_to_name("foo")

    def test_code_to_name(self):
        name = Libevdev.event_to_name(0, 0)
        self.assertEqual(name, "SYN_REPORT")

        name = Libevdev.event_to_name(1, 1)
        self.assertEqual(name, "KEY_ESC")

    def test_code_to_name_invalid(self):
        name = Libevdev.event_to_name(0, 1000)
        self.assertIsNone(name)
        name = Libevdev.event_to_name(0, -1)
        self.assertIsNone(name)
        with self.assertRaises(ctypes.ArgumentError):
            name = Libevdev.event_to_name(0, "foo")

    def test_type_to_value(self):
        v = Libevdev.event_to_value("EV_REL")
        self.assertEqual(v, 2)

    def test_type_value_invalid(self):
        v = Libevdev.event_to_value("foo")
        self.assertIsNone(v)
        with self.assertRaises(AttributeError):
            v = Libevdev.event_to_value(0)

    def test_code_value(self):
        v = Libevdev.event_to_value("EV_REL", "REL_Y")
        self.assertEqual(v, 1)

        v = Libevdev.event_to_value(0, "SYN_DROPPED")
        self.assertEqual(v, 3)

    def test_code_value_invalid(self):
        v = Libevdev.event_to_value("EV_REL", "KEY_ESC")
        self.assertIsNone(v)


class TestLibevdevDevice(unittest.TestCase):
    def test_ctx_init(self):
        l = Libevdev()
        del l

    def test_set_get_name(self):
        l = Libevdev()
        name = l.name
        self.assertEqual(name, '')

        l.name = "foo"
        name = l.name
        self.assertEqual(name, "foo")

        l.name = None
        name = l.name
        self.assertEqual(name, "")

    def test_set_get_uniq(self):
        l = Libevdev()
        uniq = l.uniq
        self.assertIsNone(uniq)

        l.uniq = "foo"
        uniq = l.uniq
        self.assertEqual(uniq, "foo")

        # libevdev issue: phys may be NULL (unlike the name) but we can't
        # set it to NULL. But the conversion code returns None for the empty
        # string, so let's test for that
        l.uniq = None
        uniq = l.uniq
        self.assertEqual(uniq, None)

    def test_set_get_phys(self):
        l = Libevdev()
        phys = l.phys
        self.assertIsNone(phys)

        l.phys = "foo"
        phys = l.phys
        self.assertEqual(phys, "foo")

        # libevdev issue: phys may be NULL (unlike the name) but we can't
        # set it to NULL. But the conversion code returns None for the empty
        # string, so let's test for that
        l.phys = None
        phys = l.phys
        self.assertEqual(phys, None)

    def test_get_driver_version(self):
        l = Libevdev()
        v = l.driver_version
        self.assertEqual(v, 0)
        # we can't set this, nothing else we can test

    def test_set_get_id(self):
        l = Libevdev()
        id = l.id
        self.assertEqual(id["bustype"], 0)
        self.assertEqual(id["vendor"], 0)
        self.assertEqual(id["product"], 0)
        self.assertEqual(id["version"], 0)

        id["bustype"] = 1
        id["vendor"] = 2
        id["product"] = 3
        id["version"] = 4

        l.id = id
        id = l.id
        self.assertEqual(id["bustype"], 1)
        self.assertEqual(id["vendor"], 2)
        self.assertEqual(id["product"], 3)
        self.assertEqual(id["version"], 4)

        del id["bustype"]
        del id["vendor"]
        del id["product"]
        id["version"] = 5

        l.id = id
        id = l.id
        self.assertEqual(id["bustype"], 1)
        self.assertEqual(id["vendor"], 2)
        self.assertEqual(id["product"], 3)
        self.assertEqual(id["version"], 5)

class TestRealDevice(unittest.TestCase):
    """
    Tests various things against /dev/input/event3 which is usually the
    keyboard. Requires root rights though.
    """
    def setUp(self):
        self.fd = open("/dev/input/event3", "rb")

    def tearDown(self):
        self.fd.close()

    def test_set_fd(self):
        l = Libevdev()
        l.fd = self.fd
        fd = l.fd
        self.assertEqual(self.fd, fd)

        fd2 = open("/dev/input/event3", "rb")
        l.fd = fd2
        fd = l.fd
        self.assertEqual(fd, fd2)
        fd2.close()

    def test_init_fd(self):
        l = Libevdev(self.fd)
        fd = l.fd
        self.assertEqual(self.fd, fd)

        fd2 = open("/dev/input/event3", "rb")
        l.fd = fd2
        fd = l.fd
        self.assertEqual(fd, fd2)
        fd2.close()

    def test_ids(self):
        l = Libevdev(self.fd)
        id = l.id
        self.assertNotEqual(id["bustype"], 0)
        self.assertNotEqual(id["vendor"], 0)
        self.assertNotEqual(id["product"], 0)
        self.assertNotEqual(id["version"], 0)

    def test_name(self):
        l = Libevdev(self.fd)
        name = l.name
        self.assertNotEqual(name, "")

    def test_driver_version(self):
        l = Libevdev(self.fd)
        v = l.driver_version
        self.assertEqual(v, 0x010001)

    def test_set_clock_id(self):
        l = Libevdev(self.fd)
        try:
            import time
            clock = time.CLOCK_MONOTONIC
        except AttributeError:
            clock = 1
        rc = l.set_clock_id(clock)
        self.assertEqual(rc, 0)

    def test_grab(self):
        l = Libevdev(self.fd)
        rc = l.grab()
        self.assertEqual(rc, 0)

        rc = l.grab(False)
        self.assertEqual(rc, 0)

        rc = l.grab(True)
        self.assertEqual(rc, 0)

    def test_has_event(self):
        l = Libevdev(self.fd)
        self.assertTrue(l.has_event("EV_SYN", "SYN_REPORT"))

        type_supported = -1
        for i in range(1, 5):
            if l.has_event(i):
                type_supported = i
                break;

        self.assertGreater(type_supported, 0)

        codes_supported = 0
        for i in range(0, 150):
            if l.has_event(type_supported, i):
                codes_supported += 1

        self.assertGreater(codes_supported, 0)

    def test_has_property(self):
        """
        Let's assume at least one between event0 and event10 is a device
        with at least one property set. May cause false negatives.
        """

        props_supported = 0
        for i in range(0, 10):
            try:
                with open("/dev/input/event{}".format(i), "rb") as fd:
                    l = Libevdev(fd)

                    for p in range(0, 6):
                        if l.has_property(p):
                            props_supported += 1
            except IOError:
                # Not all eventX nodes are guaranteed to exist
                pass
        self.assertGreater(props_supported, 0)

class TestAbsDevice(unittest.TestCase):
    """
    Tests various things against the first device with EV_ABS.
    We're relying on that this device has ABS_Y, this tests against a code
    that's nonzero and is the most common ABS anyway.
    Requires root rights.
    """
    def setUp(self):
        want_fd = None
        for i in range(0, 20):
            try:
                fd = open("/dev/input/event{}".format(i), "rb")
                l = Libevdev(fd)
                if l.has_event("EV_ABS", "ABS_Y"):
                    want_fd = fd
                    break
                fd.close()
            except IOError:
                # Not all eventX nodes are guaranteed to exist
                pass

        self.assertIsNotNone(want_fd)
        self.fd = want_fd

    def tearDown(self):
        self.fd.close()

    def test_absinfo(self):
        l = Libevdev(self.fd)
        a = l.absinfo("ABS_Y")
        self.assertTrue("minimum" in a)
        self.assertTrue("maximum" in a)
        self.assertTrue("resolution" in a)
        self.assertTrue("fuzz" in a)
        self.assertTrue("flat" in a)
        self.assertTrue("value" in a)

    def test_set_absinfo(self):
        l = Libevdev(self.fd)
        real_a = l.absinfo("ABS_Y")
        a = l.absinfo("ABS_Y")
        a["minimum"] = 100
        a["maximum"] = 200
        a["fuzz"] = 300
        a["flat"] = 400
        a["resolution"] = 500
        a["value"] = 600

        a = l.absinfo("ABS_Y", new_values=a)
        self.assertEqual(a["minimum"], 100)
        self.assertEqual(a["maximum"], 200)
        self.assertEqual(a["fuzz"], 300)
        self.assertEqual(a["flat"], 400)
        self.assertEqual(a["resolution"], 500)
        self.assertEqual(a["value"], 600)

        l2 = Libevdev(self.fd)
        a2 = l2.absinfo("ABS_Y")
        self.assertNotEqual(a["minimum"], real_a["minimum"])
        self.assertNotEqual(a["maximum"], real_a["maximum"])
        self.assertNotEqual(a["fuzz"], real_a["fuzz"])
        self.assertNotEqual(a["flat"], real_a["flat"])
        self.assertNotEqual(a["resolution"], real_a["resolution"])
        self.assertEqual(a2["value"], real_a["value"])
        self.assertEqual(a2["minimum"], real_a["minimum"])
        self.assertEqual(a2["maximum"], real_a["maximum"])
        self.assertEqual(a2["fuzz"], real_a["fuzz"])
        self.assertEqual(a2["flat"], real_a["flat"])
        self.assertEqual(a2["resolution"], real_a["resolution"])
        self.assertEqual(a2["value"], real_a["value"])

    def test_set_absinfo_kernel(self):
        # FIXME: yeah, nah, not testing that on a random device...
        pass

    def test_get_set_event_value(self):
        l = Libevdev(self.fd)
        v = l.event_value("EV_ABS", "ABS_Y")
        self.assertIsNotNone(v)
        v = l.event_value(0x03, 0x01, new_value=300)
        self.assertEqual(v, 300)
        v = l.event_value(0x03, 0x01)
        self.assertEqual(v, 300)

    def test_get_set_event_value_invalid(self):
        l = Libevdev(self.fd)
        v = l.event_value("EV_ABS", 0x600)
        self.assertIsNone(v)
        v = l.event_value(0x03, 0x600, new_value=300)
        self.assertIsNone(v)

if __name__ == '__main__':
    unittest.main()

