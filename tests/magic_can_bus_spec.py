import unittest
import canopen_monitor.canmsgs.magic_can_bus as mcb


class TestMagicCanBus(unittest.TestCase):
    def setUp(self):
        """
        Setup the CAN Bus listners
        """
        self.bus = mcb.MagicCANBus()

    def tearDown(self):
        """
        Ensure the CAN Bus listeners are shut down
        """
        self.bus.stop_all()

    def test_start_device_good(self):
        """
        Test that `listen()` correctly creates a listener for `vcan0`
        """
        self.skipTest('Revisit upon figuring out mock sockets.')
        dev = 'vcan0'
        self.bus.start(dev)
        dev_names = list(map(lambda x: x.ndev, self.bus.running()))
        self.assertIn(dev, dev_names)

    def test_receive_is_empty_no_bus(self):
        """
        Test that the Magic Can Bus returns None when no bus is initialized and no messages exist on the CAN bus.
        """
        res = self.bus.receive()
        self.assertIsNone(res)
