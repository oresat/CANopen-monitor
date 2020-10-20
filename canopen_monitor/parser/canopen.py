from ..canmsgs import CANMsg, MessageType
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

    def parse(self, msg: CANMsg) -> [str, str]:
        node_id = MessageType.cob_id_to_node_id(msg.arb_id)
        eds_config = self.eds_configs.get(hex(node_id)) \
            if node_id is not None else None

        if (eds_config is not None):
            msg.node_name = eds_config.device_info.product_name

        if (msg.message_type == MessageType.UKNOWN):
            return [str(msg.message_type), str(hex(msg.arb_id))]
        elif (msg.message_type == MessageType.SYNC):
            parse = SYNCParser.parse
        elif (msg.message_type == MessageType.EMER):
            parse = EMCYParser.parse
        elif (msg.message_type.super_type() == MessageType.PDO):
            parse = PDOParser.parse
        elif (msg.message_type.super_type() == MessageType.SDO):
            if self.sdo_parser.is_complete:
                self.sdo_parser = SDOParser()
            parse = self.sdo_parser.parse
        elif (msg.message_type == MessageType.HEARTBEAT):
            parse = HBParser.parse
        elif (msg.message_type == MessageType.TIME):
            parse = TIMEParser.parse
        else:
            return ["Unknown", str(hex(msg.arb_id))]

        try:
            message = parse(msg.arb_id, msg.data, eds_config)
        except FailedValidationError:
            message = str(list(map(lambda x: hex(x), msg.data)))

        return [message, msg.node_name]
