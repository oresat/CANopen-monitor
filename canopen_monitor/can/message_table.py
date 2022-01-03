from __future__ import annotations
from .message import Message, MessageType

class MessageTable:
    PARSER = None

    def __init__(self: MessageTable, headers: (str)):
        self.headers = headers
        self.table = {}
        self.undrawn_messages = []

    def add(self: MessageTable, message: Message) -> MessageTable:
        if(MessageTable.PARSER is not None):
            message.node_name = MessageTable.PARSER.get_name(message)
            message.message, message.error = MessageTable.PARSER.parse(message)

        table_message = self.table.get(message.arb_id)
        is_new = table_message is None
        is_dirty = not is_new and message == table_message
        self.table[message.arb_id] = message
        if(is_new or is_dirty):
            self.push_undrawn(message)

        return self

    def __len__(self: MessageTable) -> int:
        return len(self.table)

    def clear(self) -> None:
        '''
        Clear the table to remove all its messages.
        '''
        self.table = {}

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

    def push_undrawn(self: MessageTable, message: Message) -> None:
        self.undrawn_messages.append(message)

    def pop_undrawn(self: MessageTable) -> Message:
        if(len(self.undrawn_messages) == 0):
            return None
        return self.undrawn_messages.pop(0)

    def __contains__(self: MessageTable, node_id: int) -> bool:
        return node_id in self.table

    def __iter__(self: MessageTable) -> MessageTable:
        return self

    def __next__(self: MessageTable) -> Message:
        if(len(self.undrawn_messages) == 0):
            raise StopIteration()
        return self.undrawn_messages.pop(0)

    def __call__(self: MessageTable,
                 start: int,
                 stop: int = None) -> MessageTable:
        self.__stop = stop if stop < len(self.table) else len(self.table)
        self.__start = start if start < self.__stop else self.__stop
        return self
