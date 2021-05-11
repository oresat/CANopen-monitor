import unittest
from unittest.mock import mock_open, patch, MagicMock, call
from canopen_monitor.meta import Meta


class TestMeta(unittest.TestCase):
    """
    Tests for the Meta Class
    """
    def setUp(self) -> None:
        self.meta = Meta("config_dir", "cache_dir")
        self.mcb = MagicMock()

    def test_save_single_device(self):
        """
        Test Save a single Device
        """
        self.mcb.interface_list = ["vcan0"]
        with patch('builtins.open', mock_open()) as m:
            self.meta.save_devices(self.mcb)

        m.assert_called_once_with('config_dir/interfaces.json', 'w')
        calls = [call('{'),
                 call('"interfaces"'),
                 call(': '),
                 call('["vcan0"'),
                 call(']'),
                 call('}')]

        self.assertEqual(calls, m().write.mock_calls,
                         "json file not written out correctly")

    def test_save_multiple_device(self):
        """
        Test Save Multiple Devices
        """
        self.mcb.interface_list = ["vcan0", "vcan1"]
        with patch('builtins.open', mock_open()) as m:
            self.meta.save_devices(self.mcb)

        m.assert_called_once_with('config_dir/interfaces.json', 'w')
        calls = [call('{'),
                 call('"interfaces"'),
                 call(': '),
                 call('["vcan0"'),
                 call(', "vcan1"'),
                 call(']'),
                 call('}')]

        self.assertEqual(calls, m().write.mock_calls,
                         "json file not written out correctly")

    def test_save_no_device(self):
        """
        Test Save No Devices
        """
        self.mcb.interface_list = []
        with patch('builtins.open', mock_open()) as m:
            self.meta.save_devices(self.mcb)

        m.assert_called_once_with('config_dir/interfaces.json', 'w')
        calls = [call('{'),
                 call('"interfaces"'),
                 call(': '),
                 call('[]'),
                 call('}')]

        self.assertEqual(calls, m().write.mock_calls,
                         "json file not written out correctly")

        m().truncate.assert_called_once()

    def test_load_single_device(self):
        """
        Test load a single Device
        """

        json = '{"interfaces": ["vcan0"]}'
        with patch('builtins.open', mock_open(read_data=json)) as m:
            with patch('os.path.isfile', return_value=True) as m_os:
                devices = self.meta.load_devices([])

        m.assert_called_once_with('config_dir/interfaces.json', 'r')
        m_os.assert_called_once_with('config_dir/interfaces.json')
        self.assertEqual(["vcan0"], devices,
                         "Devices not loaded correctly")

    def test_load_multiple_devices(self):
        """
        Test load of multiple Device
        """

        json = '{"interfaces": ["vcan0", "vcan1"]}'
        with patch('builtins.open', mock_open(read_data=json)) as m:
            with patch('os.path.isfile', return_value=True) as m_os:
                devices = self.meta.load_devices([])

        m.assert_called_once_with('config_dir/interfaces.json', 'r')
        m_os.assert_called_once_with('config_dir/interfaces.json')
        self.assertEqual(["vcan0", "vcan1"], devices,
                         "Devices not loaded correctly")

    def test_load_no_devices(self):
        """
        Test load of no Devices
        """

        json = '{"interfaces": []}'
        with patch('builtins.open', mock_open(read_data=json)) as m:
            with patch('os.path.isfile', return_value=True) as m_os:
                devices = self.meta.load_devices([])

        m.assert_called_once_with('config_dir/interfaces.json', 'r')
        m_os.assert_called_once_with('config_dir/interfaces.json')
        self.assertEqual([], devices,
                         "Devices not loaded correctly")

    def test_load_no_file(self):
        """
        Test load with no existing file
        """

        with patch('os.path.isfile', return_value=False) as m_os:
            devices = self.meta.load_devices([])

        m_os.assert_called_once_with('config_dir/interfaces.json')
        self.assertEqual([], devices,
                         "Devices not loaded correctly")