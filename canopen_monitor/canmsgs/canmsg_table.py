class CANMsgTable:
    def __init__(self,
                 name="",
                 capacity=None,
                 stale_time=60,
                 dead_time=600):
        self.name = name
        self.type = type
        self.table = {}
        self.capacity = capacity
        self.stale_time = stale_time
        self.dead_time = dead_time

    def add(self, frame):
        frame.stale_time = self.stale_time
        frame.dead_time = self.dead_time

        if(self.capacity is not None):
            if(len(self.table) < self.capacity
                    or (self.table.get(frame.id) is not None)):
                self.table[frame.id] = frame
        else:
            self.table[frame.id] = frame

    def ids(self):
        return sorted(self.table.keys())

    def __len__(self):
        return len(self.table)

    def __str__(self):
        return self.name

    def __getitem__(self, key):
        return self.table.get(key)
