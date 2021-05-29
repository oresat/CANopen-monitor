import unittest
from unittest.mock import mock_open, patch, MagicMock, call
from canopen_monitor.meta import Meta, load_config, Config, InterfaceConfig, FeatureConfig


class TestMeta(unittest.TestCase):
    """
    Tests for the Meta Class
    """
    def setUp(self) -> None:
        self.meta = Meta("config_dir", "cache_dir")
        self.mcb = MagicMock()

    def test_save_single_interface(self):
        """
        Test Save a single interface
        """
        self.mcb.interface_list = ["vcan0"]
        with patch('builtins.open', mock_open()) as m:
            self.meta.save_interfaces(self.mcb)

        m.assert_called_once_with('config_dir/interfaces.json', 'w')
        calls = [call('{'),
                 call('\n    '),
                 call('"version"'),
                 call(': '),
                 call(f'"{InterfaceConfig.MAJOR}.{InterfaceConfig.MINOR}"'),
                 call(',\n    '),
                 call('"interfaces"'),
                 call(': '),
                 call('[\n        "vcan0"'),
                 call('\n    '),
                 call(']'),
                 call('\n'),
                 call('}')]

        self.assertEqual(calls, m().write.mock_calls,
                         "json file not written out correctly")

    def test_save_multiple_interface(self):
        """
        Test Save Multiple interfaces
        """
        self.mcb.interface_list = ["vcan0", "vcan1"]
        with patch('builtins.open', mock_open()) as m:
            self.meta.save_interfaces(self.mcb)

        m.assert_called_once_with('config_dir/interfaces.json', 'w')
        calls = [call('{'),
                 call('\n    '),
                 call('"version"'),
                 call(': '),
                 call(f'"{InterfaceConfig.MAJOR}.{InterfaceConfig.MINOR}"'),
                 call(',\n    '),
                 call('"interfaces"'),
                 call(': '),
                 call('[\n        "vcan0"'),
                 call(',\n        "vcan1"'),
                 call('\n    '),
                 call(']'),
                 call('\n'),
                 call('}')]

        self.assertEqual(calls, m().write.mock_calls,
                         "json file not written out correctly")

    def test_save_no_interface(self):
        """
        Test Save No interfaces
        """
        self.mcb.interface_list = []
        with patch('builtins.open', mock_open()) as m:
            self.meta.save_interfaces(self.mcb)

        m.assert_called_once_with('config_dir/interfaces.json', 'w')
        calls = [call('{'),
                 call('\n    '),
                 call('"version"'),
                 call(': '),
                 call(f'"{InterfaceConfig.MAJOR}.{InterfaceConfig.MINOR}"'),
                 call(',\n    '),
                 call('"interfaces"'),
                 call(': '),
                 call('[]'),
                 call('\n'),
                 call('}')]

        self.assertEqual(calls, m().write.mock_calls,
                         "json file not written out correctly")

        m().truncate.assert_called_once()

    def test_load_single_interface(self):
        """
        Test load a single interface
        """

        json = '{"interfaces": ["vcan0"]}'
        with patch('builtins.open', mock_open(read_data=json)) as m:
            with patch('os.path.isfile', return_value=True) as m_os:
                interfaces = self.meta.load_interfaces([])

        m.assert_called_once_with('config_dir/interfaces.json', 'r')
        m_os.assert_called_once_with('config_dir/interfaces.json')
        self.assertEqual(["vcan0"], interfaces,
                         "interfaces not loaded correctly")

    def test_load_multiple_interfaces(self):
        """
        Test load of multiple interface
        """

        json = '{"interfaces": ["vcan0", "vcan1"]}'
        with patch('builtins.open', mock_open(read_data=json)) as m:
            with patch('os.path.isfile', return_value=True) as m_os:
                interfaces = self.meta.load_interfaces([])

        m.assert_called_once_with('config_dir/interfaces.json', 'r')
        m_os.assert_called_once_with('config_dir/interfaces.json')
        self.assertEqual(["vcan0", "vcan1"], interfaces,
                         "interfaces not loaded correctly")

    def test_load_no_interfaces(self):
        """
        Test load of no interfaces
        """

        json = '{"interfaces": []}'
        with patch('builtins.open', mock_open(read_data=json)) as m:
            with patch('os.path.isfile', return_value=True) as m_os:
                interfaces = self.meta.load_interfaces([])

        m.assert_called_once_with('config_dir/interfaces.json', 'r')
        m_os.assert_called_once_with('config_dir/interfaces.json')
        self.assertEqual([], interfaces,
                         "interfaces not loaded correctly")

    def test_load_no_interfaces_file(self):
        """
        Test load with no existing file
        """

        with patch('builtins.open', mock_open()) as m:
            with patch('os.path.isfile', return_value=False) as m_os:
                interfaces = self.meta.load_interfaces([])

            m_os.assert_called_once_with('config_dir/interfaces.json')
            self.assertEqual([], interfaces,
                             "interfaces not loaded correctly")

    def test_load_features(self):
        """
        Test loading features from feature file
        :return:
        """
        json = f'{{"major": {FeatureConfig.MAJOR}, "minor": {FeatureConfig.MINOR}, "ecss_time": true }}'
        with patch('builtins.open', mock_open(read_data=json)) as m:
            with patch('os.path.isfile', return_value=True) as m_os:
                features = self.meta.load_features()

        m.assert_called_once_with('config_dir/features.json', 'r')
        m_os.assert_called_once_with('config_dir/features.json')
        self.assertEqual(True, features.ecss_time,
                         "features not loaded correctly")

    def test_replace_breaking_config(self):
        """
        Test loading an existing file with a breaking version
        Should create a backup and save a new file with defaults
        :return:
        """
        def isfile(filename):
            if filename == "filename":
                return True
            else:
                return False

        isfileMock = MagicMock(side_effect=isfile)
        with patch('builtins.open', mock_open()) as m:
            with patch('os.path.isfile', isfileMock) as m_os:
                with patch('os.rename') as m_os_rename:
                    config = Config(0, 0)
                    load_config("filename", config)

        m_os.assert_has_calls([call("filename"), call("filename.bak")])
        m_os_rename.assert_called_once_with('filename', 'filename.bak')
        m.assert_called_with('filename', 'w')

    def test_replace_breaking_config_with_existing_bak(self):
        """
        Test loading an existing file with a breaking version
        when an existing .bak file exists
        :return:
        """

        def isfile(filename):
            if filename == "filename" or filename == "filename.bak" or filename == "filename-1.bak":
                return True
            else:
                return False

        isfileMock = MagicMock(side_effect=isfile)
        with patch('builtins.open', mock_open()) as m:
            with patch('os.path.isfile', isfileMock) as m_os:
                with patch('os.rename') as m_os_rename:
                    config = Config(0, 0)
                    load_config("filename", config)

        m_os.assert_has_calls([call("filename"), call("filename.bak"), call("filename-1.bak")])
        m_os_rename.assert_called_once_with('filename', 'filename-2.bak')
        m.assert_called_with('filename', 'w')
