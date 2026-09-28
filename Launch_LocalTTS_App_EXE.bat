@echo off
title Voice Studio
if exist "%~dp0dist\LocalTTS_App\LocalTTS_App.exe" (
    start "" "%~dp0dist\LocalTTS_App\LocalTTS_App.exe"
) else (
    python "%~dp0main.py"
)
