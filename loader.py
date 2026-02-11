import time

SPINNER = ["|", "/", "-", "\\"]

def draw_loader(stdscr, y, x, message, frame):
    stdscr.addstr(y, x, f"{message} {SPINNER[frame % len(SPINNER)]}")
    stdscr.refresh()
