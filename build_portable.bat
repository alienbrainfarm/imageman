@echo off
REM Build a portable ImageMan.exe using PyInstaller
cd /d %~dp0imageman
pyinstaller --clean --noconfirm imageman.spec
cd ..
echo.
echo Build complete. The EXE will be in imageman\dist\ImageMan.exe
pause
