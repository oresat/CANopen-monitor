import unittest

from monitor.parser.emcy import *


class TestEMCY(unittest.TestCase):
    """
    Tests for the EMCY parser
    """
    def test_EMCY(self):
        """
        Test EMCY Message
        """
        emcy_message = b'\x81\x10\x00\x00\x00\x00\x00\x00'
        self.assertEqual("CAN overrun (objects lost)",
                         parse(emcy_message),
                         "Error on EMCY Message parse")

    def test_EMCY_invalid(self):
        """
        Test EMCY Message with undefined message
        """
        emcy_message = b'\x81\x11\x00\x00\x00\x00\x00\x00'
        self.assertEqual("Error code not found",
                         parse(emcy_message),
                         "Error on EMCY Message parse with undefined error message")


if __name__ == '__main__':
    unittest.main()
