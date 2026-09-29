r"""
main.py - Entry Point for Voice Studio
--------------------------------------
Configures portable environment variables, sets window icon assets,
and launches the desktop application.
"""

import sys
import os
import traceback

# Guard against None stdout/stderr in PyInstaller --windowed (noconsole) mode
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w", encoding="utf-8")


def get_base_app_dir() -> str:
    """Resolves portable base directory for source and PyInstaller frozen builds."""
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(os.path.abspath(sys.executable))
        if os.path.exists(os.path.join(exe_dir, "tts_models")):
            return exe_dir
        parent_root = os.path.abspath(os.path.join(exe_dir, "..", ".."))
        if os.path.exists(os.path.join(parent_root, "tts_models")):
            return parent_root
        return exe_dir
    return os.path.dirname(os.path.abspath(__file__))


BASE_APP_DIR = get_base_app_dir()

try:
    TTS_MODELS_DIR = os.path.join(BASE_APP_DIR, "tts_models")
    HF_MODELS_DIR = os.path.join(BASE_APP_DIR, "hf_models")
    TORCH_CACHE_DIR = os.path.join(BASE_APP_DIR, "torch_cache")
    TEMP_AUDIO_DIR = os.path.join(BASE_APP_DIR, "temp_audio")
    EXPORTS_DIR = os.path.join(BASE_APP_DIR, "exports")
    ASSETS_DIR = (
        os.path.join(sys._MEIPASS, "assets")
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS") and os.path.exists(os.path.join(sys._MEIPASS, "assets"))
        else os.path.join(BASE_APP_DIR, "assets")
    )

    for _folder in (TTS_MODELS_DIR, HF_MODELS_DIR, TORCH_CACHE_DIR, TEMP_AUDIO_DIR, EXPORTS_DIR, ASSETS_DIR):
        os.makedirs(_folder, exist_ok=True)

    os.environ["TTS_HOME"] = TTS_MODELS_DIR
    os.environ["COQUI_MODEL_PATH"] = TTS_MODELS_DIR
    os.environ["HF_HOME"] = HF_MODELS_DIR
    os.environ["HUGGINGFACE_HUB_CACHE"] = HF_MODELS_DIR
    os.environ["TORCH_HOME"] = TORCH_CACHE_DIR
    os.environ["COQUI_TOS_AGREED"] = "1"

    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    if hasattr(sys.stderr, "reconfigure"):
        try:
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass

    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        if sys._MEIPASS not in sys.path:
            sys.path.insert(0, sys._MEIPASS)
    if BASE_APP_DIR not in sys.path:
        sys.path.insert(0, BASE_APP_DIR)

    try:
        import transformers
        import transformers.utils
        if not hasattr(transformers.utils, "is_numba_available"):
            transformers.utils.is_numba_available = lambda: False
        import transformers.utils.versions as _tuv
        _tuv.require_version = lambda *args, **kwargs: None
        _tuv.require_version_core = lambda *args, **kwargs: None
    except Exception:
        pass

    from create_assets import generate_app_assets
    try:
        if not os.path.exists(os.path.join(ASSETS_DIR, "app_icon.ico")) or not os.path.exists(os.path.join(ASSETS_DIR, "header_banner.png")):
            generate_app_assets(ASSETS_DIR)
    except Exception as e:
        print(f"[Main] Warning generating visual assets: {e}")

    from gui.main_window import XTTSArabicEnglishChatApp
    from audio_player import AudioPlayerController
except BaseException as e:
    with open(os.path.join(BASE_APP_DIR, "exe_crash.log"), "w", encoding="utf-8") as f:
        f.write(traceback.format_exc())
    raise


def main():
    try:
        app = XTTSArabicEnglishChatApp()

        icon_path = os.path.join(ASSETS_DIR, "app_icon.ico")
        if os.path.exists(icon_path):
            try:
                app.iconbitmap(icon_path)
            except Exception:
                pass

        def on_closing():
            try:
                AudioPlayerController().stop_audio()
            except Exception:
                pass
            app.destroy()
            sys.exit(0)

        app.protocol("WM_DELETE_WINDOW", on_closing)
        app.mainloop()
    except BaseException as e:
        with open(os.path.join(BASE_APP_DIR, "exe_crash.log"), "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        raise


if __name__ == "__main__":
    main()
