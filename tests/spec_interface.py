import unittest
from canopen_monitor import can
from unittest.mock import MagicMock, patch


class Interface_Spec(unittest.TestCase):
    """Tests for the Interface serial object"""

    @patch('psutil.net_if_stats')
    def setUp(self, net_if_stats):
        # Override the net_if_stats function from psutil
        net_if_stats.return_value = {'vcan0': {}}

        # Create a fake socket
        socket = MagicMock()
        socket.start.return_value = None

        # Create Interface
        self.iface = can.Interface('vcan0')
        self.iface.socket.close()
        self.iface.socket = socket

    @unittest.skip('Cannot patch psutil module')
    def test_active_loop(self):
        """Given a fake socket and an Interface
        When binding to the socket via a `with` block
        Then the socket should bind and the interface should change to the
        `UP` state and then shoud move to the `DOWN` state when exiting the
        `with` block
        """
        with self.iface as iface:
            self.assertTrue(iface.is_up)
        self.assertFalse(iface.is_up)
