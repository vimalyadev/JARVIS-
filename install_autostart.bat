@echo off
title Install J.A.R.V.I.S. Background Autostart
cd /d "%~dp0"

echo ====================================================
echo   INSTALLING J.A.R.V.I.S. SILENT WINDOWS AUTOSTART
echo ====================================================
echo.
echo Jarvis will be set up to start automatically in the background
echo whenever you turn on or log in to your laptop.
echo.

python desktop\install_startup.py

echo.
echo All set! Jarvis is now registered to start on boot.
pause
