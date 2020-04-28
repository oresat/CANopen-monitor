import curses

class Pane:
    def __init__(self, name, fields = []):
        self.window = curses.newwin(0, 0, 0, 0)
        self.name = name
        self.fields = fields
        self.items = []

    def add(self, item): self.items.append(item)

    def resize(self, width, height, x_off, y_off):
        self.window = curses.newwin(height, width, y_off, x_off)

    def draw(self, width, height, x_off, y_off):
        self.resize(width, height, x_off, y_off)
        self.window.addstr(1, 1, self.name)
        self.window.chgat(1, 1, -1, curses.color_pair(5))

        self.window.addstr(2, 1, "")
        for field in self.fields:
            self.window.addstr(str(field) + "\t")
        self.window.chgat(2, 1, -1, curses.color_pair(6))

        for i, item in enumerate(self.items):
            self.window.addstr(3 + i, 1, str(item))

        self.window.box()
        self.window.refresh()
