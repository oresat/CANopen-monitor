from .eds import EDS
from .utilities import FailedValidationError


def parse(cob_id: int, data: list, eds: EDS):
    if len(data) != 8:
        raise FailedValidationError(data, cob_id-0x80, cob_id, __name__,
                                    "Invalid EMCY message length")
    message = EMCY(data)
    return message.error_message


class EMCY:
    """


 .. code-block:: python


     +-------+------+--------+
     |  eec  |  er  |  msef  |
     +-------+------+--------+
      0    1    2    3      7

 Definitions
 ===========
 * **eec**: Emergency Error Code
 * **er**: Error Register
 * **mcef**: Manufacturer Specific Error Code
     """

    def __init__(self, raw_sdo: list):
        self.__emergency_error_code = raw_sdo[0:2]
        self.__error_register = raw_sdo[2]
        self.__manufacturer_specific_error_code = raw_sdo[3:8]
        self.__error_message = determine_error_message(
            self.__emergency_error_code)

    @property
    def emergency_error_code(self):
        return self.__emergency_error_code

    @property
    def error_register(self):
        return self.__error_register

    @property
    def manufacturer_specific_error_code(self):
        return self.__manufacturer_specific_error_code

    @property
    def error_message(self):
        return self.__error_message


def determine_error_message(error_code: list):
    """
    Generic Emergency Error Codes are defined here, but application specific
    error codes can be defined as well
    """
    error_codes = {
        0x0000: "Error reset or no error",
        0x1000: "Generic error",
        0x2000: "Current = generic error",
        0x2100: "Current, CANopen device input side - generic",
        0x2200: "Current inside the CANopen device - generic",
        0x2300: "Current, CANopen device output side - generic",
        0x3000: "Voltage = generic error",
        0x3100: "Mains voltage - generic",
        0x3200: "Voltage inside the CANopen device - generic",
        0x3300: "Output voltage - generic",
        0x4000: "Temperature - generic error",
        0x4100: "Ambient temperature - generic",
        0x4200: "Device temperature - generic",
        0x5000: "CANopen device hardware - generic error",
        0x6000: "CANopen device software - generic error",
        0x6100: "Internal software - generic",
        0x6200: "User software - generic",
        0x6300: "Data set - generic",
        0x7000: "Additional modules - generic error",
        0x8000: "Monitoring - generic error",
        0x8100: "Communication - generic",
        0x8110: "CAN overrun (objects lost)",
        0x8120: "CAN in error passive mode",
        0x8130: "Life guard error on heartbeat error",
        0x8140: "recovered from bus off",
        0x8150: "CAN-ID collision",
        0x8200: "Protocol error - generic",
        0x8210: "PDO not processed due to length error",
        0x8220: "PDO length exceeded",
        0x8230: "DAM MPDO not processed, destination object not available",
        0x8240: "Unexpected SYNC data length",
        0x8250: "RPDO timeout",
        0x9000: "External error - generic error",
        0xF000: "Additional functions - generic error",
        0xFF00: "Device specific - generic error"
    }

    # Safe conversion to int ok, because data is bytes
    ebytes = list(map(lambda x: hex(x)[2:], error_code))
    error_id = int('0x' + ''.join(ebytes), 16)
    if error_id in error_codes.keys():
        return error_codes[error_id]
    else:
        return "Error code not found"
