import curses

from api_guard import api_call, AuthExpired
from db import get_session

SYLLABUS_URL = "https://topbrains.com/subject/v1/syllabus/get-syllabus-trainer"


def select_syllabus(stdscr):
    session = get_session()
    if not session:
        return None

    access_token = session[9]

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    try:
        data = api_call(
            stdscr,
            "GET",
            SYLLABUS_URL,
            headers=headers,
            params={
                "pageNo": 0,
                "pageSize": 20
            },
            message="Loading syllabus..."
        )
    except AuthExpired:
        stdscr.clear()
        stdscr.addstr(4, 4, "🔒 Session expired. Please login again.")
        stdscr.addstr(6, 4, "Press any key to continue...")
        stdscr.getch()
        return None

    items = data["response"]["content"]
    if not items:
        stdscr.clear()
        stdscr.addstr(4, 4, "❌ No syllabus found")
        stdscr.addstr(6, 4, "Press any key to return...")
        stdscr.getch()
        return None

    current = 0

    while True:
        stdscr.clear()
        stdscr.addstr(1, 2, "Select Syllabus")
        stdscr.addstr(2, 2, "-" * 15)

        h, w = stdscr.getmaxyx()
        visible = h - 8
        start = max(0, current - visible + 1)
        end = min(len(items), start + visible)

        for idx in range(start, end):
            y = 4 + (idx - start)
            name = items[idx]["subject"]["name"][: w - 8]

            if idx == current:
                stdscr.addstr(y, 4, name, curses.A_REVERSE)
            else:
                stdscr.addstr(y, 4, name)

        stdscr.addstr(h - 2, 2, "↑ ↓ move   Enter select   Esc cancel")
        stdscr.refresh()

        key = stdscr.getch()

        if key == curses.KEY_UP:
            current = (current - 1) % len(items)
        elif key == curses.KEY_DOWN:
            current = (current + 1) % len(items)
        elif key in (10, 13):
            subject = items[current]["subject"]
            return {
                "subjectId": subject["id"],
                "subjectName": subject["name"],
                "syllabusId": items[current]["syllabusId"]
            }
        elif key == 27:
            return None
