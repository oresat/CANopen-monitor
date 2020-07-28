import os
import shutil
import unittest
import monitor
import monitor.utilities as utils


class TestUtilities(unittest.TestCase):
    def setUp(self):
        """
        Overload monitor config paths to build a dummy environment
        """
        monitor.CANMONITOR_CONFIG_DIR = os.path.abspath('tests/config-env') \
            + os.sep
        monitor.CANMONITOR_DEVICES_CONFIG = monitor.CANMONITOR_CONFIG_DIR \
            + 'devices.json'
        monitor.CANMONITOR_LAYOUT_CONFIG = monitor.CANMONITOR_CONFIG_DIR \
            + 'layout.json'
        monitor.CANMONITOR_NODES_CONFIG = monitor.CANMONITOR_CONFIG_DIR \
            + 'nodes.json'

        utils.generate_config_dirs()

    def tearDown(self):
        """
        Ensure test environment is cleared out.
        """
        shutil.rmtree(monitor.CANMONITOR_CONFIG_DIR)

    def test_config_dir_generator_good(self):
        """
        Test that `generate_config_dirs()` correctly generates
        the config dirs needed.
        """
        self.assertTrue(os.path.exists(monitor.CANMONITOR_CONFIG_DIR))

    def test_generate_devices_good(self):
        """
        Test that the config factory cad succesfully generate
        the default devices config and that it can be read back.
        """
        expected = ['can0']
        utils.config_factory(monitor.CANMONITOR_DEVICES_CONFIG)
        config = utils.load_config(monitor.CANMONITOR_DEVICES_CONFIG)
        self.assertEqual(expected, config)

    def test_generate_node_good(self):
        """
        Test that the config factory cad succesfully generate
        the default node name override config and that it can be read back.
        """
        expected = {'64': "MDC"}
        utils.config_factory(monitor.CANMONITOR_NODES_CONFIG)
        config = utils.load_config(monitor.CANMONITOR_NODES_CONFIG)
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
        utils.config_factory(monitor.CANMONITOR_LAYOUT_CONFIG)
        config = utils.load_config(monitor.CANMONITOR_LAYOUT_CONFIG)
        self.assertEqual(expected, config)
