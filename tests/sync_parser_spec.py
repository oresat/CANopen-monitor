import unittest

from canopen_monitor.parser.sync import *


class TestSYNC(unittest.TestCase):
    """
    Tests for the SYNC parser
    """

    def test_SYNC(self):
        """
        Test SYNC Message
        """
        sync_message = b'\x81'
        self.assertEqual("SYNC - 129",
                         parse(sync_message),
                         "Error on SYNC Message parse")

    """
    Tests for the SYNC parser with an empty payload which is legal
    """

    def test_SYNC_empty(self):
        """
        Test SYNC Message as empty payload
        """
        sync_message = b''
        self.assertEqual("SYNC - 0",
                         parse(sync_message),
                         "Error on SYNC empty Message parse")

    """
    Tests for the SYNC parser with an invalid payload
    """

    def test_SYNC_invalid(self):
        """
        Test SYNC Message with an invalid payload
        """
        sync_message = b'\x01\xFF'
        with self.assertRaises(ValueError):
            parse(sync_message)


if __name__ == '__main__':
    unittest.main()
