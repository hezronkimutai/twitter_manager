@echo off
REM Create logs directory if it doesn't exist
if not exist logs mkdir logs

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Set working directory to script location
cd /d "%~dp0"

REM Run Twitter Manager (showing output in console)
python -m src.twitter_manager