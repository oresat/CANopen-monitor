from frame_data import FrameData

class FrameTable:
    def __init__(self, name="", max_table_size=None, stale_time=60, dead_time=600):
        self.name = name
        self.type = type
        self.table = {}
        self.max_table_size = max_table_size
        self.stale_time = stale_time
        self.dead_time = dead_time

    def add(self, frame):
        frame.stale_time = self.stale_time
        frame.dead_time = self.dead_time

        if(self.max_table_size is not None):
            if(len(self.table) < self.max_table_size \
                    or (self.table.get(frame.id) is not None)):
                self.table[frame.id] = frame
        else: self.table[frame.id] = frame

    def __len__(self): return len(self.table)

    def __str__(self):
        return self.name
