import unittest

from canopen_monitor.parser.time import *


class TestTIME(unittest.TestCase):
    """
    Tests for the TIME parser
    """

    def test_TIME(self):
        """
        Test TIME Message
        """
        time_message = b'\x02\x97\xC1\xE1\x34\x59'
        self.assertEqual("Time - 09/09/2020 12:05:00.001000",
                         parse(time_message),
                         "Error on heartbeat Message parse")

    def test_TIME_empty(self):
        """
        Test TIME Message with empty payload
        """
        time_message = b'\x00\x00\x00\x00\x00\x00'
        self.assertEqual("Time - 01/01/1984 00:00:00.000000",
                         parse(time_message),
                         "Error on time Message parse with empty payload")

    def test_TIME_invalid(self):
        """
        Test TIME Message with an invalid payload
        """
        hb_message = b'\xFF'
        with self.assertRaises(ValueError):
            parse(hb_message)


if __name__ == '__main__':
    unittest.main()
