import curses


class PopupWindow:
    def __init__(self, parent, message, banner='fatal', color_pair=3):
        height, width = parent.getmaxyx()
        style = curses.color_pair(color_pair) | curses.A_REVERSE
        any_key_message = "Press any key to continue..."
        message = message.split('\n')
        long = len(any_key_message)

        for m in message:
            if(len(m) > long):
                long = len(m)
        if(long < len(banner)):
            long = len(banner)
        long += 1

        window = curses.newwin(len(message) + 2,
                               long + 2,
                               int((height - len(message) + 2) / 2),
                               int((width - long + 2) / 2))
        window.attron(style)
        for i, m in enumerate(message):
            window.addstr(1 + i, 1, m.ljust(long, ' '))
        window.box()
        window.addstr(0, 1, banner + ":", curses.A_UNDERLINE | style)
        window.addstr(len(message) + 1,
                      long - len(any_key_message),
                      any_key_message)

        window.attroff(style)

        window.refresh()
        parent.refresh()

        window.getch()
        curses.flushinp()
        window.clear()
        parent.clear()
