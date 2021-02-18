import unittest
from unittest.mock import patch, mock_open

from canopen_monitor.parse import eds
from canopen_monitor.parse.sdo import SDOParser
from canopen_monitor.parse.utilities import FailedValidationError
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
        client_initiate_message = [0x27, 0x10, 0x18, 0x00, 0x0A, 0x00, 0x00,
                                   0x00]
        self.assertEqual("Downloaded - Identity unsigned8: 10",
                         parser.parse(0x600, client_initiate_message,
                                      self.eds_data),
                         "Error on Client Initiate Message")
        self.assertEqual(False, parser.is_complete,
                         "Parser should be incomplete")

        server_initiate_response = [0x60, 0x10, 0x18, 0x00, 0x00, 0x00, 0x00,
                                    0x00]
        self.assertEqual("Downloaded - Identity unsigned8: 10",
                         parser.parse(0x580, server_initiate_response,
                                      self.eds_data),
                         "Error on Server Initiate Response")
        self.assertEqual(True, parser.is_complete, "Parser should be complete")

    def test_expedited_signed_int(self):
        """
        Text expedited SDO transfer with an signed int data type
        """
        parser = SDOParser()
        client_initiate_message = [0x2F, 0x10, 0x18, 0x01, 0xF6, 0xFF, 0xFF,
                                   0xFF]
        self.assertEqual("Downloaded - Identity integer8: -10",
                         parser.parse(0x600, client_initiate_message,
                                      self.eds_data),
                         "Error on Client Initiate Message")
        self.assertEqual(False, parser.is_complete,
                         "Parser should be incomplete")

        server_initiate_response = [0x60, 0x10, 0x18, 0x01, 0x00, 0x00, 0x00,
                                    0x00]
        self.assertEqual("Downloaded - Identity integer8: -10",
                         parser.parse(0x580, server_initiate_response,
                                      self.eds_data),
                         "Error on Server Initiate Response")
        self.assertEqual(True, parser.is_complete, "Parser should be complete")

    def test_expedited_boolean(self):
        """
        Text expedited SDO transfer with a boolean data type
        Any non-zero value is considered True
        """
        parser = SDOParser()
        client_initiate_message = [0x27, 0x10, 0x18, 0x02, 0x00, 0x00, 0x00,
                                   0x01]
        self.assertEqual("Downloaded - Identity boolean: True",
                         parser.parse(0x600, client_initiate_message,
                                      self.eds_data),
                         "Error on Client Initiate Message")
        self.assertEqual(False, parser.is_complete,
                         "Parser should be incomplete")

        server_initiate_response = [0x60, 0x10, 0x18, 0x02, 0x00, 0x00, 0x00,
                                    0x00]
        self.assertEqual("Downloaded - Identity boolean: True",
                         parser.parse(0x580, server_initiate_response,
                                      self.eds_data),
                         "Error on Server Initiate Response")
        self.assertEqual(True, parser.is_complete, "Parser should be complete")

        parser = SDOParser()
        client_initiate_message = [0x27, 0x10, 0x18, 0x02, 0x00, 0x00, 0x00,
                                   0x00]
        self.assertEqual("Downloaded - Identity boolean: False",
                         parser.parse(0x600, client_initiate_message,
                                      self.eds_data),
                         "Error on Client Initiate Message")
        self.assertEqual(False, parser.is_complete,
                         "Parser should be incomplete")

        server_initiate_response = [0x60, 0x10, 0x18, 0x02, 0x00, 0x00, 0x00,
                                    0x00]
        self.assertEqual("Downloaded - Identity boolean: False",
                         parser.parse(0x580, server_initiate_response,
                                      self.eds_data),
                         "Error on Server Initiate Response")
        self.assertEqual(True, parser.is_complete, "Parser should be complete")

    def test_expedited_real32(self):
        """
        Text expedited SDO transfer with an float data type
        """
        parser = SDOParser()
        client_initiate_message = [0x2F, 0x10, 0x18, 0x03, 0x41, 0x28, 0x00,
                                   0x00]
        self.assertEqual("Downloaded - Identity real32: 10.5",
                         parser.parse(0x600, client_initiate_message,
                                      self.eds_data),
                         "Error on Client Initiate Message")
        self.assertEqual(False, parser.is_complete,
                         "Parser should be incomplete")

        server_initiate_response = [0x60, 0x10, 0x18, 0x03, 0x00, 0x00, 0x00,
                                    0x00]
        self.assertEqual("Downloaded - Identity real32: 10.5",
                         parser.parse(0x580, server_initiate_response,
                                      self.eds_data),
                         "Error on Server Initiate Response")
        self.assertEqual(True, parser.is_complete, "Parser should be complete")

    def test_expedited_visible_string(self):
        """
        Text expedited SDO transfer with an ASCII string data type
        """
        parser = SDOParser()
        client_initiate_message = [0x2F, 0x10, 0x18, 0x04, 0x61, 0x62, 0x63,
                                   0x64]
        self.assertEqual("Downloaded - Identity visible string: abcd",
                         parser.parse(0x600, client_initiate_message,
                                      self.eds_data),
                         "Error on Client Initiate Message")
        self.assertEqual(False, parser.is_complete,
                         "Parser should be incomplete")

        server_initiate_response = [0x60, 0x10, 0x18, 0x04, 0x00, 0x00, 0x00,
                                    0x00]
        self.assertEqual("Downloaded - Identity visible string: abcd",
                         parser.parse(0x580, server_initiate_response,
                                      self.eds_data),
                         "Error on Server Initiate Response")
        self.assertEqual(True, parser.is_complete, "Parser should be complete")

    def test_expedited_octet_string(self):
        """
        Text expedited SDO transfer with an octet string data type
        """
        parser = SDOParser()
        client_initiate_message = [0x2F, 0x10, 0x18, 0x05, 0x61, 0x62, 0x63,
                                   0x64]
        self.assertEqual("Downloaded - Identity octet string: 0x61626364",
                         parser.parse(0x600, client_initiate_message,
                                      self.eds_data),
                         "Error on Client Initiate Message")
        self.assertEqual(False, parser.is_complete,
                         "Parser should be incomplete")

        server_initiate_response = [0x60, 0x10, 0x18, 0x05, 0x00, 0x00, 0x00,
                                    0x00]
        self.assertEqual("Downloaded - Identity octet string: 0x61626364",
                         parser.parse(0x580, server_initiate_response,
                                      self.eds_data),
                         "Error on Server Initiate Response")
        self.assertEqual(True, parser.is_complete, "Parser should be complete")

    def test_expedited_unicode_string(self):
        """
        Text expedited SDO transfer with an unicode string data type
        """
        parser = SDOParser()
        client_initiate_message = [0x2F, 0x10, 0x18, 0x06, 0xD8, 0x3C, 0xDF,
                                   0x7B]
        self.assertEqual("Downloaded - Identity unicode string: 🍻",
                         parser.parse(0x600, client_initiate_message,
                                      self.eds_data),
                         "Error on Client Initiate Message")
        self.assertEqual(False, parser.is_complete,
                         "Parser should be incomplete")

        server_initiate_response = [0x60, 0x10, 0x18, 0x06, 0x00, 0x00, 0x00,
                                    0x00]
        self.assertEqual("Downloaded - Identity unicode string: 🍻",
                         parser.parse(0x580, server_initiate_response,
                                      self.eds_data),
                         "Error on Server Initiate Response")
        self.assertEqual(True, parser.is_complete, "Parser should be complete")

    def test_normal_transfer_multiple_segments_with_size(self):
        """
        Test Normal SDO transfer with size indicated (Data not returned)
        """
        parser = SDOParser()

        client_initiate_message = [0x21, 0x10, 0x18, 0x00, 0x00, 0x00, 0x00,
                                   0x10]
        self.assertEqual("Initiating block download - Identity unsigned8",
                         parser.parse(0x600, client_initiate_message,
                                      self.eds_data),
                         "Error on Client Initiate Message")
        self.assertEqual(False, parser.is_complete,
                         "Parser should be incomplete")

        server_initiate_response = [0x60, 0x10, 0x18, 0x00, 0x00, 0x00, 0x00,
                                    0x00]
        self.assertEqual("Identity unsigned8 0%",
                         parser.parse(0x580, server_initiate_response,
                                      self.eds_data),
                         "Error on Server Initiate Message")
        self.assertEqual(False, parser.is_complete,
                         "Parser should be incomplete")

        client_download_segment = [0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                   0x0A]
        self.assertEqual("Block downloading - Identity unsigned8",
                         parser.parse(0x600, client_download_segment,
                                      self.eds_data),
                         "Error on Client End Message")
        self.assertEqual(False, parser.is_complete,
                         "Parser should be incomplete")

        server_download_response = [0x30, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                    0x00]
        self.assertEqual("Identity unsigned8 50.0%",
                         parser.parse(0x580, server_download_response,
                                      self.eds_data),
                         "Error on Server End Message")
        self.assertEqual(False, parser.is_complete,
                         "Parser should be incomplete")

        client_download_segment = [0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                   0x0A]
        self.assertEqual("Block download done - Identity unsigned8",
                         parser.parse(0x600, client_download_segment,
                                      self.eds_data),
                         "Error on Client End Message")
        self.assertEqual(False, parser.is_complete,
                         "Parser should be incomplete")

        server_download_response = [0x20, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                    0x00]
        self.assertEqual("Identity unsigned8 100%",
                         parser.parse(0x580, server_download_response,
                                      self.eds_data),
                         "Error on Server End Message")
        self.assertEqual(True, parser.is_complete, "Parser should be complete")

    def test_normal_transfer_multiple_segments_no_size(self):
        """
        Test Normal SDO transfer without size indicated (Data not returned)
        """
        parser = SDOParser()

        client_initiate_message = [0x20, 0x10, 0x18, 0x00, 0x00, 0x00, 0x00,
                                   0x00]
        self.assertEqual("Initiating block download - Identity unsigned8",
                         parser.parse(0x600, client_initiate_message,
                                      self.eds_data),
                         "Error on Client Initiate Message")
        self.assertEqual(False, parser.is_complete,
                         "Parser should be incomplete")

        server_initiate_response = [0x60, 0x10, 0x18, 0x00, 0x00, 0x00, 0x00,
                                    0x00]
        self.assertEqual("Identity unsigned8 0%",
                         parser.parse(0x580, server_initiate_response,
                                      self.eds_data),
                         "Error on Server Initiate Message")
        self.assertEqual(False, parser.is_complete,
                         "Parser should be incomplete")

        client_download_segment = [0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                   0x0A]
        self.assertEqual("Block downloading - Identity unsigned8",
                         parser.parse(0x600, client_download_segment,
                                      self.eds_data),
                         "Error on Client End Message")
        self.assertEqual(False, parser.is_complete,
                         "Parser should be incomplete")

        server_download_response = [0x30, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                    0x00]
        self.assertEqual("Identity unsigned8 XXX%",
                         parser.parse(0x580, server_download_response,
                                      self.eds_data),
                         "Error on Server End Message")
        self.assertEqual(False, parser.is_complete,
                         "Parser should be incomplete")

        client_download_segment = [0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                   0x0A]
        self.assertEqual("Block download done - Identity unsigned8",
                         parser.parse(0x600, client_download_segment,
                                      self.eds_data),
                         "Error on Client End Message")
        self.assertEqual(False, parser.is_complete,
                         "Parser should be incomplete")

        server_download_response = [0x20, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                    0x00]
        self.assertEqual("Identity unsigned8 100%",
                         parser.parse(0x580, server_download_response,
                                      self.eds_data),
                         "Error on Server End Message")
        self.assertEqual(True, parser.is_complete, "Parser should be complete")

    def test_normal_transfer_multiple_segments_with_size_upload(self):
        """
        Test Normal SDO transfer with size indicated (Data not returned)
        This test is using the upload order (data from client not server)
        """
        parser = SDOParser()

        client_initiate_message = [0x40, 0x10, 0x18, 0x00, 0x00, 0x00, 0x00,
                                   0x00]
        self.assertEqual("Identity unsigned8 0%",
                         parser.parse(0x600, client_initiate_message,
                                      self.eds_data),
                         "Error on Client Initiate Message")
        self.assertEqual(False, parser.is_complete,
                         "Parser should be incomplete")

        server_initiate_response = [0x41, 0x10, 0x18, 0x00, 0x00, 0x00, 0x00,
                                    0x10]
        self.assertEqual("Initiating block download - Identity unsigned8",
                         parser.parse(0x580, server_initiate_response,
                                      self.eds_data),
                         "Error on Server Initiate Message")
        self.assertEqual(False, parser.is_complete,
                         "Parser should be incomplete")

        client_download_segment = [0x70, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                   0x00]
        self.assertEqual("Identity unsigned8 50.0%",
                         parser.parse(0x600, client_download_segment,
                                      self.eds_data),
                         "Error on Client End Message")
        self.assertEqual(False, parser.is_complete,
                         "Parser should be incomplete")

        server_download_response = [0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                    0x0A]
        self.assertEqual("Block downloading - Identity unsigned8",
                         parser.parse(0x580, server_download_response,
                                      self.eds_data),
                         "Error on Server End Message")
        self.assertEqual(False, parser.is_complete,
                         "Parser should be incomplete")

        client_download_segment = [0x60, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                   0x00]
        self.assertEqual("Identity unsigned8 50.0%",
                         parser.parse(0x600, client_download_segment,
                                      self.eds_data),
                         "Error on Client End Message")
        self.assertEqual(False, parser.is_complete,
                         "Parser should be incomplete")

        server_download_response = [0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                    0x0A]
        self.assertEqual("Block download done - Identity unsigned8",
                         parser.parse(0x580, server_download_response,
                                      self.eds_data),
                         "Error on Server End Message")
        self.assertEqual(True, parser.is_complete, "Parser should be complete")

    def test_expedited_unsigned_int_upload(self):
        """
        Test expedited SDO transfer with an unsigned int data type
        """
        parser = SDOParser()
        client_initiate_message = [0x40, 0x10, 0x18, 0x00, 0x00, 0x00, 0x00,
                                   0x00]
        self.assertEqual("Identity unsigned8 0%",
                         parser.parse(0x600, client_initiate_message,
                                      self.eds_data),
                         "Error on Client Initiate Message")
        self.assertEqual(False, parser.is_complete,
                         "Parser should be incomplete")

        server_initiate_response = [0x47, 0x10, 0x18, 0x00, 0x0A, 0x00, 0x00,
                                    0x00]
        self.assertEqual("Downloaded - Identity unsigned8: 10",
                         parser.parse(0x580, server_initiate_response,
                                      self.eds_data),
                         "Error on Server Initiate Response")
        self.assertEqual(True, parser.is_complete, "Parser should be complete")

    def test_sdo_block_download(self):
        """
        Test SDO Block Upload

        Upload 8byte unsigned integer with value 10
        """
        parser = SDOParser()
        client_initiate_message = [0xE6, 0x10, 0x18, 0x00, 0x00, 0x00, 0x00,
                                   0x08]
        self.assertEqual("Initiating block download - Identity unsigned8",
                         parser.parse(0x600, client_initiate_message,
                                      self.eds_data),
                         "Error on Client Initiate Message")
        self.assertEqual(False, parser.is_complete,
                         "Parser should be incomplete")

        server_initiate_response = [0xC4, 0x10, 0x18, 0x00, 0x02, 0x00, 0x00,
                                    0x00]
        self.assertEqual("Identity unsigned8 0%",
                         parser.parse(0x580, server_initiate_response,
                                      self.eds_data),
                         "Error on Server Initiate Message")
        self.assertEqual(False, parser.is_complete,
                         "Parser should be incomplete")

        client_block1_message = [0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        self.assertEqual("Block downloading - Identity unsigned8",
                         parser.parse(0x600, client_block1_message,
                                      self.eds_data),
                         "Error on Client Block1 Message")
        self.assertEqual(False, parser.is_complete,
                         "Parser should be incomplete")

        client_block2_message = [0x82, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        self.assertEqual("Block downloading - Identity unsigned8",
                         parser.parse(0x600, client_block2_message,
                                      self.eds_data),
                         "Error on Client Block1 Message")
        self.assertEqual(False, parser.is_complete,
                         "Parser should be incomplete")

        server_block_confirm_message = [0xA2, 0x02, 0x08, 0x00, 0x00, 0x00,
                                        0x00, 0x00]
        self.assertEqual("Identity unsigned8 100.0%",
                         parser.parse(0x580, server_block_confirm_message,
                                      self.eds_data),
                         "Error on Server End Message")
        self.assertEqual(False, parser.is_complete,
                         "Parser should be incomplete")

        client_block_end_message = [0xDD, 0xA1, 0x4A, 0x00, 0x00, 0x00, 0x00,
                                    0x00]
        self.assertEqual("Identity unsigned8 100%",
                         parser.parse(0x600, client_block_end_message,
                                      self.eds_data),
                         "Error on Client End Message")
        self.assertEqual(False, parser.is_complete,
                         "Parser should be incomplete")

        server_block_end_confirm_message = [0xA1, 0x00, 0x00, 0x00, 0x00, 0x00,
                                            0x00, 0x00]
        self.assertEqual("Block download done - Identity unsigned8",
                         parser.parse(0x580, server_block_end_confirm_message,
                                      self.eds_data),
                         "Error on Server End Message")
        self.assertEqual(True, parser.is_complete, "Parser should be complete")

    def test_sdo_block_upload(self):
        """
        Test SDO Block Download

        Download 8byte unsigned integer with value 10
        """
        parser = SDOParser()
        client_initiate_message = [0xA4, 0x10, 0x18, 0x00, 0x02, 0x00, 0x00,
                                   0x00]
        self.assertEqual("Identity unsigned8 0%",
                         parser.parse(0x600, client_initiate_message,
                                      self.eds_data),
                         "Error on Client Initiate Message")
        self.assertEqual(False, parser.is_complete,
                         "Parser should be incomplete")

        server_initiate_response = [0xE6, 0x10, 0x18, 0x00, 0x00, 0x00, 0x00,
                                    0x08]
        self.assertEqual("Initiating block download - Identity unsigned8",
                         parser.parse(0x580, server_initiate_response,
                                      self.eds_data),
                         "Error on Server Initiate Message")
        self.assertEqual(False, parser.is_complete,
                         "Parser should be incomplete")

        server_initiate_response = [0xA3, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                    0x00]
        self.assertEqual("Initiating block download - Identity unsigned8",
                         parser.parse(0x580, server_initiate_response,
                                      self.eds_data),
                         "Error on Server Initiate Message")
        self.assertEqual(False, parser.is_complete,
                         "Parser should be incomplete")

        server_block1_message = [0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        self.assertEqual("Block downloading - Identity unsigned8",
                         parser.parse(0x580, server_block1_message,
                                      self.eds_data),
                         "Error on Server Block1 Message")
        self.assertEqual(False, parser.is_complete,
                         "Parser should be incomplete")

        server_block2_message = [0x82, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        self.assertEqual("Block downloading - Identity unsigned8",
                         parser.parse(0x580, server_block2_message,
                                      self.eds_data),
                         "Error on Server Block2 Message")
        self.assertEqual(False, parser.is_complete,
                         "Parser should be incomplete")

        client_block_confirm_message = [0xA2, 0x02, 0x08, 0x00, 0x00, 0x00,
                                        0x00, 0x00]
        self.assertEqual("Identity unsigned8 100.0%",
                         parser.parse(0x600, client_block_confirm_message,
                                      self.eds_data),
                         "Error on Client Confirm Block Message")
        self.assertEqual(False, parser.is_complete,
                         "Parser should be incomplete")

        server_block_end_message = [0xDD, 0xA1, 0x4A, 0x00, 0x00, 0x00, 0x00,
                                    0x00]
        self.assertEqual("Identity unsigned8 100%",
                         parser.parse(0x580, server_block_end_message,
                                      self.eds_data),
                         "Error on Server End Message")
        self.assertEqual(False, parser.is_complete,
                         "Parser should be incomplete")

        client_block_end_confirm_message = [0xA1, 0x00, 0x00, 0x00, 0x00, 0x00,
                                            0x00, 0x00]
        self.assertEqual("Block download done - Identity unsigned8",
                         parser.parse(0x600, client_block_end_confirm_message,
                                      self.eds_data),
                         "Error on Server End Message")
        self.assertEqual(True, parser.is_complete, "Parser should be complete")

    def test_invalid_payload(self):
        """
        Text expedited SDO transfer with an unsigned int data type
        """
        parser = SDOParser()
        message = []
        with self.assertRaises(FailedValidationError) as context:
            parser.parse(0x580, message, self.eds_data)

        self.assertEqual("Invalid SDO payload length, expected 8, received "
                          "0", str(context.exception))
