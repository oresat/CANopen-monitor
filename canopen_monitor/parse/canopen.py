from typing import Union
from ..can import Message, MessageType
from . import hb as HBParser, \
    pdo as PDOParser, \
    sync as SYNCParser, \
    emcy as EMCYParser, \
    time as TIMEParser
from .sdo import SDOParser
from .utilities import FailedValidationError, format_bytes


class CANOpenParser:
    """
    A convenience wrapper for the parse function
    """
    def __init__(self, eds_configs: dict):
        self.sdo_parser = SDOParser()
        self.eds_configs = eds_configs

    def get_name(self, message: Message) -> Union[str, None]:
        node_id = str(hex(message.node_id))
        parser = self.eds_configs.get(node_id)
        return parser.device_commissioning.node_name \
            if parser else hex(message.node_id)

    def parse(self, message: Message) -> (str, str):
        """
        Detect the type of the given message and return the parsed version

        Arguments
        ---------
        @:param: message: a Message object containing the message

        Returns
        -------
        `str`: The parsed message

        """
        node_id = str(hex(message.node_id))
        eds_config = self.eds_configs.get(node_id) \
            if node_id is not None else None

        # Detect message type and select the appropriate parse function
        if (message.type == MessageType.SYNC):
            parse_function = SYNCParser.parse
        elif (message.type == MessageType.EMER):
            parse_function = EMCYParser.parse
        elif (message.supertype == MessageType.PDO):
            parse_function = PDOParser.parse
        elif (message.supertype == MessageType.SDO):
            if self.sdo_parser.is_complete:
                self.sdo_parser = SDOParser()
            parse_function = self.sdo_parser.parse
        elif (message.type == MessageType.HEARTBEAT):
            parse_function = HBParser.parse
        elif (message.type == MessageType.TIME):
            parse_function = TIMEParser.parse
        else:
            parse_function = None

        # Call the parse function and save the result
        # On error, return the message data
        try:
            parsed_message = parse_function(message.arb_id,
                                            message.data,
                                            eds_config)
            error = ""
        except (FailedValidationError, TypeError) as exception:
            parsed_message = format_bytes(message.data)
            error = str(exception)

        return parsed_message, error
