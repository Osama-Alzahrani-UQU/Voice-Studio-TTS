@echo off
chcp 65001 >nul
title Build LocalTTS_App Standalone EXE
echo Building LocalTTS_App Standalone Executable...
if exist "%~dp0venv\Scripts\activate.bat" (
    call "%~dp0venv\Scripts\activate.bat"
)
python "%~dp0build_exe.py"
pause
