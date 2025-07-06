@echo off
REM Batch file to start ImageMan PyQt5 application

setlocal
set PYTHON_EXEC=python
set APP_DIR=%~dp0imageman

REM If a directory argument is given, pass it to the app
if "%~1"=="" (
    %PYTHON_EXEC% "%APP_DIR%\main.py"
) else (
    %PYTHON_EXEC% "%APP_DIR%\main.py" "%~1"
)
endlocal
