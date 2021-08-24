from __future__ import annotations
from .message import Message, MessageType


class MessageTable:
    def __init__(self: MessageTable, parser=None):
        self.table = {}
        self.parser = parser

    def __add__(self: MessageTable, message: Message) -> MessageTable:
        if(self.parser is not None):
            message.node_name = self.parser.get_name(message)
            message.message, message.error = self.parser.parse(message)
        self.table[message.arb_id] = message
        return self

    def __len__(self: MessageTable) -> int:
        return len(self.table)

    def filter(self: MessageTable,
               types: MessageType,
               start: int = 0,
               end: int = None,
               sort_by: str = 'arb_id',
               reverse=False) -> [Message]:
        end = len(self.table) if end is None else end
        messages = list(filter(lambda x: x.type in types
                        or x.supertype in types, self.table.values()))
        slice = messages[start:end]
        return sorted(slice, key=lambda x: getattr(x, sort_by), reverse=reverse)

    def __contains__(self: MessageTable, node_id: int) -> bool:
        return node_id in self.table

    def __iter__(self: MessageTable) -> MessageTable:
        self.__keys = sorted(list(self.table.keys()))
        return self

    def __next__(self: MessageTable) -> Message:
        if(self.__start == self.__stop):
            raise StopIteration()
        message = self.table[self.__keys[self.__start]]
        self.__start += 1
        return message

    def __call__(self: MessageTable,
                 start: int,
                 stop: int = None) -> MessageTable:
        self.__stop = stop if stop < len(self.table) else len(self.table)
        self.__start = start if start < self.__stop else self.__stop
        return self
