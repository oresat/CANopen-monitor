from .canmsg import CANMsg
import typing


class CANMsgTable:
    def __init__(self, capacity: int = None):
        self.__message_table = {}
        self.__capacity = capacity

    def __sort__(self) -> [int]:
        return sorted(self.__message_table.keys())

    def __add__(self, frame: CANMsg) -> None:
        if self.__capacity is not None:
            if (len(self.__message_table) < self.__capacity
                    or (self.__message_table.get(frame.arb_id) is not None)):
                self.__message_table[frame.arb_id] = frame
        else:
            self.__message_table[frame.arb_id] = frame

        return self

    def __len__(self) -> int:
        return len(self.__message_table)

    def __str__(self) -> str:
        attrs = []
        for k, v in self.__dict__.items():
            attrs += ['{}={}'.format(k, v)]
        return 'CANMsgTable {}\n\n'.format(', '.join(attrs))

    def __getitem__(self, key: typing.Union[int, str]) -> CANMsg:
        sub_key = int(key, 16) if type(key) is str else key
        return self.__message_table.get(sub_key)

    def __iter__(self):
        return self.__message_table.__iter__()

    @property
    def capacity(self):
        return self.__capacity
