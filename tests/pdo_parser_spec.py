import unittest
from unittest.mock import MagicMock

from monitor.parser.pdo import *
from monitor.parser.eds import *


class TestPDO(unittest.TestCase):
    """
    Tests for the SDO parser
    """

    def setUp(self):
        """
        Generate Mocked eds file
        """
        self.index_1A00_0 = MagicMock(access_type='ro', data_type='0x0005', default_type=1, id='1A00', object_type='0x7'
                                      , parameter_name='Number of mapped objects', sub_id=0, default_value=1)

        self.index_1A00_1 = MagicMock(access_type='rw', data_type='0x0007', id='1A00', object_type='0x7',
                                      parameter_name='mapped object 1', sub_id=0, default_value=0x31010320)

        self.index_1A00 = MagicMock(id='1A00', parameter_name='TPDO mapping parameter', object_type='0x9',
                                    sub_number='0x5',
                                    sub_indices=[self.index_1A00_0, self.index_1A00_1])

        self.index_1A01_0 = MagicMock(access_type='ro', data_type='0x0005', default_type=1, id='1A01', object_type='0x7'
                                      , parameter_name='Number of mapped objects', sub_id=0, default_value=2)

        self.index_1A01_1 = MagicMock(access_type='rw', data_type='0x0007', id='1A00', object_type='0x7',
                                      parameter_name='mapped object 1', sub_id=0, default_value=0x31010320)

        self.index_1A01_2 = MagicMock(access_type='rw', data_type='0x0007', id='1A00', object_type='0x7',
                                      parameter_name='mapped object 1', sub_id=0, default_value=0x31010420)

        self.index_1A01 = MagicMock(id='1A01', parameter_name='TPDO mapping parameter', object_type='0x9',
                                    sub_number='0x5',
                                    sub_indices=[self.index_1A01_0, self.index_1A01_1, self.index_1A01_2])

        self.index_3101_0 = MagicMock(access_type='ro', data_type='0x0005', default_type=1, id=3101, object_type='0x7',
                                      parameter_name='max sub-index', sub_id=0, default_value=4)

        self.index_3101_1 = MagicMock(access_type='ro', data_type='0x0008', default_type=4, id=3101, object_type='0x7',
                                      parameter_name='declination', sub_id=0, default_value=0)

        self.index_3101_2 = MagicMock(access_type='ro', data_type='0x0008', default_type=4, id=3101, object_type='0x7',
                                      parameter_name='right ascension', sub_id=0, default_value=0)

        self.index_3101_3 = MagicMock(access_type='ro', data_type='0x0008', default_type=4, id=3101, object_type='0x7',
                                      parameter_name='orientation', sub_id=0, default_value=0)

        self.index_3101_4 = MagicMock(access_type='ro', data_type='0x0008', default_type=4, id=3101, object_type='0x7',
                                      parameter_name='timestamp', sub_id=0, default_value=0)

        self.index_3101 = MagicMock(id=3101, parameter_name='Orientation', object_type='0x9', sub_number='0x5',
                                    sub_indices=[self.index_3101_0, self.index_3101_1, self.index_3101_2,
                                                 self.index_3101_3, self.index_3101_4])

        def get_index(index):
            if index == '1A00':
                return self.index_1A00
            elif index == '1A01':
                return self.index_1A01
            elif index == 3101:
                return self.index_3101
            else:
                raise KeyError(f"Incorrect index retrieved from EDS {index} provided")

        self.eds_data = MagicMock()
        self.eds_data.__getitem__.side_effect = get_index

    def test_pdo(self):
        """
        Text PDO transmit
        """
        parser = PDOParser()
        PDO_message = b'\x3F\x80\x00\x00'
        self.assertEqual("Orientation orientation - 1.0",
                         parser.parse(0x180, self.eds_data, PDO_message),
                         "Error on PDO Message parse")

    def test_pdo_with_multiple_elements(self):
        """
        Text PDO transmit
        """
        parser = PDOParser()
        PDO_message = b'\x3F\x80\x00\x00\x3F\xC0\x00\x00'
        self.assertEqual("Orientation orientation - 1.0\nOrientation timestamp - 1.5",
                         parser.parse(0x280, self.eds_data, PDO_message),
                         "Error on PDO Message parse (multiple)")


if __name__ == '__main__':
    unittest.main()
