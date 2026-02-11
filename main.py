import curses

from db import init_db, get_session
from auth import login, logout
from syllabus_selector import select_syllabus
from chapter_selector import select_chapter
from csv_selector import select_csv, validate_csv
from bulk_question_uploader import upload_all_questions
from updater import update_app


# ---------------- UI HELPERS ---------------- #

def draw_menu(stdscr, title, options, selected):
    stdscr.clear()
    h, w = stdscr.getmaxyx()

    stdscr.addstr(1, 2, title[: w - 4], curses.A_BOLD)
    stdscr.addstr(2, 2, "-" * min(len(title), w - 4))

    for i, opt in enumerate(options):
        y = 4 + i
        if y >= h - 3:
            break

        text = opt[: w - 8]
        if i == selected:
            stdscr.addstr(y, 4, text, curses.A_REVERSE)
        else:
            stdscr.addstr(y, 4, text)

    stdscr.addstr(h - 2, 2, "↑ ↓ move   Enter select")
    stdscr.refresh()


# ---------------- MAIN MENU LOOP ---------------- #

def menu_loop(stdscr):
    curses.curs_set(0)
    stdscr.keypad(True)

    while True:
        session = get_session()

        if not session:
            title = "TopBrains CLI"
            options = ["Login", "Update App", "Exit"]
        else:
            user_name = session[1]
            user_role = session[4]
            org_name  = session[7]

            title = f"Welcome {user_name} ({user_role}) | {org_name}"
            options = [
                "Add MCQ Question",
                "Add Programming Question",
                "Update App",
                "Logout",
                "Exit"
            ]

        selected = 0

        # -------- Navigation -------- #
        while True:
            draw_menu(stdscr, title, options, selected)
            key = stdscr.getch()

            if key == curses.KEY_UP:
                selected = (selected - 1) % len(options)
            elif key == curses.KEY_DOWN:
                selected = (selected + 1) % len(options)
            elif key in (10, 13):
                choice = options[selected]
                break

        # -------- Action Handling -------- #

        try:

            if choice == "Login":
                login(stdscr)

            elif choice == "Logout":
                logout()

            elif choice == "Add MCQ Question":
                syllabus = select_syllabus(stdscr)
                if not syllabus:
                    continue

                chapter = select_chapter(
                    stdscr,
                    syllabus["subjectId"],
                    syllabus["syllabusId"]
                )
                if not chapter:
                    continue

                csv_file = select_csv(stdscr)
                if not csv_file:
                    continue

                if not validate_csv(stdscr, csv_file):
                    continue

                session = get_session()
                if not session:
                    continue

                upload_all_questions(
                    stdscr,
                    csv_file,
                    chapter["chapterId"],
                    syllabus["subjectId"],
                    session[6]
                )

            elif choice == "Add Programming Question":
                stdscr.clear()
                stdscr.addstr(5, 4, "🚧 Programming question flow coming next")
                stdscr.addstr(7, 4, "Press any key to return...")
                stdscr.getch()

            elif choice == "Update App":
                update_app(stdscr)

            elif choice == "Exit":
                break

        except Exception as e:
            stdscr.clear()
            stdscr.addstr(5, 4, "⚠ Unexpected error occurred")
            stdscr.addstr(7, 4, str(e)[:100])
            stdscr.addstr(9, 4, "Press any key to continue...")
            stdscr.getch()


# ---------------- ENTRY POINT ---------------- #

def main():
    init_db()
    curses.wrapper(menu_loop)


if __name__ == "__main__":
    main()
