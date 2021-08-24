from __future__ import annotations


class Column:
    def __init__(self: Column,
                 name: str,
                 attr_name: str,
                 fmt_fn: callable = str,
                 padding: int = 2):
        self.name = name
        self.attr_name = attr_name
        self.fmt_fn = fmt_fn
        self.padding = padding
        self.length = len(name) + self.padding

    def update_length(self: Column, object: any) -> bool:
        obj_len = len(self.fmt_fn(getattr(object, self.attr_name))) \
                  + self.padding

        if(obj_len > self.length):
            self.length = obj_len
            return True
        return False

    @property
    def header(self: Column) -> str:
        return f'{self.name}{(" " * self.padding)}'.ljust(self.length, ' ')

    def format(self: Column, object: any) -> str:
        return f'{self.fmt_fn(getattr(object, self.attr_name))}' \
               f'{(" " * self.padding)}' \
               .ljust(self.length, ' ')
