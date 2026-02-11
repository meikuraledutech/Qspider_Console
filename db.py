import sqlite3
import os
import json

# ---------- DB PATH ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "app.db")


def get_conn():
    return sqlite3.connect(DB_PATH)


# ---------- INIT ----------
def init_db():
    conn = get_conn()
    cur = conn.cursor()

    # session table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS auth_session (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id TEXT NOT NULL,
            user_name TEXT NOT NULL,
            user_email TEXT NOT NULL,
            user_phone TEXT,
            user_role TEXT NOT NULL,
            user_status TEXT NOT NULL,

            organization_id TEXT NOT NULL,
            organization_name TEXT NOT NULL,
            organization_type TEXT NOT NULL,

            access_token TEXT NOT NULL,
            refresh_token TEXT NOT NULL,

            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # upload log table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS question_upload_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            chapter_id TEXT,
            question_title TEXT,
            question_id TEXT,
            status TEXT,
            error TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # questions table – stores full API response
    cur.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id TEXT UNIQUE NOT NULL,
            version_id TEXT,
            question_title TEXT,
            question_description TEXT,
            question_type TEXT,
            difficulty_level TEXT,
            marks REAL,
            duration REAL,
            options_json TEXT,
            correct_options TEXT,
            answer_explanation TEXT,
            parent_id TEXT,
            parent_type TEXT,
            subject_reference TEXT,
            organization_reference TEXT,
            status TEXT,
            scope TEXT,
            source_category TEXT,
            source TEXT,
            applications TEXT,
            created_by_name TEXT,
            created_by_email TEXT,
            api_created_at TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


# ---------- SESSION ----------
def save_session(s):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("DELETE FROM auth_session")

    cur.execute("""
        INSERT INTO auth_session (
            user_id, user_name, user_email, user_phone,
            user_role, user_status,
            organization_id, organization_name, organization_type,
            access_token, refresh_token
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        s["user_id"],
        s["user_name"],
        s["user_email"],
        s["user_phone"],
        s["user_role"],
        s["user_status"],
        s["organization_id"],
        s["organization_name"],
        s["organization_type"],
        s["access_token"],
        s["refresh_token"]
    ))

    conn.commit()
    conn.close()


def get_session():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            user_id, user_name, user_email, user_phone,
            user_role, user_status,
            organization_id, organization_name, organization_type,
            access_token, refresh_token
        FROM auth_session
        LIMIT 1
    """)

    row = cur.fetchone()
    conn.close()
    return row


def clear_session():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM auth_session")
    conn.commit()
    conn.close()


# ---------- UPLOAD LOG ----------
def log_upload(user_id, chapter_id, title, qid, status, error=None):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO question_upload_log
        (user_id, chapter_id, question_title, question_id, status, error)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, chapter_id, title, qid, status, error))

    conn.commit()
    conn.close()

def get_upload_report(user_id, chapter_id):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            question_title,
            status,
            question_id,
            error,
            created_at
        FROM question_upload_log
        WHERE user_id = ? AND chapter_id = ?
        ORDER BY id DESC
    """, (user_id, chapter_id))

    rows = cur.fetchall()
    conn.close()
    return rows


# ---------- QUESTIONS ----------
def save_question(resp):
    """Save full question API response to questions table."""
    conn = get_conn()
    cur = conn.cursor()

    ver = resp.get("version", {})
    sol = ver.get("solution", {})

    cur.execute("""
        INSERT OR IGNORE INTO questions (
            question_id, version_id, question_title,
            question_description, question_type, difficulty_level,
            marks, duration, options_json, correct_options,
            answer_explanation, parent_id, parent_type,
            subject_reference, organization_reference,
            status, scope, source_category, source,
            applications, created_by_name, created_by_email,
            api_created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        resp.get("id"),
        ver.get("id"),
        resp.get("questionTitle"),
        ver.get("questionDescription"),
        resp.get("type"),
        resp.get("difficultyLevel"),
        ver.get("marks"),
        ver.get("duration"),
        json.dumps(sol.get("options", {})),
        json.dumps(sol.get("correctOptions", [])),
        sol.get("answerExplanation", ""),
        resp.get("parentId"),
        resp.get("parentType"),
        resp.get("subjectReference"),
        resp.get("organizationReference"),
        resp.get("status"),
        resp.get("scope"),
        resp.get("sourceCategory"),
        resp.get("source"),
        json.dumps(resp.get("applications", [])),
        ver.get("createdByName"),
        ver.get("createdByEmail"),
        ver.get("createdOn"),
    ))

    conn.commit()
    conn.close()


def get_questions_by_chapter(chapter_id):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            question_id, question_title, question_type,
            difficulty_level, marks, status, correct_options,
            api_created_at
        FROM questions
        WHERE parent_id = ?
        ORDER BY id DESC
    """, (chapter_id,))

    rows = cur.fetchall()
    conn.close()
    return rows
