@echo off
REM Invoice App Quick Start Script for Windows

echo ==========================================
echo    Invoice Dashboard - Quick Start
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9 or higher from https://www.python.org
    pause
    exit /b 1
)

echo SUCCESS: Python found

REM Create virtual environment
echo.
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo.
echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

REM Check if uploads folder exists
if not exist "uploads" (
    echo Creating uploads folder...
    mkdir uploads
)

echo.
echo ==========================================
echo    Starting Invoice Dashboard
echo ==========================================
echo.
echo Backend starting on http://localhost:8000
echo API Docs available at http://localhost:8000/docs
echo Open index.html in a web browser
echo.
echo Press CTRL+C to stop the server
echo.

REM Run the app
python app.py

pause
