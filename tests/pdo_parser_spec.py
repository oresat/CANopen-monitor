import unittest
from unittest.mock import MagicMock, patch, mock_open

from canopen_monitor.parser import eds
from canopen_monitor.parser.pdo import *
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
        pdo_message = b'\x3F\x80\x00\x00'
        self.assertEqual("Orientation orientation - 1.0",
                         parse(0x180, self.eds_data, pdo_message),
                         "Error on PDO Message parse")

    def test_pdo_with_multiple_elements(self):
        """
        Test PDO transmit with multiple elements in message
        """
        pdo_message = b'\x3F\x80\x00\x00\x3F\xC0\x00\x00'
        self.assertEqual("Orientation orientation - 1.0\nOrientation timestamp - 1.5",
                         parse(0x280, self.eds_data, pdo_message),
                         "Error on PDO Message parse (multiple)")

    def test_pdo_with_multiple_elements_complex(self):
        """
        Test PDO transmit with multiple elements in message
        """
        pdo_message = b'\x01\x3F\xC0\x00\x00'
        self.assertEqual("Orientation boolean - True\nOrientation timestamp - 1.5",
                         parse(0x200, self.eds_data, pdo_message),
                         "Error on PDO Message parse (multiple & complex)")

        pdo_message = b'\x7F\x80\x00\x01'
        self.assertEqual("Orientation timestamp - 1.5\nOrientation boolean - True",
                         parse(0x300, self.eds_data, pdo_message),
                         "Error on PDO Message parse (multiple & complex - reverse)")

    def test_mpdo_with_SAM(self):
        """
        Test MPDO transmit with source addressing mode
        """
        pdo_message = b'\x00\x31\x01\x03\x3F\x80\x00\x00'
        self.assertEqual("Orientation orientation - 1.0",
                         parse(0x380, self.eds_data, pdo_message),
                         "Error on MPDO SAM Message parse")


if __name__ == '__main__':
    unittest.main()
