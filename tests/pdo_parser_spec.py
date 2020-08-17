import unittest
from unittest.mock import MagicMock

from monitor.parser.pdo import *


class TestPDO(unittest.TestCase):
    """
    Tests for the SDO parser
    """

    def setUp(self):
        """
        Generate Mocked eds file
        """
        # 1A00 - TPDO with 1 mapped object
        self.index_1A00_0 = MagicMock(access_type='ro', data_type='0x0005', default_type=1, id=0x1A00, object_type='0x7'
                                      , parameter_name='Number of mapped objects', sub_id=0, default_value=1)

        self.index_1A00_1 = MagicMock(access_type='rw', data_type='0x0007', id=0x1A00, object_type='0x7',
                                      parameter_name='mapped object 1', sub_id=0, default_value=0x31010320)

        self.index_1A00 = MagicMock(id='1A00', parameter_name='TPDO mapping parameter', object_type='0x9',
                                    sub_number='0x5',
                                    sub_indices=[self.index_1A00_0, self.index_1A00_1])

        # 1A01 - TPDO with 2 mapped objects
        self.index_1A01_0 = MagicMock(access_type='ro', data_type='0x0005', default_type=1, id=0x1A01, object_type='0x7'
                                      , parameter_name='Number of mapped objects', sub_id=0, default_value=2)

        self.index_1A01_1 = MagicMock(access_type='rw', data_type='0x0007', id=0x1A00, object_type='0x7',
                                      parameter_name='mapped object 1', sub_id=0, default_value=0x31010320)

        self.index_1A01_2 = MagicMock(access_type='rw', data_type='0x0007', id=0x1A00, object_type='0x7',
                                      parameter_name='mapped object 1', sub_id=0, default_value=0x31010420)

        self.index_1A01 = MagicMock(id=0x1A01, parameter_name='TPDO mapping parameter', object_type='0x9',
                                    sub_number='0x5',
                                    sub_indices=[self.index_1A01_0, self.index_1A01_1, self.index_1A01_2])

        # 1A02 - MPDO SAM mapping
        self.index_1A02_0 = MagicMock(access_type='ro', data_type='0x0005', default_type=1, id=0x1A02, object_type='0x7'
                                      , parameter_name='Number of mapped objects', sub_id=0, default_value=0xFE)

        self.index_1A02 = MagicMock(id=0x1A02, parameter_name='TPDO mapping parameter', object_type='0x9',
                                    sub_number='0x5',
                                    sub_indices=[self.index_1A02_0])

        # 1A03 - MPDO DAM mapping
        self.index_1A03_0 = MagicMock(access_type='ro', data_type='0x0005', default_type=1, id=0x1A03, object_type='0x7'
                                      , parameter_name='Number of mapped objects', sub_id=0, default_value=0xFF)

        self.index_1A03 = MagicMock(id=0x1A03, parameter_name='TPDO mapping parameter', object_type='0x9',
                                    sub_number='0x5',
                                    sub_indices=[self.index_1A03_0])

        # 3101 orientation
        self.index_3101_0 = MagicMock(access_type='ro', data_type='0x0005', default_type=1, id=0x3101, object_type='0x7',
                                      parameter_name='max sub-index', sub_id=0, default_value=4)

        self.index_3101_1 = MagicMock(access_type='ro', data_type='0x0008', default_type=4, id=0x3101, object_type='0x7',
                                      parameter_name='declination', sub_id=0, default_value=0)

        self.index_3101_2 = MagicMock(access_type='ro', data_type='0x0008', default_type=4, id=0x3101, object_type='0x7',
                                      parameter_name='right ascension', sub_id=0, default_value=0)

        self.index_3101_3 = MagicMock(access_type='ro', data_type='0x0008', default_type=4, id=0x3101, object_type='0x7',
                                      parameter_name='orientation', sub_id=0, default_value=0)

        self.index_3101_4 = MagicMock(access_type='ro', data_type='0x0008', default_type=4, id=0x3101, object_type='0x7',
                                      parameter_name='timestamp', sub_id=0, default_value=0)

        self.index_3101 = MagicMock(id=0x3101, parameter_name='Orientation', object_type='0x9', sub_number='0x5',
                                    sub_indices=[self.index_3101_0, self.index_3101_1, self.index_3101_2,
                                                 self.index_3101_3, self.index_3101_4])

        def get_index(index):
            if index == 0x1A00:
                return self.index_1A00
            elif index == 0x1A01:
                return self.index_1A01
            elif index == 0x1A02:
                return self.index_1A02
            elif index == 0x3101:
                return self.index_3101
            else:
                raise KeyError(f"Incorrect index retrieved from EDS {index} provided")

        self.eds_data = MagicMock()
        self.eds_data.__getitem__.side_effect = get_index

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
