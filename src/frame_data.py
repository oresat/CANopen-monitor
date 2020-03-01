import time
from canard.can import Frame
from enum import Enum
from dictionaries import node_names, heartbeat_statuses

class FrameType(Enum):
    HEARBEAT = 0
    SDO = 1
    RDO = 2
    PDO = 3
    MISC = 4

    def __str__(self): return { 0: "Heartbeat",
                                1: "SDO",
                                2: "RDO",
                                3: "PDO",
                                4: "N/A" }[self.value]

class FrameData(Frame):
    def __init__(self, src, ndev, type=FrameType.MISC):
        super().__init__(src.id, src.dlc, src.data, src.frame_type, src.is_extended_id)
        self.ndev = ndev
        self.type = type
        self.stale_time = 0
        self.dead_time = 0
        self.last_modified = time.time()

        # Process the ID
        if(self.id >= 0x701 and self.id <= 0x7FF): # Heartbeats
            self.id -= 0x700
            self.type = FrameType.HEARBEAT
        elif(self.id >= 0x581 and self.id <= 0x5FF): # SDO tx
            self.id -= 0x580
            self.type = FrameType.SDO
        elif(self.id >= 0x601 and self.id <= 0x67F): # SDO rx
            self.id -= 0x600
            self.type = FrameType.SDO
        elif(self.id >= 0x181 and self.id <= 0x57F): # PDO
            self.id -= 0x181
            self.type = FrameType.PDO

        self.name = node_names.get(self.id)
        if(self.name is None): self.name = str(hex(self.id))

    def __str__(self):
        if(self.type == FrameType.HEARBEAT):
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
