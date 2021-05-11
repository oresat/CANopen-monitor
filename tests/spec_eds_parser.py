import unittest
from canopen_monitor import parse
from unittest.mock import mock_open, patch
from tests import TEST_EDS, TEST_DCF

eds = parse.eds


class TestEDS(unittest.TestCase):
    def setUp(self):
        with patch('builtins.open', mock_open(read_data=TEST_EDS)) as _:
            self.eds = eds.load_eds_file("star_tracker_OD.eds")

    def test_parse_index(self):
        """
        EDS should allow for parsing index locations
        """
        self.assertEqual("Device type",
                         self.eds[hex(0x1000)].parameter_name,
                         "Error parsing index")

    def test_parse_sub_index(self):
        """
        EDS should allow for parsing sub-index locations
        """
        self.assertEqual("unsigned8",
                         self.eds[hex(0x1018)][0].parameter_name,
                         "Error parsing sub-index")

    def test_parse_high_hex_index(self):
        """
        EDS should allow for parsing of high (>9) index hex values
        """
        self.assertEqual("TPDO mapping parameter",
                         self.eds[hex(0x1A00)].parameter_name,
                         "Error parsing high hex index")

    def test_parse_high_hex_sub_index(self):
        """
        EDS should allow for parsing of high (>9) sub index hex values
        """
        self.assertEqual("This is for testing",
                         self.eds[hex(0x3002)][0xA].parameter_name,
                         "Error parsing high hex sub-index")

    def test_named_sections(self):
        """
        Some sections use names instead of hex values, this should test all
        valid names Currently the deadbeef problem exist, where a name made
        up of hex values will be treated as a hex location. This can be
        tested here if new named sections are added.
        """
        self.assertEqual("OreSat Star Tracker Board Object Dictionary",
                         self.eds.file_info.description,
                         "Error parsing File Info named section")

        self.assertEqual("Portland State Aerospace Society",
                         self.eds.device_info.vendor_name,
                         "Error parsing File Info named section")

        self.assertEqual("0",
                         self.eds.dummy_usage.dummy_0001,
                         "Error parsing Dummy Usage named section")

        self.assertEqual("EDS File for CANopen device",
                         self.eds.comments.line_1,
                         "Error parsing Comments named section")

        self.assertEqual("3",
                         self.eds.mandatory_objects.supported_objects,
                         "Error parsing Comments named section")

    def test_last_index(self):
        """
        Parsing should capture the last index if there is no newline
        """
        file_check = TEST_EDS.splitlines()
        self.assertEqual("PDOMapping=0",
                         file_check[len(file_check)-1],
                         "The last line in the EDS test file should not be "
                         "blank")

        self.assertEqual("Last Aolved filepath",
                         self.eds[hex(0x3102)].parameter_name,
                         "Error parsing last index location")


class TestDCF(unittest.TestCase):
    def setUp(self):
        with patch('builtins.open', mock_open(read_data=TEST_DCF)) as _:
            self.eds = eds.load_eds_file("star_tracker_OD.eds")

    def test_check_device_commissioning(self):
        """
        DCF Parsing should allow for parsing node id
        """
        self.assertEqual("10",
                         self.eds.device_commissioning.node_id,
                         "Error parsing device commissioning")

    def test_get_node_id(self):
        """
        DCF Parsing set node id attribute
        """
        self.assertEqual(0x10,
                         self.eds.node_id,
                         "Error parsing node id")

    def test_existing_spaces(self):
        """
        DCF tests should test importing a file with arbitrary blank lines
        This test confirms that the test file contains those blank lines
        """
        file_check = TEST_DCF.splitlines()
        self.assertEqual("",
                         file_check[len(file_check) - 1],
                         "The last line in the DCF Test file should be blank")

        self.assertEqual("",
                         file_check[len(file_check) - 12],
                         "There should be 2 blank lines before the last index")

        self.assertEqual("",
                         file_check[len(file_check) - 13],
                         "There should be 2 blank lines before the last index")
