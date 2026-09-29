"""
generate_studio_voices.py - Studio-Quality Reference Audio Generator (24kHz Mono 16-bit PCM)
-----------------------------------------------------------------------------------------
Generates crystal-clear, steady broadcasting reference audio samples for XTTS v2 voice cloning.
Saves samples into speakers/male/ and speakers/female/.
"""

import os
import sys
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xtts_engine import XTTSEngineManager, BASE_APP_DIR, MALE_DIR, FEMALE_DIR

os.makedirs(MALE_DIR, exist_ok=True)
os.makedirs(FEMALE_DIR, exist_ok=True)

MALE_PROFILES = {
    "Damien_Black": {
        "model_spk": "Damien Black",
        "speed": 0.92,
        "text": "This is a deep, steady, and professional broadcasting narration voice sample."
    },
    "Abrahan_Mack": {
        "model_spk": "Abrahan Mack",
        "speed": 0.95,
        "text": "This is an energetic, clear, and articulate professional speech sample."
    },
    "Andrew_Kasch": {
        "model_spk": "Abrahan Mack",
        "speed": 0.90,
        "text": "This is a smooth, resonant broadcasting narrator voice sample."
    },
    "Baldur_Otto": {
        "model_spk": "Abrahan Mack",
        "speed": 0.88,
        "text": "This is a rich, warm, and steady male storyteller voice sample."
    },
    "Adalberto_Santos": {
        "model_spk": "Damien Black",
        "speed": 0.94,
        "text": "This is a clear, precise professional narration voice sample."
    },
    "Gideon_Keel": {
        "model_spk": "Damien Black",
        "speed": 0.91,
        "text": "This is a warm, steady conversational male voice sample."
    }
}

FEMALE_PROFILES = {
    "Ana_Florence": {
        "model_spk": "Ana Florence",
        "speed": 0.95,
        "text": "This is a clear, professional, and articulate female narration sample."
    },
    "Claribel_Dervux": {
        "model_spk": "Claribel Dervla",
        "speed": 0.94,
        "text": "This is a warm, steady, and articulate female voice sample."
    },
    "Daisy_Soft": {
        "model_spk": "Daisy Studious",
        "speed": 0.96,
        "text": "This is a soft, smooth, and calm female voice sample."
    },
    "Gracie_MacArthur": {
        "model_spk": "Gracie Wise",
        "speed": 0.94,
        "text": "This is an expressive, clear female broadcasting sample."
    },
    "Sofia_Medina": {
        "model_spk": "Sofia Hellen",
        "speed": 0.96,
        "text": "This is a bright, clear, and professional female voice sample."
    },
    "Tammie_Smith": {
        "model_spk": "Tammie Ema",
        "speed": 0.95,
        "text": "This is a natural, steady female speech sample."
    },
    "Alison_Vervaecke": {
        "model_spk": "Alison Dietlinde",
        "speed": 0.92,
        "text": "This is a smooth, elegant female narrator voice sample."
    },
    "Brenda_Stenaker": {
        "model_spk": "Brenda Stern",
        "speed": 0.95,
        "text": "This is a clear, professional female broadcast voice sample."
    }
}

def normalize_audio(audio_data: np.ndarray, target_sr: int = 24000) -> np.ndarray:
    """Normalizes peak volume to -1 dB and trims silence."""
    if len(audio_data) == 0:
        return audio_data

    # Ensure float32
    audio = audio_data.astype(np.float32)

    # Convert stereo to mono if necessary
    if audio.ndim > 1:
        audio = np.mean(audio, axis=1)

    # Trim leading and trailing silence (< -40 dB)
    abs_audio = np.abs(audio)
    threshold = 0.01 * np.max(abs_audio) if np.max(abs_audio) > 0 else 0.001
    nonzero = np.where(abs_audio > threshold)[0]
    if len(nonzero) > 0:
        start_idx = max(0, nonzero[0] - int(target_sr * 0.05))
        end_idx = min(len(audio), nonzero[-1] + int(target_sr * 0.05))
        audio = audio[start_idx:end_idx]

    # Peak normalization to 0.90 (-0.9 dB)
    max_val = np.max(np.abs(audio))
    if max_val > 0:
        audio = audio * (0.90 / max_val)

    return audio

def generate_studio_samples():
    print("==================================================")
    print("   Generating Studio-Grade Reference Audio Samples  ")
    print("==================================================")

    mgr = XTTSEngineManager()
    mgr.initialize()

    # 1. Male Voices
    print("\n--- Generating Studio Male Voices ---")
    for name, cfg in MALE_PROFILES.items():
        out_path = os.path.join(MALE_DIR, f"{name}.wav")
        temp_wav = os.path.join(MALE_DIR, f"temp_{name}.wav")
        print(f"[Male] Generating studio sample for '{name}'...")
        try:
            mgr.tts.tts_to_file(
                text=cfg["text"],
                speaker=cfg["model_spk"],
                language="en",
                speed=cfg["speed"],
                file_path=temp_wav
            )
            raw_audio, sr = sf.read(temp_wav)
            clean_audio = normalize_audio(raw_audio, target_sr=sr)
            sf.write(out_path, clean_audio, sr, subtype="PCM_16")
            if os.path.exists(temp_wav):
                os.remove(temp_wav)
            print(f"  -> SUCCESS: Created Studio Sample {os.path.basename(out_path)} ({len(clean_audio)/sr:.2f}s)")
        except Exception as err:
            print(f"  -> ERROR generating {name}: {err}")

    # 2. Female Voices
    print("\n--- Generating Studio Female Voices ---")
    for name, cfg in FEMALE_PROFILES.items():
        out_path = os.path.join(FEMALE_DIR, f"{name}.wav")
        temp_wav = os.path.join(FEMALE_DIR, f"temp_{name}.wav")
        print(f"[Female] Generating studio sample for '{name}'...")
        try:
            mgr.tts.tts_to_file(
                text=cfg["text"],
                speaker=cfg["model_spk"],
                language="en",
                speed=cfg["speed"],
                file_path=temp_wav
            )
            raw_audio, sr = sf.read(temp_wav)
            clean_audio = normalize_audio(raw_audio, target_sr=sr)
            sf.write(out_path, clean_audio, sr, subtype="PCM_16")
            if os.path.exists(temp_wav):
                os.remove(temp_wav)
            print(f"  -> SUCCESS: Created Studio Sample {os.path.basename(out_path)} ({len(clean_audio)/sr:.2f}s)")
        except Exception as err:
            print(f"  -> ERROR generating {name}: {err}")

    print("\n==================================================")
    print("   Studio Reference Samples Generation Complete!  ")
    print("==================================================")

if __name__ == "__main__":
    generate_studio_samples()
