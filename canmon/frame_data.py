import time
from canard.can import Frame
from enum import Enum
from .dictionaries import node_names, heartbeat_statuses

class FrameType(Enum):
    NMT = 0
    SYNC = 1
    EMER = 2
    TIME_STAMP = 3
    PDO1_TX = 4
    PDO1_RX = 5
    PDO2_TX = 6
    PDO2_RX = 7
    PDO3_TX = 8
    PDO3_RX = 9
    PDO4_TX = 10
    PDO4_RX = 11
    SDO_TX = 12
    SDO_RX = 13
    HEARTBEAT = 14
    UKNOWN = 15

    def __str__(self): return {
            0: "NMT",
            1: "SYNC",
            2: "EMCY",
            3: "TIME",
            4: "TPDO1",
            5: "RPDO1",
            6: "TPDO2",
            7: "RPDO2",
            8: "TPDO3",
            9: "RPDO3",
            10: "TPDO4",
            11: "RPDO4",
            12: "TSDO",
            13: "RSDO",
            14: "HB",
            15: "UKOWN"
            }[self.value]

class FrameData(Frame):
    def __init__(self, src, ndev, type=FrameType.UKNOWN):
        super().__init__(src.id, src.dlc, src.data, src.frame_type, src.is_extended_id)
        self.node_id = src.id
        self.ndev = ndev
        self.type = type
        self.stale_time = 0
        self.dead_time = 0
        self.last_modified = time.time()

        # Process the ID
        if(self.id == 0): # NMT node control
            self.type = FrameType.NMT
            self.node_id = self.id
        elif(self.id == 0x080): # SYNC
            self.type = FrameType.SYNC
            self.node_id = self.id
        elif(self.id > 0x80 and self.id < 0x100): # Emergency
            self.type = FrameType.EMER
            self.node_id = self.id - 0x80
        elif(self.id == 100): # Time Stamp
            self.type = FrameType.TIME_STAMP
            self.node_id = self.id
        elif(self.id >= 0x180 and self.id < 0x200): # PDO1 tx
            self.type = FrameType.PDO1_TX
            self.node_id = self.id - 0x180
        elif(self.id >= 0x200 and self.id < 0x280): # PDO1 rx
            self.type = FrameType.PDO1_RX
            self.node_id = self.id - 0x200
        elif(self.id >= 0x280 and self.id < 0x300): # PDO2 tx
            self.type = FrameType.PDO2_TX
            self.node_id = self.id - 0x280
        elif(self.id >= 0x300 and self.id < 0x380): # PDO2 rx
            self.type = FrameType.PDO2_RX
            self.node_id = self.id - 0x300
        elif(self.id >= 0x380 and self.id < 0x400): # PDO3 tx
            self.type = FrameType.PDO3_TX
            self.node_id = self.id - 0x380
        elif(self.id >= 0x400 and self.id < 0x480): # PDO3 rx
            self.type = FrameType.PDO3_RX
            self.node_id = self.id - 0x400
        elif(self.id >= 0x480 and self.id < 0x500): # PDO4 tx
            self.type = FrameType.PDO4_TX
            self.node_id = self.id - 0x480
        elif(self.id >= 0x500 and self.id < 0x580): # PDO4 rx
            self.type = FrameType.PDO4_RX
            self.node_id = self.id - 0x500
        elif(self.id >= 0x580 and self.id < 0x600): # SDO tx
            self.type = FrameType.SDO_TX
            self.node_id = self.id - 0x580
        elif(self.id >= 0x600 and self.id < 0x680): # SDO rx
            self.type = FrameType.SDO_RX
            self.node_id = self.id - 0x600
        elif(self.id > 0x700 and self.id < 0x7FF): # Heartbeats
            self.node_id = self.id - 0x700
            self.type = FrameType.HEARTBEAT

        self.name = node_names.get(self.node_id)
        if(self.name is None):
            self.name = str(hex(self.id))

    def __str__(self):
        if(self.type == FrameType.HEARTBEAT):
            status = heartbeat_statuses.get(self.data[0])
            if(status is None): return str(hex(self.data[0]))
            else: return status
        else:
            res = ""
            for i in self.data: res += str(hex(i)) + " "
            return res

    def __lt__(self, operand): return self.type.value < operand.value
    def __le__(self, operand): return self.type.value <= operand.value
    def __gt__(self, operand): return self.type.value > operand.value
    def __ge__(self, operand): return self.type.value >= operand.value
    def __eq__(self, operand): return self.type.value == operand.value
    def __ne__(self, operand): return self.type.value != operand.value
    def is_stale(self): return ((time.time() - self.last_modified) >= self.stale_time)
    def is_dead(self): return ((time.time() - self.last_modified) >= self.dead_time)
