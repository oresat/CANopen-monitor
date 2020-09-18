import canopen_monitor.parser.sync as SYNCParser
import canopen_monitor.parser.emcy as EMCYParser
import canopen_monitor.parser.pdo as PDOParser
import canopen_monitor.parser.hb as HBParser
from canopen_monitor.parser import FailedValidationError
from canopen_monitor.parser.sdo import SDOParser


class CANOpenParser:
    def __init__(self, eds_configs: dict):
        self.sdo = SDOParser()
        self.eds_configs = eds_configs

    def parse(self, cob_id: int, data: [bytes]) -> str:
        try:
            response = 'Unknown Parse for COB ID {}'.format(hex(cob_id))

            if(cob_id <= 0x80):
                response = SYNCParser.parse(data, cob_id)
            elif(cob_id >= 0x80 and cob_id < 0x180):
                response = EMCYParser.parse(data)
            elif(cob_id >= 0x180 and cob_id < 0x580):
                node_id = hex(int(str(cob_id - 0x180), 16))
                eds_config = self.eds_configs.get(node_id)
                if(eds_config is None):
                    response = 'Unregistered Node: {}'.format(node_id)
                else:
                    response = PDOParser.parse(cob_id, eds_config, data)
            elif(cob_id >= 0x580 and cob_id < 0x700):
                node_id = hex(int(str(cob_id - 0x580), 16))
                eds_config = self.eds_configs.get(node_id)
                if(eds_config is None):
                    response = 'Unregistered Node: {}'.format(node_id)
                else:
                    response = self.sdo.parse(cob_id, eds_config, data)
            elif(cob_id >= 0x700 and cob_id < 0x7E4):
                node_id = hex(int(str(cob_id - 0x700), 16))
                eds_config = self.eds_configs.get(node_id)
                if(eds_config is None):
                    response = 'Unregistered Node: {}'.format(node_id)
                else:
                    response = HBParser.parse(cob_id, eds_config, data)
        except FailedValidationError as error:
            return str(error)
        return response
