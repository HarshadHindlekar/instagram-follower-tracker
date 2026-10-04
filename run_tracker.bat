@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

if not exist "%~dp0logs" mkdir "%~dp0logs"
if not exist "%~dp0output" mkdir "%~dp0output"

echo ======================================================
echo Running Instagram Follower Tracker
echo ======================================================

"C:\Users\HARSHAD\AppData\Local\Programs\Python\Python311\python.exe" "%~dp0instagram_tracker.py"
pause
