@echo off
title Voice Studio
cd /d "%~dp0"
if exist "%~dp0dist\LocalTTS_App\LocalTTS_App.exe" (
    start "" /D "%~dp0" "%~dp0dist\LocalTTS_App\LocalTTS_App.exe"
) else (
    python "%~dp0main.py"
)
