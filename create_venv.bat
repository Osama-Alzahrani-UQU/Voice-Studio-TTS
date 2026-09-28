@echo off
chcp 65001 >nul
title Setup Python Virtual Environment for LocalTTS_App
echo Creating Python virtual environment in "%~dp0venv"...

python -m venv "%~dp0venv"
if errorlevel 1 (
    echo Error creating virtual environment.
    pause
    exit /b 1
)

echo Activating virtual environment...
call "%~dp0venv\Scripts\activate.bat"

echo Installing required packages...
python -m pip install --upgrade pip
python -m pip install -r "%~dp0requirements.txt"
python -m pip install coqui-tts

echo Virtual environment setup complete!
pause
