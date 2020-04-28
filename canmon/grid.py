from .pane import Pane
from enum import Enum

class Split(Enum):
    HORIZONTAL = 0
    VERTICAL = 1

    horizontal = HORIZONTAL
    vertical = VERTICAL

class Grid:
    def __init__(self, width = 0, height = 0, x_off = 0, y_off = 0, split = Split.VERTICAL):
        self.width = width
        self.height = height
        self.x_off = x_off
        self.y_off = y_off
        self.split = split
        self.items = []

    def resize(self, width, height, x_off, y_off):
        self.width = width
        self.height = height
        self.x_off = x_off
        self.y_off = y_off

    def add_pannel(self, pannel): self.items.append(pannel)

    def add_item(self, name, item):
        for i in self.items:
            if(type(i) == Grid): i.add_item(name, item)
            else:
                if(i.name.lower() == name.lower()): i.add(item)

    def flat_pannels(self):
        res = []
        for item in self.items:
            if(type(item) is Grid): res += item.flat_pannels()
            else: res.append(item)
        return res

    def draw(self):
        if(self.split == Split.HORIZONTAL):
            width = self.width
            height = int(self.height / len(self.items))
            h_off = height
            w_off = 0
        elif(self.split == Split.VERTICAL):
            width = int(self.width / len(self.items))
            height = self.height
            h_off = 0
            w_off = width

        for i, item in enumerate(self.items):
            if(type(item) == Pane): item.draw(width, height, i * w_off + self.x_off, i * h_off + self.y_off)
            else:
                item.resize(width, height, i * w_off + self.x_off, i * h_off + self.y_off)
                item.draw()
