import curses
import requests
import urllib3
from db import get_session

urllib3.disable_warnings()

BATCH_URL = "https://topbrains.com/subject/v1/batch/get-batches"


def select_batch(stdscr, subject_id):
    session = get_session()
    if not session:
        return None

    (
        user_id,
        user_name,
        user_email,
        user_phone,
        user_role,
        user_status,
        organization_id,
        organization_name,
        organization_type,
        access_token,
        refresh_token
    ) = session

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    params = {
        "subjectId": subject_id,
        "organizationId": organization_id,
        "pageNo": 0,
        "pageSize": 50
    }

    res = requests.get(
        BATCH_URL,
        headers=headers,
        params=params,
        verify=False
    )

    if res.status_code != 200:
        stdscr.clear()
        stdscr.addstr(4, 4, "❌ Failed to load batches")
        stdscr.addstr(6, 4, res.text)
        stdscr.addstr(8, 4, "Press any key to return...")
        stdscr.getch()
        return None

    items = res.json()["response"]["content"]

    if not items:
        stdscr.clear()
        stdscr.addstr(4, 4, "❌ No batches found")
        stdscr.addstr(6, 4, "Press any key to return...")
        stdscr.getch()
        return None

    batches = []
    for b in items:
        batches.append({
            "batchId": b["id"],
            "batchName": b["name"],
            "batchCode": b.get("batchCode"),
            "syllabusReference": b["syllabusReference"]
        })

    current = 0

    while True:
        stdscr.clear()
        stdscr.addstr(1, 2, "Select Batch")
        stdscr.addstr(2, 2, "-" * 13)

        for i, b in enumerate(batches):
            label = b["batchName"]
            if b["batchCode"]:
                label += f" ({b['batchCode']})"

            if i == current:
                stdscr.addstr(4 + i, 4, label, curses.A_REVERSE)
            else:
                stdscr.addstr(4 + i, 4, label)

        stdscr.addstr(6 + len(batches), 2, "↑ ↓ move   Enter select   Esc cancel")
        stdscr.refresh()

        key = stdscr.getch()

        if key == curses.KEY_UP:
            current = (current - 1) % len(batches)
        elif key == curses.KEY_DOWN:
            current = (current + 1) % len(batches)
        elif key in (10, 13):
            return batches[current]
        elif key == 27:
            return None
