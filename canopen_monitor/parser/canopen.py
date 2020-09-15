import canopen_monitor.parser.sync as SYNCParser
import canopen_monitor.parser.emcy as EMCYParser
import canopen_monitor.parser.pdo as PDOParser
import canopen_monitor.parser.hb as HBParser
from canopen_monitor.parser.sdo import SDOParser


class CANOpenParser:
    def __init__(self, eds_configs: dict):
        self.sdo = SDOParser()
        self.eds_configs = eds_configs

    def parse(self, cob_id: hex, data: [bytes]) -> str:
        response = 'BAD PARSE'

        if(cob_id <= 0x80):
            response = SYNCParser.parse(data)
        elif(cob_id >= 0x80 and cob_id < 0x180):
            response = EMCYParser.parse(data)
        elif(cob_id >= 0x180 and cob_id < 0x580):
            node_id = cob_id - 0x180
            eds_config = self.eds_configs.get(node_id)
            if(eds_config is None):
                response = "PDO PARSER NOT FOUND FOR NODE ID #{}".format(node_id)
            else:
                response = PDOParser.parse(cob_id, eds_config, data)
        elif(cob_id >= 0x580 and cob_id < 0x700):
            node_id = cob_id - 0x180
            eds_config = self.eds_configs.get(node_id)
            if(eds_config is None):
                response = "SDO PARSER NOT FOUND FOR NODE ID #{}".format(node_id)
            else:
                response = self.sdo.parse(cob_id, eds_config, data)
        elif(cob_id >= 0x700 and cob_id < 0x7E4):
            response = HBParser.parse(data)

        return response
