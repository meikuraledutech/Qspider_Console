from api_guard import api_call, AuthExpired
from db import save_session, clear_session

LOGIN_URL = "https://topbrains.com/subject/v1/auth/login"


# -------- CURSES INPUT HELPERS -------- #

def _text_input(stdscr, y, x, prompt):
    stdscr.addstr(y, x, prompt)
    stdscr.refresh()
    buf = ""

    while True:
        ch = stdscr.getch()

        if ch in (10, 13):
            break
        elif ch in (8, 127):
            buf = buf[:-1]
        elif 32 <= ch <= 126:
            buf += chr(ch)

        stdscr.addstr(y, x + len(prompt), " " * 40)
        stdscr.addstr(y, x + len(prompt), buf)
        stdscr.refresh()

    return buf.strip()


def _password_input(stdscr, y, x, prompt):
    stdscr.addstr(y, x, prompt)
    stdscr.refresh()
    buf = ""

    while True:
        ch = stdscr.getch()

        if ch in (10, 13):
            break
        elif ch in (8, 127):
            buf = buf[:-1]
        elif 32 <= ch <= 126:
            buf += chr(ch)

        stdscr.addstr(y, x + len(prompt), " " * 40)
        stdscr.addstr(y, x + len(prompt), "*" * len(buf))
        stdscr.refresh()

    return buf


# -------- LOGIN -------- #

def login(stdscr):
    stdscr.clear()
    stdscr.addstr(1, 2, "🔐 Login")
    stdscr.addstr(2, 2, "-" * 10)

    user_email = _text_input(stdscr, 4, 4, "User Email : ")
    password = _password_input(stdscr, 6, 4, "Password   : ")

    try:
        data = api_call(
            stdscr,
            "POST",
            LOGIN_URL,
            json={
                "userEmail": user_email,
                "password": password
            },
            message="Logging in..."
        )
    except AuthExpired:
        stdscr.addstr(8, 4, "❌ Login failed")
        stdscr.getch()
        return False

    body = data["response"]["userLoginResponse"]
    user = body["user"]

    session = {
        "user_id": user["id"],
        "user_name": user["name"],
        "user_email": user["email"],
        "user_phone": user.get("phoneNumber"),
        "user_role": user["currentPrivilege"],
        "user_status": user["status"],
        "organization_id": user["organizationId"],
        "organization_name": user["organizationName"],
        "organization_type": user["organizationType"],
        "access_token": body["accessToken"],
        "refresh_token": body["refreshToken"]
    }

    save_session(session)
    return True


def logout():
    clear_session()
