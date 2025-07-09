@echo off
REM Batch file to start ImageMan PyQt5 application

setlocal
set PYTHON_EXEC="%~dp0venv\Scripts\python.exe"
set APP_DIR=%~dp0imageman

REM Change to the project root directory
cd /d "%~dp0"

REM If a directory argument is given, pass it to the app
if "%~1"=="" (
    %PYTHON_EXEC% "%APP_DIR%\main.py"
) else (
    %PYTHON_EXEC% "%APP_DIR%\main.py" "%~1"
)
endlocal
