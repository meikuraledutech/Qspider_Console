import csv
import json
import curses
import asyncio
import ssl
import aiohttp

from db import get_session, log_upload, save_question
from table_renderer import draw_table, scrollable_table

QUESTION_CREATE_URL = "https://topbrains.com/subject/v1/question"


def _build_payload(row, chapter_id, subject_id, organization_id):
    return {
        "questionTitle": row["questionTitle"],
        "parentId": chapter_id,
        "parentType": "CHAPTER",
        "type": "MCQ",
        "applications": ["QLABS", "TESTFRESHERS"],
        "subjectReference": subject_id,
        "organizationReference": organization_id,
        "evaluationType": "AUTOMATIC",
        "difficultyLevel": row["difficulty"],
        "isSharable": False,
        "sourceCategory": "SAMPLE",
        "source": "Sample",
        "resource": {"images": [], "text": []},
        "status": "NEW",
        "version": {
            "questionDescription": f"<p>{row['questionDescription']}</p>",
            "solution": {
                "options": {
                    "a": row["optionA"],
                    "b": row["optionB"],
                    "c": row["optionC"],
                    "d": row["optionD"]
                },
                "correctOptions": [row["correctOption"].lower()],
                "answerExplanation": ""
            },
            "marks": float(row["marks"]),
            "duration": 2
        },
        "isMultipleChoice": True,
        "isMultiAnswer": False,
        "isShuffleOption": False
    }


def _draw_live(stdscr, results, total, success, duplicate, failed, skipped):
    """Redraw screen with live-updating table after each upload."""
    stdscr.clear()
    h, w = stdscr.getmaxyx()

    done = success + duplicate + failed + skipped
    stdscr.addstr(1, 2, f"Uploading... {done} / {total}", curses.A_BOLD)
    stdscr.addstr(2, 2, f"Success: {success}    Duplicate: {duplicate}    Failed: {failed}    Skipped: {skipped}")

    table_headers = ["#", "Question Title", "Status", "Error"]

    # show only rows that fit on screen, auto-scroll to latest
    max_visible = h - 8
    visible = results[-max_visible:] if len(results) > max_visible else results

    draw_table(stdscr, table_headers, visible, start_y=4, max_rows=max_visible)

    if done < total:
        stdscr.addstr(h - 2, 2, "Uploading next question...")
    else:
        stdscr.addstr(h - 2, 2, "Done! Press any key for full report...")

    stdscr.refresh()


async def _upload_one(session, access_token, payload):
    """Post one question and return parsed JSON."""
    headers = {"Authorization": f"Bearer {access_token}"}

    form = aiohttp.FormData()
    form.add_field(
        "questionRequest",
        json.dumps(payload),
        content_type="application/json"
    )

    ssl_ctx = ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE

    async with session.post(
        QUESTION_CREATE_URL,
        headers=headers,
        data=form,
        ssl=ssl_ctx
    ) as resp:
        data = await resp.json()
        return data


async def _upload_all_async(stdscr, rows, chapter_id, subject_id, organization_id):
    db_session = get_session()
    if not db_session:
        return

    user_id = db_session[0]
    access_token = db_session[9]

    total = len(rows)
    results = []
    success = 0
    duplicate = 0
    failed = 0
    skipped = 0

    async with aiohttp.ClientSession() as session:
        for idx, row in enumerate(rows, start=1):

            # build payload — skip row on error
            try:
                payload = _build_payload(row, chapter_id, subject_id, organization_id)
            except Exception as e:
                log_upload(user_id, chapter_id, row.get("questionTitle", f"Row {idx}"), None, "SKIPPED", str(e))
                results.append([idx, row.get("questionTitle", f"Row {idx}")[:30], "SKIPPED", str(e)[:30]])
                skipped += 1
                _draw_live(stdscr, results, total, success, duplicate, failed, skipped)
                if idx < total:
                    await asyncio.sleep(1)
                continue

            # upload — skip on error
            try:
                data = await _upload_one(session, access_token, payload)
                status_code = data.get("statusCode", 0)

                if status_code == 201 and "response" in data and "id" in data["response"]:
                    resp = data["response"]
                    qid = resp["id"]
                    save_question(resp)
                    log_upload(user_id, chapter_id, row["questionTitle"], qid, "SUCCESS")
                    results.append([idx, row["questionTitle"][:30], "SUCCESS", ""])
                    success += 1

                elif status_code == 409:
                    msg = data.get("response", "Duplicate")
                    log_upload(user_id, chapter_id, row["questionTitle"], None, "DUPLICATE", str(msg))
                    results.append([idx, row["questionTitle"][:30], "DUPLICATE", str(msg)[:30]])
                    duplicate += 1

                elif status_code in (401, 403):
                    stdscr.clear()
                    stdscr.addstr(5, 4, "Session expired. Please login again.")
                    stdscr.getch()
                    return

                else:
                    msg = str(data.get("response", "Unknown error"))
                    log_upload(user_id, chapter_id, row["questionTitle"], None, "FAILED", msg)
                    results.append([idx, row["questionTitle"][:30], "FAILED", msg[:30]])
                    failed += 1

            except Exception as e:
                log_upload(user_id, chapter_id, row["questionTitle"], None, "SKIPPED", str(e))
                results.append([idx, row["questionTitle"][:30], "SKIPPED", str(e)[:30]])
                skipped += 1

            # live update after each question
            _draw_live(stdscr, results, total, success, duplicate, failed, skipped)

            # 1 sec delay before next upload
            if idx < total:
                await asyncio.sleep(1)

    # final live screen — wait for keypress then open scrollable report
    _draw_live(stdscr, results, total, success, duplicate, failed, skipped)
    stdscr.getch()

    # scrollable full report
    title = f"Upload Report  |  Success: {success}  Duplicate: {duplicate}  Failed: {failed}  Skipped: {skipped}"
    report_headers = ["#", "Question Title", "Status", "Error"]
    scrollable_table(stdscr, title, report_headers, results)


def upload_all_questions(
    stdscr,
    csv_file,
    chapter_id,
    subject_id,
    organization_id
):
    with open(csv_file, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    asyncio.run(
        _upload_all_async(stdscr, rows, chapter_id, subject_id, organization_id)
    )
