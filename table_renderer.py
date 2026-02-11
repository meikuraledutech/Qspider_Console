import curses


def draw_table(stdscr, headers, rows, start_y=2, start_x=2, max_rows=None):
    """
    Draws a formatted table inside curses screen.
    If max_rows is None, fits as many as the screen allows.
    """
    h, w = stdscr.getmaxyx()

    if max_rows is None:
        max_rows = h - start_y - 4  # leave room for borders + footer

    rows = rows[:max_rows]

    # Calculate column widths
    col_widths = []

    for i, header in enumerate(headers):
        max_width = len(header)

        for row in rows:
            cell = str(row[i]) if i < len(row) else ""
            max_width = max(max_width, len(cell))

        col_widths.append(max_width + 2)

    # Draw top border
    y = start_y
    x = start_x

    def draw_separator():
        nonlocal y
        line = "+"
        for cw in col_widths:
            line += "-" * cw + "+"
        stdscr.addstr(y, x, line[: w - x - 1])

    # Top line
    draw_separator()
    y += 1

    # Header row
    pos = x + 1
    stdscr.addstr(y, x, "|")
    for i, header in enumerate(headers):
        stdscr.addstr(y, pos, header.ljust(col_widths[i])[: w - pos - 2])
        pos += col_widths[i]
        stdscr.addstr(y, pos, "|")
        pos += 1
    y += 1

    # Header separator
    draw_separator()
    y += 1

    # Data rows
    for row in rows:
        pos = x + 1
        stdscr.addstr(y, x, "|")

        for i in range(len(headers)):
            cell = str(row[i]) if i < len(row) else ""
            stdscr.addstr(y, pos, cell.ljust(col_widths[i])[: w - pos - 2])
            pos += col_widths[i]
            stdscr.addstr(y, pos, "|")
            pos += 1

        y += 1

    # Bottom line
    draw_separator()

    stdscr.refresh()


def scrollable_table(stdscr, title, headers, rows):
    """
    Full-screen scrollable table with keyboard navigation.
    Up/Down to scroll, Esc or q to exit.
    """
    curses.curs_set(0)
    scroll = 0

    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        stdscr.addstr(1, 2, title[: w - 4], curses.A_BOLD)

        visible_rows = h - 8  # header(3 lines) + footer(2) + table borders(3)
        total = len(rows)

        max_scroll = max(0, total - visible_rows)
        scroll = max(0, min(scroll, max_scroll))

        page = rows[scroll: scroll + visible_rows]
        draw_table(stdscr, headers, page, start_y=3, max_rows=visible_rows)

        # footer
        pos_text = f"Showing {scroll + 1}-{scroll + len(page)} of {total}"
        stdscr.addstr(h - 2, 2, pos_text)
        stdscr.addstr(h - 1, 2, "Up/Down scroll   Esc/q return"[: w - 4])
        stdscr.refresh()

        key = stdscr.getch()

        if key == curses.KEY_UP:
            scroll = max(0, scroll - 1)
        elif key == curses.KEY_DOWN:
            scroll = min(max_scroll, scroll + 1)
        elif key == curses.KEY_PPAGE:  # Page Up
            scroll = max(0, scroll - visible_rows)
        elif key == curses.KEY_NPAGE:  # Page Down
            scroll = min(max_scroll, scroll + visible_rows)
        elif key in (27, ord('q')):  # Esc or q
            break
