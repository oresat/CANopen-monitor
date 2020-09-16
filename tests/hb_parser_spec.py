import unittest

from canopen_monitor.parser.hb import *


class TestHB(unittest.TestCase):
    """
    Tests for the Heartbeat parser
    """

    def test_HB(self):
        """
        Test Heartbeat Message
        """
        hb_message = b'\x04'
        self.assertEqual("Heartbeat - Stopped",
                         parse(hb_message),
                         "Error on heartbeat Message parse")

    def test_HB_Invalid(self):
        """
        Test Heartbeat Message with an invalid payload
        """
        hb_message = b'\xFF'
        with self.assertRaises(ValueError):
            parse(hb_message)


if __name__ == '__main__':
    unittest.main()
