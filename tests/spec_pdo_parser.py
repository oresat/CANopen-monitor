import unittest
from unittest.mock import patch, mock_open

from canopen_monitor.parse import eds
from canopen_monitor.parse.pdo import parse
from canopen_monitor.parse.utilities import FailedValidationError
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

    def test_pdo_transmit_with_invalid_index(self):
        """
        Test PDO transmit with invalid OD File index
        An exception is returned here because this is due
        to an malformed OD file, not a malformed message
        """
        pdo_message = [0x3f, 0x80, 0x0, 0x0]
        with self.assertRaises(KeyError) as context:
            parse(0x480, pdo_message, self.eds_data)

        self.assertEqual("'3101sub6'", str(context.exception))

    def test_mpdo_with_invalid_index(self):
        """
        Test MPDO transmit with source addressing mode and an invalid index
        This should return a Failed Validation Error
        """
        pdo_message = [0x00, 0x31, 0x0A, 0x03, 0x3F, 0x80, 0x00, 0x00]
        with self.assertRaises(FailedValidationError) as context:
            parse(0x380, pdo_message, self.eds_data),

        self.assertEqual("MPDO provided type index does not exist. Check "
                         "provided index '310a'", str(context.exception))
