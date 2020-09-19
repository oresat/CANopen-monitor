import os
import shutil
import unittest
import canopen_monitor
import canopen_monitor.utilities as utils


class TestUtilities(unittest.TestCase):
    def setUp(self):
        """
        Overload canopen_monitor config paths to build a dummy environment
        """
        self.skipTest("This is still in progress")
        canopen_monitor.CONFIG_DIR = os.path.abspath('tests/config-env') \
            + os.sep
        canopen_monitor.CONFIG_DIR = canopen_monitor.CONFIG_DIR \
            + 'devices.json'
        canopen_monitor.LAYOUT_CONFIG = canopen_monitor.LAYOUT_CONFIG \
            + 'layout.json'
        canopen_monitor.NODES_CONFIG = canopen_monitor.NODES_CONFIG \
            + 'nodes.json'

        utils.generate_config_dirs()

    def tearDown(self):
        """
        Ensure test environment is cleared out.
        """
        shutil.rmtree(canopen_monitor.CONFIG_DIR)

    def test_config_dir_generator_good(self):
        """
        Test that `generate_config_dirs()` correctly generates
        the config dirs needed.
        """
        self.assertTrue(os.path.exists(canopen_monitor.CONFIG_DIR))

    def test_generate_devices_good(self):
        """
        Test that the config factory cad succesfully generate
        the default devices config and that it can be read back.
        """
        expected = ['can0']
        utils.config_factory(canopen_monitor.DEVICES_CONFIG)
        config = utils.load_config(canopen_monitor.DEVICES_CONFIG)
        self.assertEqual(expected, config)

    def test_generate_node_good(self):
        """
        Test that the config factory cad succesfully generate
        the default node name override config and that it can be read back.
        """
        expected = {'64': "MDC"}
        utils.config_factory(canopen_monitor.NODES_CONFIG)
        config = utils.load_config(canopen_monitor.NODES_CONFIG)
        self.assertEqual(expected, config)

    def test_generate_layout_good(self):
        """
        Test that the config factory cad succesfully generate
        the default node name override config and that it can be read back.
        """
        expected = {
            'type': 'grid',
            'split': 'horizontal',
            'data': [{
                'type': 'grid',
                'split': 'vertical',
                'data': [{
                            'type': 'table',
                            'capacity': 16,
                            'dead_node_timeout': 600,
                            'name': 'Hearbeats',
                            'stale_node_timeout': 60,
                            'fields': [],
                            'frame_types': ['HB']
                        }, {
                            'type': 'table',
                            'capacity': 16,
                            'dead_node_timeout': 600,
                            'name': 'Info',
                            'stale_node_timeout': 60,
                            'fields': [],
                            'frame_types': []
                        }]
            }, {
                'type': 'table',
                'capacity': 16,
                'dead_node_timeout': 60,
                'name': 'Misc',
                'stale_node_timeout': 600,
                'fields': [],
                'frame_types': [
                    'NMT',
                    'SYNC',
                    'EMCY',
                    'TIME',
                    'TPDO1',
                    'RPDO1',
                    'TPDO2',
                    'RPDO2',
                    'TPDO3',
                    'RPDO3',
                    'TPDO4',
                    'RPDO4',
                    'TSDO',
                    'RSDO',
                    'UKOWN'
                ]
            }]}
        utils.config_factory(canopen_monitor.LAYOUT_CONFIG)
        config = utils.load_config(canopen_monitor.LAYOUT_CONFIG)
        self.assertEqual(expected, config)
