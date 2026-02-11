@echo off
REM TopBrains CLI — Windows Setup & Check

setlocal EnableDelayedExpansion

set PASS=0
set FAIL=0
set WARN=0

echo.
echo =====================================
echo   TopBrains CLI — Windows Setup
echo =====================================
echo.

REM -------- Python --------
echo -- Python --
python --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%v in ('python --version 2^>^&1') do set PY_VER=%%v
    echo   [OK]   Python found: !PY_VER!
    set /a PASS+=1

    for /f %%m in ('python -c "import sys; print(sys.version_info.minor)"') do set PY_MINOR=%%m
    if !PY_MINOR! geq 9 (
        echo   [OK]   Python version ^>= 3.9
        set /a PASS+=1
    ) else (
        echo   [FAIL] Python 3.9+ required ^(found 3.!PY_MINOR!^)
        set /a FAIL+=1
    )
) else (
    echo   [FAIL] Python not found
    echo.
    echo   Install Python:
    echo     1. Go to https://www.python.org/downloads/
    echo     2. Download latest Python 3
    echo     3. IMPORTANT: Check "Add Python to PATH" during install
    echo     4. Restart this terminal after install
    echo.
    set /a FAIL+=1
)

REM -------- Package Manager --------
echo.
echo -- Package Manager --
uv --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%v in ('uv --version 2^>^&1') do echo   [OK]   uv found: %%v
    set /a PASS+=1
) else (
    pip --version >nul 2>&1
    if %errorlevel% equ 0 (
        echo   [OK]   pip found
        set /a PASS+=1
    ) else (
        echo   [FAIL] No package manager found
        echo.
        echo   Install uv ^(recommended^):
        echo     powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
        echo.
        set /a FAIL+=1
    )
)

REM -------- Virtual Environment --------
echo.
echo -- Virtual Environment --
if exist ".venv\" (
    echo   [OK]   .venv exists
    set /a PASS+=1
) else (
    echo   Creating .venv...
    python -m venv .venv >nul 2>&1
    if exist ".venv\" (
        echo   [OK]   .venv created
        set /a PASS+=1
    ) else (
        echo   [FAIL] Could not create .venv
        set /a FAIL+=1
    )
)

if exist ".venv\Scripts\python.exe" (
    for /f "tokens=*" %%v in ('.venv\Scripts\python --version 2^>^&1') do echo   [OK]   .venv Python: %%v
    set /a PASS+=1
) else (
    echo   [FAIL] .venv\Scripts\python.exe not found
    set /a FAIL+=1
)

REM -------- Install Dependencies --------
echo.
echo -- Dependencies --
if exist ".venv\Scripts\python.exe" (
    if exist "requirements.txt" (
        REM Check if missing
        set NEED_INSTALL=0
        .venv\Scripts\python -c "import requests" >nul 2>&1
        if %errorlevel% neq 0 set NEED_INSTALL=1
        .venv\Scripts\python -c "import aiohttp" >nul 2>&1
        if %errorlevel% neq 0 set NEED_INSTALL=1

        if !NEED_INSTALL! equ 1 (
            echo   Installing dependencies...
            uv pip install -r requirements.txt >nul 2>&1
            if %errorlevel% neq 0 (
                .venv\Scripts\pip install -r requirements.txt >nul 2>&1
            )
        )

        for %%p in (requests aiohttp) do (
            .venv\Scripts\python -c "import %%p" >nul 2>&1
            if !errorlevel! equ 0 (
                echo   [OK]   %%p
                set /a PASS+=1
            ) else (
                echo   [FAIL] %%p not installed
                echo          Run: uv pip install -r requirements.txt
                set /a FAIL+=1
            )
        )
    ) else (
        echo   [WARN] requirements.txt missing
        set /a WARN+=1
    )
) else (
    echo   [WARN] Skipping ^(.venv not ready^)
    set /a WARN+=1
)

REM -------- Curses (Windows needs windows-curses) --------
echo.
echo -- Terminal --
if exist ".venv\Scripts\python.exe" (
    .venv\Scripts\python -c "import curses" >nul 2>&1
    if %errorlevel% equ 0 (
        echo   [OK]   curses module available
        set /a PASS+=1
    ) else (
        echo   Installing windows-curses...
        uv pip install windows-curses >nul 2>&1
        if %errorlevel% neq 0 (
            .venv\Scripts\pip install windows-curses >nul 2>&1
        )
        .venv\Scripts\python -c "import curses" >nul 2>&1
        if !errorlevel! equ 0 (
            echo   [OK]   windows-curses installed
            set /a PASS+=1
        ) else (
            echo   [FAIL] curses not available. Run: pip install windows-curses
            set /a FAIL+=1
        )
    )
)

REM -------- Execution Policy --------
echo.
echo -- Windows Specific --
for /f "tokens=*" %%p in ('powershell -Command "Get-ExecutionPolicy" 2^>nul') do set EXEC_POL=%%p
if defined EXEC_POL (
    if "!EXEC_POL!"=="Restricted" (
        echo   [WARN] PowerShell ExecutionPolicy is Restricted
        echo          Fix: Open PowerShell as Admin and run:
        echo          Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
        set /a WARN+=1
    ) else (
        echo   [OK]   ExecutionPolicy: !EXEC_POL!
        set /a PASS+=1
    )
)

REM -------- Project Files --------
echo.
echo -- Project Files --
for %%f in (main.py auth.py db.py api_guard.py bulk_question_uploader.py syllabus_selector.py chapter_selector.py csv_selector.py table_renderer.py requirements.txt) do (
    if exist "%%f" (
        echo   [OK]   %%f
        set /a PASS+=1
    ) else (
        echo   [FAIL] %%f missing
        set /a FAIL+=1
    )
)

REM -------- CSV Files --------
echo.
echo -- CSV Files --
set CSV_COUNT=0
for %%f in (*.csv) do (
    if not "%%f"=="*.csv" (
        set /a CSV_COUNT+=1
        echo          %%f
    )
)
if !CSV_COUNT! gtr 0 (
    echo   [OK]   !CSV_COUNT! CSV file^(s^) found
    set /a PASS+=1
) else (
    echo   [WARN] No CSV files in current directory
    set /a WARN+=1
)

REM -------- Network --------
echo.
echo -- Network --
ping -n 1 -w 5000 topbrains.com >nul 2>&1
if %errorlevel% equ 0 (
    echo   [OK]   topbrains.com is reachable
    set /a PASS+=1
) else (
    echo   [FAIL] Cannot reach topbrains.com — check internet
    set /a FAIL+=1
)

REM -------- Summary --------
echo.
echo =====================================
echo   Results: !PASS! passed, !FAIL! failed, !WARN! warnings
echo =====================================

if !FAIL! gtr 0 (
    echo.
    echo   Fix the [FAIL] items above, then run this script again.
    echo.
    pause
    exit /b 1
) else (
    echo.
    echo   All good! Start the app:
    echo.
    echo     .venv\Scripts\activate
    echo     python main.py
    echo.
    pause
    exit /b 0
)
