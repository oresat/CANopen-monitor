import unittest
import threading
from canopen_monitor import can
from unittest.mock import MagicMock


class MagicCanBus_Spec(unittest.TestCase):
    """Tests for the Magic Can Bus"""

    def setUp(self):
        # Fake CAN frame
        generic_frame = MagicMock()

        # Create fake interfaces
        if0 = MagicMock()
        if0.name = 'vcan0'
        if0.is_up = True
        if0.recv.return_value = generic_frame
        if0.__str__.return_value = 'vcan0'

        if1 = MagicMock()
        if1.name = 'vcan1'
        if1.is_up = False
        if1.recv.return_value = generic_frame
        if1.__str__.return_value = 'vcan1'

        # Setup the bus with no interfaces and then overide with the fakes
        self.bus = can.MagicCANBus([])
        self.bus.interfaces = [if0, if1]

    def test_statuses(self):
        """Given an MCB with 2 fake interfaces
        When calling the statuses proprty
        Then, the correct array of formatted tuples should be returned
        """
        statuses = self.bus.statuses
        self.assertEqual(statuses, [('vcan0', True), ('vcan1', False)])

    def test_handler(self):
        """Given an MCB with 2 interfaces
        When starting the bus listeners with a `with` block
        And calling the bus as an itterable
        Then the bus should start a separate thread and fill the queue with
        frames while the bus is open and then close the threads when the bus is
        closed
        """
        with self.bus as bus:
            for frame in bus:
                self.assertIsNotNone(frame)
        # Active threads should only be 1 by the end, 1 being the parent
        self.assertEqual(threading.active_count(), 1)

    def test_str(self):
        """Given an MCB with 2 interfaces
        When calling repr() on the bus
        Then it should return a correctly formated string representation
        of the bus
        """
        expected = 'Magic Can Bus: vcan0, vcan1, pending messages:' \
                   ' 0 threads: 0, keep-alive: True'
        actual = str(self.bus)
        self.assertEqual(expected, actual)
