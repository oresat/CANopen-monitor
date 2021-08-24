import unittest
from unittest.mock import patch, mock_open

from canopen_monitor.parse import eds, load_eds_files
from canopen_monitor.parse.pdo import parse
from canopen_monitor.parse.utilities import FailedValidationError
from tests import TEST_EDS, BATTERY_DCF
from canopen_monitor.parse.canopen import CANOpenParser
from canopen_monitor.can import Message


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


class TestExtendedPDODefinition(unittest.TestCase):
    """
    Tests the extended PDO definitions. This is an integration test of the OD changes.
    If there is an issue here, the OD class is a good place to look for a
    resolution.
    """

    def setUp(self):
        """
        load eds files from folder
        """
        with patch('builtins.open', mock_open(read_data=BATTERY_DCF)) as _:
            with patch('os.listdir') as mocked_listdir:
                mocked_listdir.return_value = ["battery.dcf"]
                self.parser = CANOpenParser(load_eds_files("/"))

    def test1(self):
        pdo_message = Message(0x184,
                data=[0xDF, 0x1D, 0xEC, 0x0E, 0xD8, 0x0E, 0xF0, 0x0E],
                frame_type=1,
                interface="vcan0",
                timestamp="", # datetime.datetime.now()
                extended=False)

        pdo_message.node_name = self.parser.get_name(pdo_message)
        pdo_message.message, pdo_message.error = self.parser.parse(pdo_message)

        self.assertEqual("Battery", pdo_message.node_name)
        self.assertEqual(
            "Battery Vbatt - 7647 Battery VCell max - 3820 Battery VCell min - 3800 Battery VCell - 3824",
            pdo_message.message)
        self.assertEqual("", pdo_message.error)

    def test2(self):
        pdo_message = Message(0x284,
                              data=[0xF0, 0x0E, 0xEF, 0x0E, 0xF0, 0x0E, 0x00, 0x00],
                              frame_type=1,
                              interface="vcan0",
                              timestamp="",  # datetime.datetime.now()
                              extended=False)

        pdo_message.node_name = self.parser.get_name(pdo_message)
        pdo_message.message, pdo_message.error = self.parser.parse(pdo_message)

        self.assertEqual("Battery", pdo_message.node_name)
        self.assertEqual(
            "Battery VCell1 - 3823 Battery VCell2 - 3824 Battery VCell avg - 0",
            pdo_message.message)
        self.assertEqual("", pdo_message.error)


    def test3(self):

        pdo_message = Message(0x384,
                              data=[0x09, 0x00, 0x04, 0x00, 0x50, 0x00, 0x38, 0xFF],
                              frame_type=1,
                              interface="vcan0",
                              timestamp="",  # datetime.datetime.now()
                              extended=False)

        pdo_message.node_name = self.parser.get_name(pdo_message)
        pdo_message.message, pdo_message.error = self.parser.parse(pdo_message)

        self.assertEqual("Battery", pdo_message.node_name)
        self.assertEqual(
            "Battery Current - 9 Battery Current avg - 4 Battery Current max - 80 Battery Current min - -200",
            pdo_message.message)
        self.assertEqual("", pdo_message.error)

    def test4(self):
        pdo_message = Message(0x484,
                              data=[0x17, 0x00, 0x17, 0x00, 0x18, 0x00, 0x16, 0x00],
                              frame_type=1,
                              interface="vcan0",
                              timestamp="",  # datetime.datetime.now()
                              extended=False)

        pdo_message.node_name = self.parser.get_name(pdo_message)
        pdo_message.message, pdo_message.error = self.parser.parse(pdo_message)

        self.assertEqual("Battery", pdo_message.node_name)
        self.assertEqual(
            "Battery Temperature - 23 Battery Temperature avg - 23 Battery Temperature max - 24 Battery Temperature min - 22",
            pdo_message.message)
        self.assertEqual("", pdo_message.error)


    def test5(self):
        pdo_message = Message(0x185,
                              data=[0xDC, 0x05, 0xF5, 0x02, 0x32, 0x18],
                              frame_type=1,
                              interface="vcan0",
                              timestamp="",  # datetime.datetime.now()
                              extended=False)

        pdo_message.node_name = self.parser.get_name(pdo_message)
        self.assertEqual("Battery", pdo_message.node_name)
        pdo_message.message, pdo_message.error = self.parser.parse(pdo_message)


        self.assertEqual(
            "Battery Full Capacity - 1500 Battery Reported Capacity - 757 Battery Reported State of Charge - 50 Battery State - 24",
            pdo_message.message)
        self.assertEqual("", pdo_message.error)

    def test6(self):
        pdo_message = Message(0x285,
                              data=[0xE2, 0x1D, 0xEC, 0x0E, 0xD8, 0x0E, 0xF1,
                                    0x0E],
                              frame_type=1,
                              interface="vcan0",
                              timestamp="",  # datetime.datetime.now()
                              extended=False)

        pdo_message.node_name = self.parser.get_name(pdo_message)
        self.assertEqual("Battery", pdo_message.node_name)
        pdo_message.message, pdo_message.error = self.parser.parse(pdo_message)

        self.assertEqual(
            "Battery Vbatt - 7650 Battery VCell max - 3820 Battery VCell min - 3800 Battery VCell - 3825",
            pdo_message.message)
        self.assertEqual("", pdo_message.error)

    def test7(self):
        pdo_message = Message(0x385,
                              data=[0xF1, 0x0E, 0xF1, 0x0E, 0xF2, 0x0E],
                              frame_type=1,
                              interface="vcan0",
                              timestamp="",  # datetime.datetime.now()
                              extended=False)

        pdo_message.node_name = self.parser.get_name(pdo_message)
        self.assertEqual("Battery", pdo_message.node_name)
        pdo_message.message, pdo_message.error = self.parser.parse(pdo_message)

        self.assertEqual(
            "Battery VCell1 - 3825 Battery VCell2 - 3825 Battery VCell avg - 3826",
            pdo_message.message)
        self.assertEqual("", pdo_message.error)

    def test8(self):
        pdo_message = Message(0x485,
                              data=[0x09, 0x00, 0x04, 0x00, 0x50, 0x38, 0xFF],
                              frame_type=1,
                              interface="vcan0",
                              timestamp="",  # datetime.datetime.now()
                              extended=False)

        pdo_message.node_name = self.parser.get_name(pdo_message)
        self.assertEqual("Battery", pdo_message.node_name)
        pdo_message.message, pdo_message.error = self.parser.parse(
            pdo_message)

        self.assertEqual(
            "Battery Current - 0 Battery Current avg - 1024 Battery Current max - 20480 Battery Current min - -200",
            pdo_message.message)
        self.assertEqual("", pdo_message.error)

    def test9(self):
        pdo_message = Message(0x186,
                              data=[0x15, 0x00, 0x15, 0x00, 0x16, 0x00, 0x15,
                                    0x00],
                              frame_type=1,
                              interface="vcan0",
                              timestamp="",  # datetime.datetime.now()
                              extended=False)

        pdo_message.node_name = self.parser.get_name(pdo_message)
        self.assertEqual("Battery", pdo_message.node_name)
        pdo_message.message, pdo_message.error = self.parser.parse(
            pdo_message)

        self.assertEqual(
            "Battery Temperature - 21 Battery Temperature avg - 21 Battery Temperature max - 22 Battery Temperature min - 21",
            pdo_message.message)
        self.assertEqual("", pdo_message.error)

    def test10(self):
        pdo_message = Message(0x286,
                              data=[0xDC, 0x05, 0xF8, 0x02, 0x32, 0x18],
                              frame_type=1,
                              interface="vcan0",
                              timestamp="",  # datetime.datetime.now()
                              extended=False)

        pdo_message.node_name = self.parser.get_name(pdo_message)
        self.assertEqual("Battery", pdo_message.node_name)
        pdo_message.message, pdo_message.error = self.parser.parse(
            pdo_message)

        self.assertEqual(
            "Battery Full Capacity - 1500 Battery Reported Capacity - 760 Battery Reported State of Charge - 50 Battery State - 24",
            pdo_message.message)
        self.assertEqual("", pdo_message.error)



