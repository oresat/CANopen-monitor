from ..canmsgs import CANMsg, MessageType
from . import hb as HBParser, \
              pdo as PDOParser, \
              sync as SYNCParser, \
              emcy as EMCYParser
from .sdo import SDOParser
from .utilities import FailedValidationError


class CANOpenParser:
    def __init__(self, eds_configs: dict):
        self.sdo_parser = SDOParser()
        self.eds_configs = eds_configs

    def parse(self, msg: CANMsg) -> [str, str]:
        node_id = MessageType.cob_id_to_node_id(msg.arb_id)
        eds_config = self.eds_configs.get(node_id)

        if(msg.message_type == MessageType.UKNOWN):
            return [str(msg.message_type), str(hex(msg.arb_id))]
        elif(msg.message_type == MessageType.SYNC):
            parse = SYNCParser.parse
        elif(msg.message_type == MessageType.EMER):
            parse = EMCYParser.parse
        elif(msg.message_type in [
            MessageType.PDO1_TX, MessageType.PDO1_RX,
            MessageType.PDO2_TX, MessageType.PDO2_RX,
            MessageType.PDO3_TX, MessageType.PDO3_RX,
            MessageType.PDO4_TX, MessageType.PDO4_RX
        ]):
            parse = PDOParser.parse
        elif(msg.message_type in [
            MessageType.SDO_TX, MessageType.SDO_RX,
        ]):
            parse = self.sdo_parser.parse
        elif(msg.message_type == MessageType.HEARTBEAT):
            parse = HBParser.parse

        try:
            message = parse(msg.arb_id, msg.data, eds_config)
        except UnboundLocalError as e:
            message = str(e)
        except TypeError as e:
            message = str(e)
        except FailedValidationError as e:
            message = str(e)

        return [message, str(hex(node_id))]
