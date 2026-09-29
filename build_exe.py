r"""
build_exe.py - Automated PyInstaller Compilation Script
------------------------------------------------------
Compiles the application into a standalone Windows executable (.exe) with
embedded custom taskbar icon, header branding assets, and speaker samples.
"""

import os
import sys
import subprocess
from create_assets import generate_app_assets

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def build():
    print("==================================================")
    print("      Building LocalTTS_App Standalone EXE        ")
    print("==================================================")

    # 1. Ensure assets and speaker reference audio samples are present
    assets_dir = os.path.join(BASE_DIR, "assets")
    speakers_dir = os.path.join(BASE_DIR, "speakers")
    os.makedirs(speakers_dir, exist_ok=True)
    generate_app_assets(assets_dir)

    icon_path = os.path.join(assets_dir, "app_icon.ico")
    main_script = os.path.join(BASE_DIR, "main.py")

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--name=LocalTTS_App",
        f"--icon={icon_path}",
        f"--add-data={assets_dir};assets",
        f"--add-data={speakers_dir};speakers",
        "--collect-all=customtkinter",
        "--collect-all=TTS",
        "--hidden-import=TTS",
        "--hidden-import=TTS.api",
        "--hidden-import=TTS.utils",
        "--hidden-import=TTS.tts",
        "--collect-all=mutagen",
        "--hidden-import=mutagen",
        "--collect-all=pydub",
        "--hidden-import=pydub",
        "--collect-all=pysbd",
        "--hidden-import=pysbd",
        "--collect-all=librosa",
        "--hidden-import=librosa",
        "--collect-all=scipy",
        "--hidden-import=scipy",
        "--collect-all=numba",
        "--hidden-import=numba",
        "--collect-all=einops",
        "--hidden-import=einops",
        "--collect-all=torchaudio",
        "--hidden-import=torchaudio",
        "--collect-all=trainer",
        "--hidden-import=trainer",
        "--collect-all=pandas",
        "--hidden-import=pandas",
        "--collect-all=gruut",
        "--hidden-import=gruut",
        "--collect-all=g2pkk",
        "--hidden-import=g2pkk",
        "--collect-all=bangla",
        "--hidden-import=bangla",
        "--collect-all=bnnumerizer",
        "--hidden-import=bnnumerizer",
        "--collect-all=bnunicodenormalizer",
        "--hidden-import=bnunicodenormalizer",
        "--collect-all=hangul_romanize",
        "--hidden-import=hangul_romanize",
        "--collect-all=jamo",
        "--hidden-import=jamo",
        "--collect-all=jieba",
        "--hidden-import=jieba",
        "--collect-all=pypinyin",
        "--hidden-import=pypinyin",
        "--collect-all=anyascii",
        "--hidden-import=anyascii",
        "--collect-all=coqpit",
        "--hidden-import=coqpit",
        "--collect-all=encodec",
        "--hidden-import=encodec",
        "--collect-all=inflect",
        "--hidden-import=inflect",
        "--collect-all=nltk",
        "--hidden-import=nltk",
        "--collect-all=unidecode",
        "--hidden-import=unidecode",
        "--collect-all=audioread",
        "--hidden-import=audioread",
        "--collect-all=soxr",
        "--hidden-import=soxr",
        "--collect-all=lazy_loader",
        "--hidden-import=lazy_loader",
        "--collect-all=pyarabic",
        "--hidden-import=pyarabic",
        "--collect-all=tashaphyne",
        "--hidden-import=tashaphyne",
        "--collect-all=omnivoice",
        "--hidden-import=omnivoice",
        "--collect-all=accelerate",
        "--hidden-import=accelerate",
        "--collect-all=webdataset",
        "--hidden-import=webdataset",
        "--collect-all=tensorboardX",
        "--hidden-import=tensorboardX",
        "--hidden-import=audio_dsp",
        "--hidden-import=ssml_lite",
        "--hidden-import=mcp_server",
        "--hidden-import=cli_synthesizer",
        main_script,
    ]

    print(f"[Build] Executing command: {' '.join(cmd)}")
    subprocess.check_call(cmd, cwd=BASE_DIR)

    exe_out = os.path.join(BASE_DIR, "dist", "LocalTTS_App", "LocalTTS_App.exe")
    print("==================================================")
    print("   Build Successful! Executable ready at:         ")
    print(f"   {exe_out}")
    print("==================================================")


if __name__ == "__main__":
    build()
