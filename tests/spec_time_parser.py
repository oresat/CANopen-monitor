import unittest
from unittest.mock import mock_open, patch

from canopen_monitor.parse import time, eds
from canopen_monitor.parse.utilities import FailedValidationError
from . import TEST_EDS


class TestTIME(unittest.TestCase):
    """
    Tests for the TIME parser
    """
    def setUp(self) -> None:
        with patch('builtins.open', mock_open(read_data=TEST_EDS)) as m:
            self.eds = eds.load_eds_file("star_tracker_OD.eds")

    def test_TIME(self):
        """
        Test TIME Message
        """
        time_message = [0xE1, 0xC1, 0x97, 0x02, 0x59, 0x34]
        self.assertEqual("Time - 09/09/2020 12:05:00.001000",
                         time.parse(123, time_message, self.eds),
                         "Error on heartbeat Message parse")

    def test_TIME_empty(self):
        """
        Test TIME Message with empty payload
        """
        time_message = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        self.assertEqual("Time - 01/01/1984 00:00:00.000000",
                         time.parse(123, time_message, self.eds),
                         "Error on time Message parse with empty payload")

    def test_TIME_invalid(self):
        """
        Test TIME Message with an invalid payload
        """
        time_message = [0xFF]
        with self.assertRaises(FailedValidationError) as context:
            time.parse(123, time_message, self.eds)

        self.assertEqual("Invalid TIME message length",
                         str(context.exception))
