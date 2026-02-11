import curses
import requests
import urllib3
from db import get_session

urllib3.disable_warnings()

TREE_URL = "https://topbrains.com/subject/v1/tree/syllabus"


def select_chapter(stdscr, subject_id, syllabus_id):
    session = get_session()
    if not session:
        return None

    access_token = session[9]  # access_token index

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    params = {
        "resourceId": subject_id,   # ✅ IMPORTANT
        "syllabusId": syllabus_id,  # ✅ IMPORTANT
        "pageNo": 0,
        "pageSize": 200
    }

    res = requests.get(
        TREE_URL,
        headers=headers,
        params=params,
        verify=False
    )

    if res.status_code != 200:
        stdscr.clear()
        stdscr.addstr(4, 4, "❌ Failed to load chapters")
        stdscr.addstr(6, 4, res.text)
        stdscr.addstr(8, 4, "Press any key to return...")
        stdscr.getch()
        return None

    nodes = res.json()["response"]["content"]

    # Extract CHAPTER nodes
    chapters = [
        {
            "chapterId": n["_id"],
            "chapterName": n["name"]
        }
        for n in nodes
        if n.get("type") == "CHAPTER"
    ]

    if not chapters:
        stdscr.clear()
        stdscr.addstr(4, 4, "❌ No chapters found")
        stdscr.addstr(6, 4, "Press any key to return...")
        stdscr.getch()
        return None

    current = 0

    while True:
        stdscr.clear()
        stdscr.addstr(1, 2, "Select Chapter")
        stdscr.addstr(2, 2, "-" * 14)

        h, w = stdscr.getmaxyx()
        visible_height = h - 8          # keep space for header/footer
        start = max(0, current - visible_height + 1)
        end = min(len(chapters), start + visible_height)

        for idx in range(start, end):
            y = 4 + (idx - start)
            name = chapters[idx]["chapterName"][: w - 8]  # trim long text

            if idx == current:
                stdscr.addstr(y, 4, name, curses.A_REVERSE)
            else:
                stdscr.addstr(y, 4, name)

        h, w = stdscr.getmaxyx()
        footer_y = h - 2

        stdscr.addstr(
            footer_y,
            2,
            "↑ ↓ move   Enter select   Esc cancel"[: w - 4]
        )

        stdscr.refresh()

        key = stdscr.getch()

        if key == curses.KEY_UP:
            current = (current - 1) % len(chapters)
        elif key == curses.KEY_DOWN:
            current = (current + 1) % len(chapters)
        elif key in (10, 13):
            return chapters[current]
        elif key == 27:
            return None
