@echo off
cd /d "%~dp0"
echo ==============================================
echo   STUDENT ASSIGNMENT TRACKER - TASKWISE
echo ==============================================
if not exist ".venv\Scripts\python.exe" (
    echo Creating Python virtual environment...
    py -3.14 -m venv .venv
    if errorlevel 1 py -m venv .venv
)
if not exist ".venv\Scripts\python.exe" (
    echo Could not create the virtual environment. Install Python and try again.
    pause
    exit /b 1
)
echo Installing project requirements...
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto error
echo Applying database migrations...
.venv\Scripts\python.exe manage.py migrate
if errorlevel 1 goto error
echo Starting the development server...
.venv\Scripts\python.exe manage.py runserver
goto end
:error
echo Setup stopped because a command failed. Read README.md for troubleshooting.
 pause
:end
