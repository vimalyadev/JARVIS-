@echo off
title J.A.R.V.I.S. Assistant Launcher
cd /d "%~dp0"

echo ====================================================
echo        INITIALIZING J.A.R.V.I.S. PERSONAL AI
echo ====================================================
echo.

:: Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.10+ and check 'Add Python to PATH'.
    pause
    exit /b
)

:: Check if requirements are installed
if not exist ".installed_flag" (
    echo [SETUP] Installing required dependencies...
    pip install -r requirements.txt
    if errorlevel 0 (
        echo dependencies installed > .installed_flag
    )
)

:: Create default .env if not present
if not exist ".env" (
    echo [CONFIG] Creating default .env configuration...
    copy .env.example .env >nul
)

echo.
echo [STATUS] Starting J.A.R.V.I.S. Desktop & Mobile Assistant...
echo.
python desktop\run_desktop.py
pause
