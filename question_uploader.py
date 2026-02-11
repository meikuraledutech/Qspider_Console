import csv
import json
import requests
import urllib3
from db import get_session

urllib3.disable_warnings()

QUESTION_CREATE_URL = "https://topbrains.com/subject/v1/question"


def upload_first_question(
    stdscr,
    csv_file,
    chapter_id,
    subject_id,
    organization_id
):
    session = get_session()
    access_token = session[9]  # access_token

    # --- Read first question from CSV ---
    with open(csv_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        row = next(reader)  # ✅ ONLY FIRST QUESTION

    payload = {
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
        "resource": {
            "images": [],
            "text": []
        },
        "status": "NEW",
        "additionalDetails": {
            "company": "",
            "keywords": [],
            "relatedExams": [],
            "relatedQuestionIds": []
        },
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
        "isMultiAnswer": False,
        "isMultipleChoice": True,
        "isShuffleOption": False
    }

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    files = {
        "questionRequest": (None, json.dumps(payload), "application/json")
    }

    res = requests.post(
        QUESTION_CREATE_URL,
        headers=headers,
        files=files,
        verify=False
    )

    stdscr.clear()

    if res.status_code in (200, 201):
        body = res.json()["response"]
        stdscr.addstr(4, 4, "✅ Question uploaded successfully")
        stdscr.addstr(6, 6, f"Question ID : {body['id']}")
        stdscr.addstr(7, 6, f"Title       : {body['questionTitle']}")
    else:
        stdscr.addstr(4, 4, "❌ Upload failed")
        stdscr.addstr(6, 6, f"Status : {res.status_code}")
        stdscr.addstr(7, 6, res.text[:200])

    stdscr.addstr(10, 4, "Press any key to return...")
    stdscr.getch()
