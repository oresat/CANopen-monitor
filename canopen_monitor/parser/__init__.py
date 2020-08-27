import enum

emergency_error_codes = {
    0x0000: "Error reset or no error",
    0x1000: "Generic error",
    0x2000: "Current –generic error",
    0x2100: "Current, CANopen device input side –generic",
    0x2200: "Current inside the CANopen device –generic",
    0x2300: "Current, CANopen device output side –generic",
    0x3000: "Voltage –generic error",
    0x3100: "Mains voltage –generic",
    0x3200: "Voltage inside the CANopen device –generic",
    0x3300: "Outputvoltage –generic",
    0x4000: "Temperature –generic error",
    0x4100: "Ambient temperature –generic",
    0x4200: "Device temperature –generic",
    0x5000: "CANopen device hardware –generic error",
    0x6000: "CANopen device software –generic error",
    0x6100: "Internal software –generic",
    0x6200: "User software –generic",
    0x6300: "Data set –generic",
    0x7000: "Additional modules –generic error",
    0x8000: "Monitoring –generic error",
    0x8100: "Communication –generic",
    0x8110: "CAN overrun (objects lost)",
    0x8120: "CAN in error passive mode",
    0x8130: "Life guard error or heartbeat error",
    0x8140: "recovered from bus off",
    0x8150: "CAN-ID collision",
    0x8200: "Protocol error -generic",
    0x8210: "PDO not processed due to length error",
    0x8220: "PDO length exceeded",
    0x8230: "DAM MPDO not processed, destination object not available",
    0x8240: "Unexpected SYNC data length",
    0x8250: "RPDO timeout",
    0x9000: "External error –generic error",
    0xF000: "Additional functions –generic error",
    0xFF00: "Device specific –generic error",
}

node_names = {0x01: "C3",
              0x06: "Solar Panel",
              0x11: "SDR GPS",
              0x12: "Star Tracker",
              0x21: "OreSat Live",
              0x22: "Cirrus Flux Cameras",
              0x31: "Battery",
              0x32: "Test Board 1",
              0x33: "Test Board 2",
              0x40: "MDC"}

heartbeat_statuses = {0x00: "Initializing",
                      0x04: "Stopped",
                      0x05: "Operational",
                      0x7f: "Pre-Operational"}

data_types = {0x01: "BOOLEAN",
              0x02: "INTEGER8",
              0x03: "INTEGER16",
              0x04: "INTEGER32",
              0x05: "UNSIGNED8",
              0x06: "UNSIGNED16",
              0x07: "UNSIGNED32",
              0x08: "REAL32",
              0x09: "VISIBLE_STRING",
              0x0A: "OCTET_STRING",
              0x0B: "UNICODE_STRING",
              0x0F: "DOMAIN",
              0x11: "REAL64",
              0x15: "INTEGER64",
              0x1B: "UNSIGNED64"}


class DataTypes(enum.Enum):
    BOOLEAN = 0x1
    INTEGER8 = 0x2
    INTEGER16 = 0x3
    INTEGER32 = 0x4
    UNSIGNED8 = 0x5
    UNSIGNED16 = 0x6
    UNSIGNED32 = 0x7
    REAL32 = 0x8
    VISIBLE_STRING = 0x9
    OCTET_STRING = 0xA
    UNICODE_STRING = 0xB
    DOMAIN = 0xF
    REAL64 = 0x11
    INTEGER64 = 0x15
    UNSIGNED64 = 0x1B


object_types = {0x00: "NULL",
                0x02: "DOMAIN",
                0x05: "DEFTYPE",
                0x06: "DEFSTRUCT",
                0x07: "VAR",
                0x08: "ARRAY",
                0x09: "RECORD"}
