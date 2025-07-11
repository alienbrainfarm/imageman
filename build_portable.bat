@echo off
REM Build a portable ImageMan.exe using PyInstaller

REM Forcefully delete old build artifacts to ensure a clean build
rmdir /s /q imageman\build
rmdir /s /q imageman\dist

taskkill /f /im ImageMan.exe 2>nul
cd /d %~dp0imageman
"%~dp0\venv\Scripts\python.exe" -m PyInstaller --noconfirm imageman.spec
cd ..
echo.
echo Build complete. The EXE will be in imageman\dist\ImageMan.exe
pause
