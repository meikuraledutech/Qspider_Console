#!/bin/bash

# TopBrains CLI — Mac/Linux Setup & Check

PASS=0
FAIL=0
WARN=0

pass() { echo "  [OK]   $1"; ((PASS++)); }
fail() { echo "  [FAIL] $1"; ((FAIL++)); }
warn() { echo "  [WARN] $1"; ((WARN++)); }

echo ""
echo "====================================="
echo "  TopBrains CLI — Mac/Linux Setup"
echo "====================================="
echo ""

# -------- Python --------
echo "-- Python --"
if command -v python3 &>/dev/null; then
    PY_VER=$(python3 --version 2>&1)
    pass "Python3 found: $PY_VER"

    PY_MINOR=$(python3 -c "import sys; print(sys.version_info.minor)")
    if [ "$PY_MINOR" -ge 9 ]; then
        pass "Python version >= 3.9"
    else
        fail "Python 3.9+ required (found 3.$PY_MINOR)"
        echo ""
        echo "  Install latest Python:"
        echo "    Mac  : brew install python3"
        echo "    Linux: sudo apt install python3"
        echo ""
    fi
else
    fail "Python3 not found"
    echo ""
    echo "  Install Python:"
    echo "    Mac  : brew install python3"
    echo "    Linux: sudo apt install python3"
    echo "    Or download from https://www.python.org/downloads/"
    echo ""
fi

# -------- Package Manager --------
echo ""
echo "-- Package Manager --"
if command -v uv &>/dev/null; then
    pass "uv found: $(uv --version 2>&1)"
elif command -v pip3 &>/dev/null; then
    pass "pip3 found"
else
    fail "No package manager found"
    echo ""
    echo "  Install uv (recommended):"
    echo "    curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo ""
fi

# -------- Virtual Environment --------
echo ""
echo "-- Virtual Environment --"
if [ -d ".venv" ]; then
    pass ".venv exists"
else
    echo "  Creating .venv..."
    python3 -m venv .venv 2>/dev/null
    if [ -d ".venv" ]; then
        pass ".venv created"
    else
        fail "Could not create .venv"
    fi
fi

if [ -f ".venv/bin/python" ]; then
    VENV_PY=$(.venv/bin/python --version 2>&1)
    pass ".venv Python: $VENV_PY"
else
    fail ".venv/bin/python not found"
fi

# -------- Install Dependencies --------
echo ""
echo "-- Dependencies --"
if [ -f ".venv/bin/python" ] && [ -f "requirements.txt" ]; then
    MISSING=0
    for pkg in requests aiohttp; do
        if ! .venv/bin/python -c "import $pkg" 2>/dev/null; then
            MISSING=1
            break
        fi
    done

    if [ "$MISSING" -eq 1 ]; then
        echo "  Installing dependencies..."
        if command -v uv &>/dev/null; then
            uv pip install -r requirements.txt 2>&1 | tail -1
        else
            .venv/bin/pip install -r requirements.txt 2>&1 | tail -1
        fi
    fi

    for pkg in requests aiohttp; do
        if .venv/bin/python -c "import $pkg" 2>/dev/null; then
            pass "$pkg"
        else
            fail "$pkg not installed"
        fi
    done
else
    warn "Skipping (venv or requirements.txt missing)"
fi

# -------- Curses --------
echo ""
echo "-- Terminal --"
if [ -n "$TERM" ]; then
    pass "TERM: $TERM"
else
    warn "TERM not set. Curses UI may not work."
fi

if [ -f ".venv/bin/python" ]; then
    if .venv/bin/python -c "import curses" 2>/dev/null; then
        pass "curses module available"
    else
        fail "curses module not available"
    fi
fi

# -------- Project Files --------
echo ""
echo "-- Project Files --"
for f in main.py auth.py db.py api_guard.py bulk_question_uploader.py \
         syllabus_selector.py chapter_selector.py csv_selector.py \
         table_renderer.py requirements.txt; do
    if [ -f "$f" ]; then
        pass "$f"
    else
        fail "$f missing"
    fi
done

# -------- CSV Files --------
echo ""
echo "-- CSV Files --"
CSV_COUNT=$(ls *.csv 2>/dev/null | wc -l | tr -d ' ')
if [ "$CSV_COUNT" -gt 0 ]; then
    pass "$CSV_COUNT CSV file(s) found"
    ls *.csv 2>/dev/null | while read f; do echo "         $f"; done
else
    warn "No CSV files in current directory"
fi

# -------- Network --------
echo ""
echo "-- Network --"
if curl -s --connect-timeout 5 --max-time 10 -o /dev/null -w "%{http_code}" "https://topbrains.com" 2>/dev/null | grep -q "200\|301\|302"; then
    pass "topbrains.com is reachable"
else
    fail "Cannot reach topbrains.com — check internet"
fi

# -------- Summary --------
echo ""
echo "====================================="
echo "  Results: $PASS passed, $FAIL failed, $WARN warnings"
echo "====================================="

if [ "$FAIL" -gt 0 ]; then
    echo ""
    echo "  Fix the [FAIL] items above, then run this script again."
    echo ""
    exit 1
else
    echo ""
    echo "  All good! Start the app:"
    echo ""
    echo "    source .venv/bin/activate"
    echo "    python main.py"
    echo ""
    exit 0
fi
