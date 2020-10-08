import unittest
from canopen_monitor.parser.emcy import parse


class TestEMCY(unittest.TestCase):
    """
    Tests for the EMCY parser
    """

    def test_EMCY(self):
        """
        Test EMCY Message
        """
        emcy_message = [0x81, 0x10, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0]
        self.assertEqual("CAN overrun (objects lost)",
                         parse(None, emcy_message, None),
                         "Error on EMCY Message parse")

    def test_EMCY_invalid(self):
        """
        Test EMCY Message with undefined message
        """
        emcy_message = [0x81, 0x11, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0]
        self.assertEqual("Error code not found",
                         parse(None, emcy_message, None),
                         "Error on EMCY Message parse with undefined error "
                         "message")


if __name__ == '__main__':
    unittest.main()
