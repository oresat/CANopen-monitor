from __future__ import annotations
from .canmsg import CANMsg
import typing
from collections.abc import Iterable, Iterator


class CANMsgTable(Iterable):
    """
    Table of CAN Messages
    """

    def __init__(self: CANMsgTable, capacity: int = None):
        self.__message_table = {}
        self.capacity = capacity

    def __sort__(self: CANMsgTable) -> [int]:
        """
        Overloaded sort function
        Sort by COB-ID

        Returns
        --------
        [int]: List of keys sorted
        """
        return sorted(self.__message_table.keys())

    def __add__(self: CANMsgTable, frame: CANMsg) -> CANMsgTable:
        """
        Overloaded add operator
        allows for following:
        CANMsgTable += CANMsg

        Arguments
        ----------
        frame: CANMsg to be added

        Returns
        --------
        CANMsgTable: returns self after adding message
        """
        if self.capacity is not None:
            if (len(self.__message_table) < self.capacity
                    or (self.__message_table.get(frame.arb_id) is not None)):
                self.__message_table[frame.arb_id] = frame
        else:
            self.__message_table[frame.arb_id] = frame

        return self

    def __len__(self: CANMsgTable) -> int:
        """
        Overloaded len function

        Returns
        --------
        int: Number of CANMsg records in table
        """
        return len(self.__message_table)

    def __str__(self: CANMsgTable) -> str:
        """
        Overloaded str function

        Returns
        --------
        str: String representation of CANMsgTable
        """
        attrs = []
        for k, v in self.__dict__.items():
            attrs += ['{}={}'.format(k, v)]
        return 'CANMsgTable {}\n\n'.format(', '.join(attrs))

    def __getitem__(self: CANMsgTable, key: typing.Union[int, str]) -> \
            typing.Union[CANMsg, None]:
        """
        Overloaded getitem operator
        Example: CANMsgTable[0x40]

        Arguments
        ----------
        key: int or string representation of node COB-ID

        Returns
        --------
        CANMsg: last message added for the provided COB-ID
        None: None will be returned if no messages exist for provided COB-ID
        """
        sub_key = int(key, 16) if type(key) is str else key
        return self.__message_table.get(sub_key)

    def __iter__(self: CANMsgTable) -> Iterator[CANMsg]:
        """
        Overloaded iter function

        Returns
        --------
        Iterator[CANMsg]: iterator for contained messages
        """
        return self.__message_table.__iter__()
