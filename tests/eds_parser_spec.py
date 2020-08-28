import unittest
import os
import canopen_monitor.parser.eds as eds

TEST_FILENAME = os.path.join(os.path.dirname(__file__), 'data/star_tracker_OD.eds')


class TestEDS(unittest.TestCase):
    def setUp(self):
        self.eds = eds.load_eds_file(TEST_FILENAME)

    def test_parse_index(self):
        """
        EDS should allow for parsing index locations
        """
        self.assertEqual("Device type",
                         self.eds[0x1000].parameter_name,
                         "Error parsing index")

    def test_parse_sub_index(self):
        """
        EDS should allow for parsing sub-index locations
        """
        self.assertEqual("max sub-index",
                         self.eds[0x1018].sub_indices[0].parameter_name,
                         "Error parsing sub-index")

    def test_parse_high_hex_index(self):
        """
        EDS should allow for parsing of high (>9) index hex values
        """
        self.assertEqual("TPDO mapping parameter",
                         self.eds[0x1A00].parameter_name,
                         "Error parsing high hex index")

    def test_parse_high_hex_sub_index(self):
        """
        EDS should allow for parsing of high (>9) sub index hex values
        """
        self.assertEqual("This is for testing",
                         self.eds[0x3002].sub_indices[0xA].parameter_name,
                         "Error parsing high hex sub-index")

    def test_named_sections(self):
        """
        Some sections use names instead of hex values, this should test all valid names
        Currently the deadbeef problem exist, where a name made up of hex values will be treated
        as a hex location. This can be tested here if new named sections are added.
        """
        self.assertEqual("OreSat Star Tracker Board Object Dictionary",
                         self.eds['FileInfo'].description,
                         "Error parsing File Info named section")

        self.assertEqual("Portland State Aerospace Society",
                         self.eds['DeviceInfo'].vendor_name,
                         "Error parsing File Info named section")

        self.assertEqual("0",
                         self.eds['DummyUsage'].dummy0001,
                         "Error parsing Dummy Usage named section")

        self.assertEqual("EDS File for CANopen device",
                         self.eds['Comments'].line1,
                         "Error parsing Comments named section")

        self.assertEqual("3",
                         self.eds['MandatoryObjects'].supported_objects,
                         "Error parsing Comments named section")


if __name__ == '__main__':
    unittest.main()
