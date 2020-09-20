import unittest
from unittest.mock import mock_open, patch

from canopen_monitor.parser import eds
from canopen_monitor.parser.hb import *
from tests import TEST_EDS


class TestHB(unittest.TestCase):
    """
    Tests for the Heartbeat parser
    """
    def setUp(self) -> None:
        with patch('builtins.open', mock_open(read_data=TEST_EDS)) as m:
            self.eds = eds.load_eds_file("star_tracker_OD.eds")

    def test_HB(self):
        """
        Test Heartbeat Message
        """
        hb_message = b'\x04'
        self.assertEqual("OreSat Star Tracker Stopped",
                         parse(123, self.eds, hb_message),
                         "Error on heartbeat Message parse")

    def test_HB_Invalid(self):
        """
        Test Heartbeat Message with an invalid payload
        """
        hb_message = b'\xFF'
        self.assertEqual("OreSat Star Tracker Invalid State",
                         parse(123, self.eds, hb_message),
                         "Error on heartbeat Message parse")


if __name__ == '__main__':
    unittest.main()
