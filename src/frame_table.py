from enum import Enum
from frame_data import FrameData

class FrameType(Enum):
    HEARBEAT = 0
    RDO = 1
    PDO = 2
    MISC = 3

class FrameTable:
    def __init__(self, name="", type=FrameType.MISC, max_table_size=None):
        self.name = name
        self.type = type
        self.table = {}
        self.max_table_size = max_table_size

    def add(self, frame):
        if(self.max_table_size is not None):
            if(len(self.table) < self.max_table_size \
                    or (self.table.get(frame.id) is not None)):
                self.table[frame.id] = frame
        else: self.table[frame.id] = frame

    def __len__(self): return len(self.table)

    def __str__(self):
        res = "table"
        if(not self.name is None): res += "<" + self.name + ">"
        res += ": (" + str(len(self.table)) + ")"

        for frame in self.table.values(): res += "\n\t" + str(frame)
        return res
