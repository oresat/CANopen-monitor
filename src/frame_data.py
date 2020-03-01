import time
from canard.can import Frame
from enum import Enum

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

    def __str__(self):
        res = ""
        for i in self.data: res += str(hex(i)) + " "
        return res

    def is_stale(self): return ((time.time() - self.last_modified) >= self.stale_time)
    def is_dead(self): return ((time.time() - self.last_modified) >= self.dead_time)
