from .canmsg import CANMsg
import typing


class CANMsgTable:
    def __init__(self, capacity: int = None):
        self.__message_table = {}
        self.__capacity = capacity

    def __sort__(self) -> [int]:
        return sorted(self.message_table.keys())

    def __ladd__(self, frame: CANMsg) -> None:
        if(self.capacity is not None):
            if(len(self.message_table) < self.capacity
                    or (self.message_table.get(frame.arb_id) is not None)):
                self.message_table[frame.arb_id] = frame
        else:
            self.message_table[frame.arb_id] = frame

    def __len__(self) -> int:
        return len(self.message_table)

    def __str__(self) -> str:
        attrs = []
        for k, v in self.__dict__.items():
            attrs += ['{}={}'.format(k, v)]
        return 'CANMsgTable {}\n\n'.format(', '.join(attrs))

    def __getitem__(self, key: typing.Union[int, str]) -> CANMsg:
        sub_key = int(key, 16) if type(key) is str else key
        return self.message_table.get(sub_key)
