import unittest
from unittest.mock import MagicMock, patch, mock_open

from canopen_monitor.parser import eds
from canopen_monitor.parser.sdo import *
from tests import TEST_EDS


class TestSDO(unittest.TestCase):
    """
    Tests for the SDO parser
    """

    def setUp(self):
        """
        Generate Mocked eds file
        """
        with patch('builtins.open', mock_open(read_data=TEST_EDS)) as m:
            self.eds_data = eds.load_eds_file("star_tracker_OD.eds")

    def test_expedited_unsigned_int(self):
        """
        Text expedited SDO transfer with an unsigned int data type
        """
        parser = SDOParser()
        client_initiate_message = b'\x27\x10\x18\x00\x00\x00\x00\x0A'
        self.assertEqual("Downloaded - Identity unsigned8: 10",
                         parser.parse(0x600, self.eds_data, client_initiate_message),
                         "Error on Client Initiate Message")
        self.assertEqual(False, parser.is_complete, "Parser should be incomplete")

        server_initiate_response = b'\x60\x10\x18\x00\x00\x00\x00\x00'
        self.assertEqual("Downloaded - Identity unsigned8: 10",
                         parser.parse(0x580, self.eds_data, server_initiate_response),
                         "Error on Server Initiate Response")
        self.assertEqual(True, parser.is_complete, "Parser should be complete")

    def test_expedited_signed_int(self):
        """
        Text expedited SDO transfer with an signed int data type
        """
        parser = SDOParser()
        client_initiate_message = b'\x2F\x10\x18\x01\xFF\xFF\xFF\xF6'
        self.assertEqual("Downloaded - Identity integer8: -10",
                         parser.parse(0x600, self.eds_data, client_initiate_message),
                         "Error on Client Initiate Message")
        self.assertEqual(False, parser.is_complete, "Parser should be incomplete")

        server_initiate_response = b'\x60\x10\x18\x01\x00\x00\x00\x00'
        self.assertEqual("Downloaded - Identity integer8: -10",
                         parser.parse(0x580, self.eds_data, server_initiate_response),
                         "Error on Server Initiate Response")
        self.assertEqual(True, parser.is_complete, "Parser should be complete")

    def test_expedited_boolean(self):
        """
        Text expedited SDO transfer with a boolean data type
        Any non-zero value is considered True
        """
        parser = SDOParser()
        client_initiate_message = b'\x27\x10\x18\x02\x00\x00\x00\x01'
        self.assertEqual("Downloaded - Identity boolean: True",
                         parser.parse(0x600, self.eds_data, client_initiate_message),
                         "Error on Client Initiate Message")
        self.assertEqual(False, parser.is_complete, "Parser should be incomplete")

        server_initiate_response = b'\x60\x10\x18\x02\x00\x00\x00\x00'
        self.assertEqual("Downloaded - Identity boolean: True",
                         parser.parse(0x580, self.eds_data, server_initiate_response),
                         "Error on Server Initiate Response")
        self.assertEqual(True, parser.is_complete, "Parser should be complete")

        parser = SDOParser()
        client_initiate_message = b'\x27\x10\x18\x02\x00\x00\x00\x00'
        self.assertEqual("Downloaded - Identity boolean: False",
                         parser.parse(0x600, self.eds_data, client_initiate_message),
                         "Error on Client Initiate Message")
        self.assertEqual(False, parser.is_complete, "Parser should be incomplete")

        server_initiate_response = b'\x60\x10\x18\x02\x00\x00\x00\x00'
        self.assertEqual("Downloaded - Identity boolean: False",
                         parser.parse(0x580, self.eds_data, server_initiate_response),
                         "Error on Server Initiate Response")
        self.assertEqual(True, parser.is_complete, "Parser should be complete")

    def test_expedited_real32(self):
        """
        Text expedited SDO transfer with an float data type
        """
        parser = SDOParser()
        client_initiate_message = b'\x2F\x10\x18\x03\x41\x28\x00\x00'
        self.assertEqual("Downloaded - Identity real32: 10.5",
                         parser.parse(0x600, self.eds_data, client_initiate_message),
                         "Error on Client Initiate Message")
        self.assertEqual(False, parser.is_complete, "Parser should be incomplete")

        server_initiate_response = b'\x60\x10\x18\x03\x00\x00\x00\x00'
        self.assertEqual("Downloaded - Identity real32: 10.5",
                         parser.parse(0x580, self.eds_data, server_initiate_response),
                         "Error on Server Initiate Response")
        self.assertEqual(True, parser.is_complete, "Parser should be complete")

    def test_expedited_visible_string(self):
        """
        Text expedited SDO transfer with an ASCII string data type
        """
        parser = SDOParser()
        client_initiate_message = b'\x2F\x10\x18\x04\x61\x62\x63\x64'
        self.assertEqual("Downloaded - Identity visible string: abcd",
                         parser.parse(0x600, self.eds_data, client_initiate_message),
                         "Error on Client Initiate Message")
        self.assertEqual(False, parser.is_complete, "Parser should be incomplete")

        server_initiate_response = b'\x60\x10\x18\x04\x00\x00\x00\x00'
        self.assertEqual("Downloaded - Identity visible string: abcd",
                         parser.parse(0x580, self.eds_data, server_initiate_response),
                         "Error on Server Initiate Response")
        self.assertEqual(True, parser.is_complete, "Parser should be complete")

    def test_expedited_octet_string(self):
        """
        Text expedited SDO transfer with an octet string data type (bytes as a string)
        """
        parser = SDOParser()
        client_initiate_message = b'\x2F\x10\x18\x05\x61\x62\x63\x64'
        self.assertEqual("Downloaded - Identity octet string: 61626364",
                         parser.parse(0x600, self.eds_data, client_initiate_message),
                         "Error on Client Initiate Message")
        self.assertEqual(False, parser.is_complete, "Parser should be incomplete")

        server_initiate_response = b'\x60\x10\x18\x05\x00\x00\x00\x00'
        self.assertEqual("Downloaded - Identity octet string: 61626364",
                         parser.parse(0x580, self.eds_data, server_initiate_response),
                         "Error on Server Initiate Response")
        self.assertEqual(True, parser.is_complete, "Parser should be complete")

    def test_expedited_unicode_string(self):
        """
        Text expedited SDO transfer with an unicode string data type
        """
        parser = SDOParser()
        client_initiate_message = b'\x2F\x10\x18\x06\xD8\x3C\xDF\x7B'
        self.assertEqual("Downloaded - Identity unicode string: 🍻",
                         parser.parse(0x600, self.eds_data, client_initiate_message),
                         "Error on Client Initiate Message")
        self.assertEqual(False, parser.is_complete, "Parser should be incomplete")

        server_initiate_response = b'\x60\x10\x18\x06\x00\x00\x00\x00'
        self.assertEqual("Downloaded - Identity unicode string: 🍻",
                         parser.parse(0x580, self.eds_data, server_initiate_response),
                         "Error on Server Initiate Response")
        self.assertEqual(True, parser.is_complete, "Parser should be complete")

    def test_normal_transfer_multiple_segments_with_size(self):
        """
        Test Normal SDO transfer with size indicated (Data not returned)
        """
        parser = SDOParser()

        client_initiate_message = b'\x21\x10\x18\x00\x00\x00\x00\x10'
        self.assertEqual("Initiating block download - Identity unsigned8",
                         parser.parse(0x600, self.eds_data, client_initiate_message),
                         "Error on Client Initiate Message")
        self.assertEqual(False, parser.is_complete, "Parser should be incomplete")

        server_initiate_response = b'\x60\x10\x18\x00\x00\x00\x00\x00'
        self.assertEqual("Identity unsigned8 0%",
                         parser.parse(0x580, self.eds_data, server_initiate_response),
                         "Error on Server Initiate Message")
        self.assertEqual(False, parser.is_complete, "Parser should be incomplete")

        client_download_segment = b'\x10\x00\x00\x00\x00\x00\x00\x0A'
        self.assertEqual("Block downloading - Identity unsigned8",
                         parser.parse(0x600, self.eds_data, client_download_segment),
                         "Error on Client End Message")
        self.assertEqual(False, parser.is_complete, "Parser should be incomplete")

        server_download_response = b'\x30\x00\x00\x00\x00\x00\x00\x00'
        self.assertEqual("Identity unsigned8 50.0%",
                         parser.parse(0x580, self.eds_data, server_download_response),
                         "Error on Server End Message")
        self.assertEqual(False, parser.is_complete, "Parser should be incomplete")

        client_download_segment = b'\x01\x00\x00\x00\x00\x00\x00\x0A'
        self.assertEqual("Block download done - Identity unsigned8",
                         parser.parse(0x600, self.eds_data, client_download_segment),
                         "Error on Client End Message")
        self.assertEqual(False, parser.is_complete, "Parser should be incomplete")

        server_download_response = b'\x20\x00\x00\x00\x00\x00\x00\x00'
        self.assertEqual("Identity unsigned8 100%",
                         parser.parse(0x580, self.eds_data, server_download_response),
                         "Error on Server End Message")
        self.assertEqual(True, parser.is_complete, "Parser should be complete")

    def test_normal_transfer_multiple_segments_no_size(self):
        """
        Test Normal SDO transfer without size indicated (Data not returned)
        """
        parser = SDOParser()

        client_initiate_message = b'\x20\x10\x18\x00\x00\x00\x00\x00'
        self.assertEqual("Initiating block download - Identity unsigned8",
                         parser.parse(0x600, self.eds_data, client_initiate_message),
                         "Error on Client Initiate Message")
        self.assertEqual(False, parser.is_complete, "Parser should be incomplete")

        server_initiate_response = b'\x60\x10\x18\x00\x00\x00\x00\x00'
        self.assertEqual("Identity unsigned8 0%",
                         parser.parse(0x580, self.eds_data, server_initiate_response),
                         "Error on Server Initiate Message")
        self.assertEqual(False, parser.is_complete, "Parser should be incomplete")

        client_download_segment = b'\x10\x00\x00\x00\x00\x00\x00\x0A'
        self.assertEqual("Block downloading - Identity unsigned8",
                         parser.parse(0x600, self.eds_data, client_download_segment),
                         "Error on Client End Message")
        self.assertEqual(False, parser.is_complete, "Parser should be incomplete")

        server_download_response = b'\x30\x00\x00\x00\x00\x00\x00\x00'
        self.assertEqual("Identity unsigned8 XXX%",
                         parser.parse(0x580, self.eds_data, server_download_response),
                         "Error on Server End Message")
        self.assertEqual(False, parser.is_complete, "Parser should be incomplete")

        client_download_segment = b'\x01\x00\x00\x00\x00\x00\x00\x0A'
        self.assertEqual("Block download done - Identity unsigned8",
                         parser.parse(0x600, self.eds_data, client_download_segment),
                         "Error on Client End Message")
        self.assertEqual(False, parser.is_complete, "Parser should be incomplete")

        server_download_response = b'\x20\x00\x00\x00\x00\x00\x00\x00'
        self.assertEqual("Identity unsigned8 100%",
                         parser.parse(0x580, self.eds_data, server_download_response),
                         "Error on Server End Message")
        self.assertEqual(True, parser.is_complete, "Parser should be complete")

    def test_normal_transfer_multiple_segments_with_size_upload(self):
        """
        Test Normal SDO transfer with size indicated (Data not returned)
        This test is using the upload order (data from client not server)
        """
        parser = SDOParser()

        client_initiate_message = b'\x40\x10\x18\x00\x00\x00\x00\x00'
        self.assertEqual("Identity unsigned8 0%",
                         parser.parse(0x600, self.eds_data, client_initiate_message),
                         "Error on Client Initiate Message")
        self.assertEqual(False, parser.is_complete, "Parser should be incomplete")

        server_initiate_response = b'\x41\x10\x18\x00\x00\x00\x00\x10'
        self.assertEqual("Initiating block download - Identity unsigned8",
                         parser.parse(0x580, self.eds_data, server_initiate_response),
                         "Error on Server Initiate Message")
        self.assertEqual(False, parser.is_complete, "Parser should be incomplete")

        client_download_segment = b'\x70\x00\x00\x00\x00\x00\x00\x00'
        self.assertEqual("Identity unsigned8 50.0%",
                         parser.parse(0x600, self.eds_data, client_download_segment),
                         "Error on Client End Message")
        self.assertEqual(False, parser.is_complete, "Parser should be incomplete")

        server_download_response = b'\x10\x00\x00\x00\x00\x00\x00\x0A'
        self.assertEqual("Block downloading - Identity unsigned8",
                         parser.parse(0x580, self.eds_data, server_download_response),
                         "Error on Server End Message")
        self.assertEqual(False, parser.is_complete, "Parser should be incomplete")

        client_download_segment = b'\x60\x00\x00\x00\x00\x00\x00\x00'
        self.assertEqual("Identity unsigned8 50.0%",
                         parser.parse(0x600, self.eds_data, client_download_segment),
                         "Error on Client End Message")
        self.assertEqual(False, parser.is_complete, "Parser should be incomplete")

        server_download_response = b'\x01\x00\x00\x00\x00\x00\x00\x0A'
        self.assertEqual("Block download done - Identity unsigned8",
                         parser.parse(0x580, self.eds_data, server_download_response),
                         "Error on Server End Message")
        self.assertEqual(True, parser.is_complete, "Parser should be complete")

    def test_expedited_unsigned_int_upload(self):
        """
        Test expedited SDO transfer with an unsigned int data type
        """
        parser = SDOParser()
        client_initiate_message = b'\x40\x10\x18\x00\x00\x00\x00\x00'
        self.assertEqual("Identity unsigned8 0%",
                         parser.parse(0x600, self.eds_data, client_initiate_message),
                         "Error on Client Initiate Message")
        self.assertEqual(False, parser.is_complete, "Parser should be incomplete")

        server_initiate_response = b'\x47\x10\x18\x00\x00\x00\x00\x0A'
        self.assertEqual("Downloaded - Identity unsigned8: 10",
                         parser.parse(0x580, self.eds_data, server_initiate_response),
                         "Error on Server Initiate Response")
        self.assertEqual(True, parser.is_complete, "Parser should be complete")

    def test_sdo_block_download(self):
        """
        Test SDO Block Upload

        Upload 8byte unsigned integer with value 10
        """
        parser = SDOParser()
        client_initiate_message = b'\xE6\x10\x18\x00\x00\x00\x00\x08'
        self.assertEqual("Initiating block download - Identity unsigned8",
                         parser.parse(0x600, self.eds_data, client_initiate_message),
                         "Error on Client Initiate Message")
        self.assertEqual(False, parser.is_complete, "Parser should be incomplete")

        server_initiate_response = b'\xC4\x10\x18\x00\x02\x00\x00\x00'
        self.assertEqual("Identity unsigned8 0%",
                         parser.parse(0x580, self.eds_data, server_initiate_response),
                         "Error on Server Initiate Message")
        self.assertEqual(False, parser.is_complete, "Parser should be incomplete")

        client_block1_message = b'\x01\x00\x00\x00\x00\x00\x00\x00'
        self.assertEqual("Block downloading - Identity unsigned8",
                         parser.parse(0x600, self.eds_data, client_block1_message),
                         "Error on Client Block1 Message")
        self.assertEqual(False, parser.is_complete, "Parser should be incomplete")

        client_block2_message = b'\x82\x0A\x00\x00\x00\x00\x00\x00'
        self.assertEqual("Block downloading - Identity unsigned8",
                         parser.parse(0x600, self.eds_data, client_block2_message),
                         "Error on Client Block1 Message")
        self.assertEqual(False, parser.is_complete, "Parser should be incomplete")

        server_block_confirm_message = b'\xA2\x02\x08\x00\x00\x00\x00\x00'
        self.assertEqual("Identity unsigned8 100.0%",
                         parser.parse(0x580, self.eds_data, server_block_confirm_message),
                         "Error on Server End Message")
        self.assertEqual(False, parser.is_complete, "Parser should be incomplete")

        client_block_end_message = b'\xDD\xA1\x4A\x00\x00\x00\x00\x00'
        self.assertEqual("Identity unsigned8 100%",
                         parser.parse(0x600, self.eds_data, client_block_end_message),
                         "Error on Client End Message")
        self.assertEqual(False, parser.is_complete, "Parser should be incomplete")

        server_block_end_confirm_message = b'\xA1\x00\x00\x00\x00\x00\x00\x00'
        self.assertEqual("Block download done - Identity unsigned8",
                         parser.parse(0x580, self.eds_data, server_block_end_confirm_message),
                         "Error on Server End Message")
        self.assertEqual(True, parser.is_complete, "Parser should be complete")

    def test_sdo_block_upload(self):
        """
        Test SDO Block Download

        Download 8byte unsigned integer with value 10
        """
        parser = SDOParser()
        client_initiate_message = b'\xA4\x10\x18\x00\x02\x00\x00\x00'
        self.assertEqual("Identity unsigned8 0%",
                         parser.parse(0x600, self.eds_data, client_initiate_message),
                         "Error on Client Initiate Message")
        self.assertEqual(False, parser.is_complete, "Parser should be incomplete")

        server_initiate_response = b'\xE6\x10\x18\x00\x00\x00\x00\x08'
        self.assertEqual("Initiating block download - Identity unsigned8",
                         parser.parse(0x580, self.eds_data, server_initiate_response),
                         "Error on Server Initiate Message")
        self.assertEqual(False, parser.is_complete, "Parser should be incomplete#")

        server_initiate_response = b'\xA3\x00\x00\x00\x00\x00\x00\x00'
        self.assertEqual("Initiating block download - Identity unsigned8",
                         parser.parse(0x580, self.eds_data, server_initiate_response),
                         "Error on Server Initiate Message")
        self.assertEqual(False, parser.is_complete, "Parser should be incomplete#")

        server_block1_message = b'\x01\x00\x00\x00\x00\x00\x00\x00'
        self.assertEqual("Block downloading - Identity unsigned8",
                         parser.parse(0x580, self.eds_data, server_block1_message),
                         "Error on Server Block1 Message")
        self.assertEqual(False, parser.is_complete, "Parser should be incomplete")

        server_block2_message = b'\x82\x0A\x00\x00\x00\x00\x00\x00'
        self.assertEqual("Block downloading - Identity unsigned8",
                         parser.parse(0x580, self.eds_data, server_block2_message),
                         "Error on Server Block2 Message")
        self.assertEqual(False, parser.is_complete, "Parser should be incomplete")

        client_block_confirm_message = b'\xA2\x02\x08\x00\x00\x00\x00\x00'
        self.assertEqual("Identity unsigned8 100.0%",
                         parser.parse(0x600, self.eds_data, client_block_confirm_message),
                         "Error on Client Confirm Block Message")
        self.assertEqual(False, parser.is_complete, "Parser should be incomplete")

        server_block_end_message = b'\xDD\xA1\x4A\x00\x00\x00\x00\x00'
        self.assertEqual("Identity unsigned8 100%",
                         parser.parse(0x580, self.eds_data, server_block_end_message),
                         "Error on Server End Message")
        self.assertEqual(False, parser.is_complete, "Parser should be incomplete")

        client_block_end_confirm_message = b'\xA1\x00\x00\x00\x00\x00\x00\x00'
        self.assertEqual("Block download done - Identity unsigned8",
                         parser.parse(0x600, self.eds_data, client_block_end_confirm_message),
                         "Error on Server End Message")
        self.assertEqual(True, parser.is_complete, "Parser should be complete")


if __name__ == '__main__':
    unittest.main()
