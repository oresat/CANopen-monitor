import datetime
import enum
from re import finditer

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


def camel_to_snake(old_name: str) -> str:
    new_name = ''

    for match in finditer('[A-Z0-9]+[a-z]*', old_name):
        span = match.span()
        substr = old_name[span[0]:span[1]]
        length = span[1] - span[0]
        found_submatch = False

        for sub_match in finditer('[A-Z]+', substr):
            sub_span = sub_match.span()
            sub_substr = old_name[sub_span[0]:sub_span[1]]
            sub_length = sub_span[1] - sub_span[0]

            if (sub_length > 1):
                found_submatch = True

                if (span[0] != 0):
                    new_name += '_'

                first = sub_substr[:-1]
                second = substr.replace(first, '')

                new_name += '{}_{}'.format(first, second).lower()

        if (not found_submatch):
            if (span[0] != 0):
                new_name += '_'

            new_name += substr.lower()

    return new_name


class FailedValidationError(Exception):
    """
    Exception raised for validation errors found when parsing CAN messages

    Attributes
    ----------
    bytes - The byte string representation of the message
    message - text describing the error (same as __str__)
    node_id - if of the node sending the message
    cob-id - message cob-id
    parse_type - message type that failed (ex: SDO, PDO)
    sub_type - sub-type of message that failed (ex: SDO Segment) or None
    """

    def __init__(self, data, node_id, cob_id, parse_type, message="A Validation Error has occurred", sub_type=None):
        self.data = data
        self.node_id = node_id
        self.cob_id = cob_id
        self.parse_type = parse_type
        self.sub_type = sub_type
        self.message = message
        self.time_occured = datetime.datetime.now()
        super().__init__(self.message)
