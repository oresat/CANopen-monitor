from ..can import Message, MessageType
from . import hb as HBParser, \
    pdo as PDOParser, \
    sync as SYNCParser, \
    emcy as EMCYParser, \
    time as TIMEParser
from .sdo import SDOParser
from .utilities import FailedValidationError


class CANOpenParser:
    def __init__(self, eds_configs: dict):
        self.sdo_parser = SDOParser()
        self.eds_configs = eds_configs

    def parse(self, message: Message) -> str:
        node_id = message.node_id
        eds_config = self.eds_configs.get(hex(node_id)) \
            if node_id is not None else None

        if (message.type == MessageType.SYNC):
            parse = SYNCParser.parse
        elif (message.type == MessageType.EMER):
            parse = EMCYParser.parse
        elif (message.supertype == MessageType.PDO):
            parse = PDOParser.parse
        elif (message.supertype == MessageType.SDO):
            if self.sdo_parser.is_complete:
                self.sdo_parser = SDOParser()
            parse = self.sdo_parser.parse
        elif (message.type == MessageType.HEARTBEAT):
            parse = HBParser.parse
        elif (message.type == MessageType.TIME):
            parse = TIMEParser.parse
        else:
            parse = None

        try:
            parsed_message = parse(message.arb_id, message.data, eds_config)
        except (FailedValidationError, TypeError):
            parsed_message = ' '.join(list(map(lambda x: hex(x)[2:]
                                               .upper()
                                               .rjust(2, '0'),
                                               message.data)))
        return parsed_message
