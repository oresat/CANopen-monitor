from .canmsg import CANMsg


class CANMsgTable:
    def __init__(self,
                 name: str = "message_table",
                 capacity: int = None):
        self.name = name
        self.message_table = {}
        self.capacity = capacity

    def add(self, frame: CANMsg) -> None:
        if(self.capacity is not None):
            if(len(self.message_table) < self.capacity
                    or (self.message_table.get(frame.arb_id) is not None)):
                self.message_table[frame.arb_id] = frame
        else:
            self.message_table[frame.arb_id] = frame

    def ids(self) -> [int]:
        return sorted(self.message_table.keys())

    def __len__(self) -> int:
        return len(self.message_table)

    def __str__(self) -> str:
        attrs = []
        for k, v in self.__dict__.items():
            attrs += ['{}={}'.format(k, v)]
        return 'CANMsgTable {}\n\n'.format(', '.join(attrs))

    def __getitem__(self, key: int) -> CANMsg:
        return self.message_table.get(key)
