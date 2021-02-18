import unittest
from unittest.mock import patch, mock_open

from canopen_monitor.parse import eds
from canopen_monitor.parse.pdo import parse
from tests import TEST_EDS


class TestPDO(unittest.TestCase):
    """
    Tests for the SDO parser
    """

    def setUp(self):
        """
        Generate Mocked eds file
        """
        with patch('builtins.open', mock_open(read_data=TEST_EDS)) as m:
            self.eds_data = eds.load_eds_file("star_tracker_OD.eds")

    def test_pdo(self):
        """
        Test PDO transmit
        """
        pdo_message = [0x3f, 0x80, 0x0, 0x0]
        self.assertEqual("Orientation orientation - 1.0",
                         parse(0x180, pdo_message, self.eds_data),
                         "Error on PDO Message parse")

    def test_pdo_with_multiple_elements(self):
        """
        Test PDO transmit with multiple elements in message
        """
        pdo_message = [0x3F, 0x80, 0x00, 0x00, 0x3F, 0xC0, 0x00, 0x00]
        self.assertEqual("Orientation orientation - 1.0 Orientation timestamp "
                         "- 1.5",
                         parse(0x280, pdo_message, self.eds_data),
                         "Error on PDO Message parse (multiple)")

    def test_pdo_with_multiple_elements_complex(self):
        """
        Test PDO transmit with multiple elements in message
        """
        pdo_message = [0x01, 0x3F, 0xC0, 0x00, 0x00]
        self.assertEqual("Orientation boolean - True Orientation timestamp - "
                         "1.5",
                         parse(0x200, pdo_message, self.eds_data),
                         "Error on PDO Message parse (multiple & complex)")

        pdo_message = [0x7F, 0x80, 0x00, 0x01]
        self.assertEqual("Orientation timestamp - 1.5 Orientation boolean - "
                         "True",
                         parse(0x300, pdo_message, self.eds_data),
                         "Error on PDO Message parse (multiple & complex - "
                         "reverse)")

    def test_mpdo_with_SAM(self):
        """
        Test MPDO transmit with source addressing mode
        """
        pdo_message = [0x00, 0x31, 0x01, 0x03, 0x3F, 0x80, 0x00, 0x00]
        self.assertEqual("Orientation orientation - 1.0",
                         parse(0x380, pdo_message, self.eds_data),
                         "Error on MPDO SAM Message parse")
