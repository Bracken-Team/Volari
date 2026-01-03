@echo off
REM Build Volari Windows Executable
REM Run this script on a Windows machine in Command Prompt or PowerShell

echo Installing dependencies...
pip install -r requirements.txt
pip install pyinstaller

echo Building executable...
rmdir /s /q dist\Volari build\Volari
pyinstaller volari.spec --clean

echo.
echo Build complete! Executable is located at dist\Volari.exe
pause
