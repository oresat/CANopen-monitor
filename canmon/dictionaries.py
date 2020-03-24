from enum import Enum

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


class DataTypes(Enum):
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
