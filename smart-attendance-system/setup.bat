@echo off
REM Smart Attendance System - Quick Setup Script for Windows

echo ================================
echo Smart Attendance System Setup
echo ================================
echo.

REM Get the directory where this script is located
cd /d "%~dp0"

REM Check Python version
echo Checking Python installation...
python --version
echo.

REM Create virtual environment in current directory
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo ================================
echo Setup Complete!
echo ================================
echo.
echo To start the application:
echo 1. Activate virtual environment: venv\Scripts\activate.bat
echo 2. Run the server: python backend\app.py
echo 3. Open browser: http://localhost:5000
echo.
echo ================================
pause
