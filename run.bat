@echo off
chcp 65001 >nul
title Voice Studio
if exist "%~dp0venv\Scripts\activate.bat" (
    call "%~dp0venv\Scripts\activate.bat"
)
python "%~dp0main.py"
if errorlevel 1 pause
