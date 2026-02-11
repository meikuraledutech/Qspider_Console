import curses
import os
import csv


REQUIRED_HEADERS = [
    "questionTitle",
    "questionDescription",
    "optionA",
    "optionB",
    "optionC",
    "optionD",
    "correctOption",
    "marks",
    "difficulty"
]


def select_csv(stdscr):
    files = [f for f in os.listdir(".") if f.lower().endswith(".csv")]

    if not files:
        stdscr.clear()
        stdscr.addstr(4, 4, "❌ No CSV files found in current directory")
        stdscr.addstr(6, 4, "Press any key to return...")
        stdscr.getch()
        return None

    current = 0

    while True:
        stdscr.clear()
        stdscr.addstr(1, 2, "Select CSV File")
        stdscr.addstr(2, 2, "-" * 15)

        h, w = stdscr.getmaxyx()
        visible = h - 8
        start = max(0, current - visible + 1)
        end = min(len(files), start + visible)

        for idx in range(start, end):
            y = 4 + (idx - start)
            name = files[idx][: w - 6]

            if idx == current:
                stdscr.addstr(y, 4, name, curses.A_REVERSE)
            else:
                stdscr.addstr(y, 4, name)

        stdscr.addstr(h - 2, 2, "↑ ↓ move   Enter select   Esc cancel")
        stdscr.refresh()

        key = stdscr.getch()

        if key == curses.KEY_UP:
            current = (current - 1) % len(files)
        elif key == curses.KEY_DOWN:
            current = (current + 1) % len(files)
        elif key in (10, 13):
            return files[current]
        elif key == 27:
            return None


def validate_csv(stdscr, csv_file):
    try:
        with open(csv_file, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader)
            first_row = next(reader, None)
    except Exception as e:
        stdscr.clear()
        stdscr.addstr(4, 4, f"❌ Failed to read CSV: {e}")
        stdscr.addstr(6, 4, "Press any key to return...")
        stdscr.getch()
        return False

    if headers != REQUIRED_HEADERS:
        stdscr.clear()
        stdscr.addstr(4, 4, "❌ CSV header mismatch")
        stdscr.addstr(6, 6, f"Expected: {', '.join(REQUIRED_HEADERS)}")
        stdscr.addstr(8, 4, "Press any key to return...")
        stdscr.getch()
        return False

    if not first_row:
        stdscr.clear()
        stdscr.addstr(4, 4, "❌ CSV has no data rows")
        stdscr.addstr(6, 4, "Press any key to return...")
        stdscr.getch()
        return False

    stdscr.clear()
    stdscr.addstr(4, 4, "✅ CSV validation successful")
    stdscr.addstr(6, 6, f"File : {csv_file}")
    stdscr.addstr(7, 6, f"Questions detected (min): 1+")
    stdscr.addstr(9, 4, "Press any key to continue...")
    stdscr.getch()

    return True
