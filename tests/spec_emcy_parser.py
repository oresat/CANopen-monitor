import unittest
from canopen_monitor.parse.emcy import parse
from canopen_monitor.parse.utilities import FailedValidationError


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
                         parse(0, emcy_message, 0),
                         "Error on EMCY Message parse")

    def test_EMCY_invalid(self):
        """
        Test EMCY Message with undefined message
        """
        emcy_message = [0x81, 0x11, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0]
        self.assertEqual("Error code not found",
                         parse(0, emcy_message, 0),
                         "Error on EMCY Message parse with undefined error "
                         "message")

    def test_EMCY_invalid_length(self):
        """
        Test EMCY Message with undefined message
        """
        emcy_message = [0x81, 0x11, 0x0]
        with self.assertRaises(FailedValidationError) as context:
            parse(0, emcy_message, 0)

        self.assertEqual("Invalid EMCY message length", str(context.exception))
