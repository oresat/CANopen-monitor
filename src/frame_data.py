import time
from canard.can import Frame
from enum import Enum

class FrameType(Enum):
    HEARBEAT = 0
    SDO = 1
    RDO = 2
    PDO = 3
    MISC = 4

    def __str__(self):
        if(self.value == 0): return "Heartbeat"
        elif(self.value == 1): return "SDO"
        elif(self.value == 2): return "RDO"
        elif(self.value == 3): return "PDO"
        else: return "N/A"


# Expanded frame data class
class FrameData(Frame):
    def __init__(self, src, ndev, type=FrameType.MISC):
        self.ndev = ndev
        self.type = type
        self.stale_time = 0
        self.dead_time = 0
        self.last_modified = time.time()
        self.is_extended_id = src.is_extended_id
        self.dlc = src.dlc
        self.id = src.id
        self.data = src.data
        self.frame_type = src.frame_type

    def hex_data_str(self):
        res = ""
        for i in self.data: res += str(hex(i)) + " "
        return res

    def is_stale(self): return ((time.time() - self.last_modified) >= self.stale_time)
    def is_dead(self): return ((time.time() - self.last_modified) >= self.dead_time)
