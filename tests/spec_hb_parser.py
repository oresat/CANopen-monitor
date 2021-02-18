import unittest
from unittest.mock import mock_open, patch

from canopen_monitor.parse import eds
from canopen_monitor.parse.hb import parse
from canopen_monitor.parse.utilities import FailedValidationError
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
        hb_message = [0x04]
        self.assertEqual("Stopped",
                         parse(123, hb_message, self.eds),
                         "Error on heartbeat Message parse")

    def test_HB_Invalid(self):
        """
        Test Heartbeat Message with an invalid payload
        """
        hb_message = [0xFF]
        with self.assertRaises(FailedValidationError) as context:
            parse(123, hb_message, self.eds)

        self.assertEqual("Invalid heartbeat state detected",
                          str(context.exception))

    def test_HB_Empty(self):
        """
        Test Heartbeat Message with an invalid payload
        """
        hb_message = []
        with self.assertRaises(FailedValidationError) as context:
            parse(123, hb_message, self.eds)

        self.assertEqual("Invalid heartbeat state detected", str(context.exception))
