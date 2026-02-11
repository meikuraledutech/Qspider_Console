# TopBrains CLI — User Guide

A console application for bulk managing questions on the TopBrains platform.

---

## Getting Started

```bash
source .venv/bin/activate
python main.py
```

---

## Login

On launch you'll see:

```
TopBrains CLI
--------------
  Login
  Exit
```

Select **Login** and enter your credentials:

```
User Email : your@email.com
Password   : ********
```

After login, the menu updates to show your name, role, and organization.

---

## Add MCQ Questions (Bulk Upload)

### Step 1 — Select Syllabus

A list of your assigned syllabuses is loaded from the server. Use arrow keys to pick one.

```
Select Syllabus
---------------
  Complete Content - Capgemini
  Data Structures
  ...
```

### Step 2 — Select Chapter

Chapters under the selected syllabus are shown. Pick the target chapter.

```
Select Chapter
--------------
  Problem Solving and Data Structure with Java
  Database and SQL
  Spring 5.0
  ...
```

### Step 3 — Select CSV File

All `.csv` files in the current directory are listed. Pick your question file.

```
Select CSV File
---------------
  stack.csv
  java_basics.csv
  ...
```

### Step 4 — CSV Validation

The app checks that your CSV has the correct headers and at least one row.

```
CSV validation successful
File : stack.csv
Questions detected (min): 1+
```

### Step 5 — Upload Progress (Live)

Questions upload one by one with a **1 second delay** between each. The screen updates live after every question:

```
Uploading... 12 / 30
Success: 10    Duplicate: 1    Failed: 0    Skipped: 1

+---+--------------------------------+-----------+------------------------------+
| # | Question Title                 | Status    | Error                        |
+---+--------------------------------+-----------+------------------------------+
| 1 | Stack Basic Principle          | SUCCESS   |                              |
| 2 | Primary Stack Operations       | SUCCESS   |                              |
| 3 | Stack Peek Operation           | DUPLICATE | questionTitle is already ex. |
| 4 | Stack Overflow Condition       | SKIPPED   | could not convert string...  |
| 5 | Stack Underflow Condition      | SUCCESS   |                              |
+---+--------------------------------+-----------+------------------------------+

Uploading next question...
```

**Status meanings:**

| Status    | Meaning                                                                |
| --------- | ---------------------------------------------------------------------- |
| SUCCESS   | Uploaded and saved to local database                                   |
| DUPLICATE | Question with same title already exists in that chapter                |
| FAILED    | Server returned an error                                               |
| SKIPPED   | Bad CSV row (e.g. missing field, invalid data) — skipped automatically |

If your session expires mid-upload, the process stops and asks you to login again.

### Step 6 — Scrollable Report

After all uploads finish, press any key to open the full scrollable report.

```
Upload Report  |  Success: 25  Duplicate: 3  Failed: 0  Skipped: 2

+---+--------------------------------+-----------+------------------------------+
| # | Question Title                 | Status    | Error                        |
+---+--------------------------------+-----------+------------------------------+
| 1 | Stack Basic Principle          | SUCCESS   |                              |
| 2 | Primary Stack Operations       | SUCCESS   |                              |
|   | ...                            |           |                              |
|30 | Middle Element LinkedList      | SUCCESS   |                              |
+---+--------------------------------+-----------+------------------------------+

Showing 1-20 of 30
Up/Down scroll   Esc/q return
```

| Key                     | Action              |
| ----------------------- | ------------------- |
| `Up` / `Down`           | Scroll one row      |
| `Page Up` / `Page Down` | Scroll one page     |
| `Esc` or `q`            | Return to main menu |

---

## CSV File Format

Your CSV must have these exact headers in this order:

```
questionTitle,questionDescription,optionA,optionB,optionC,optionD,correctOption,marks,difficulty
```

| Field               | Example                              | Notes                                    |
| ------------------- | ------------------------------------ | ---------------------------------------- |
| questionTitle       | Stack Basic Principle                | Short title                              |
| questionDescription | Which principle does a Stack follow? | **Quote with `"` if it contains commas** |
| optionA–D           | FIFO, LIFO, etc.                     | Four options                             |
| correctOption       | B                                    | A, B, C, or D                            |
| marks               | 2                                    | Numeric value                            |
| difficulty          | EASY                                 | EASY, MEDIUM, or HARD                    |

### Example

```csv
questionTitle,questionDescription,optionA,optionB,optionC,optionD,correctOption,marks,difficulty
Stack Principle,Which principle does a Stack follow?,FIFO,LIFO,Random,Circular,B,2,EASY
Array Stack,"In array stack, what tracks the top?",front,rear,top,head,C,3,MEDIUM
```

**Common mistake:** If your description has a comma and isn't quoted, the CSV columns shift and upload fails. Always wrap such fields in double quotes.

---

## Logout

Select **Logout** from the main menu. Your session is cleared locally.

---

## Navigation (All Screens)

| Key           | Action            |
| ------------- | ----------------- |
| `Up` / `Down` | Move selection    |
| `Enter`       | Confirm selection |
| `Esc`         | Cancel / go back  |

