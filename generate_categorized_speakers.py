"""
generate_categorized_speakers.py - Generates distinct male and female reference audio samples
---------------------------------------------------------------------------------------------
Creates speakers/male/ and speakers/female/ and generates
high-quality, distinct .wav reference samples for all voices.
"""

import os
import sys
import numpy as np
import soundfile as sf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xtts_engine import XTTSEngineManager, BASE_APP_DIR

SPEAKERS_DIR = os.path.join(BASE_APP_DIR, "speakers")
MALE_DIR = os.path.join(SPEAKERS_DIR, "male")
FEMALE_DIR = os.path.join(SPEAKERS_DIR, "female")

os.makedirs(MALE_DIR, exist_ok=True)
os.makedirs(FEMALE_DIR, exist_ok=True)

MALE_VOICE_MAP = {
    "Damien_Black": {"model_spk": "Damien Black", "pitch_shift": 0.88, "text": "This is a deep, authoritative male narration voice sample."},
    "Abrahan_Mack": {"model_spk": "Abrahan Mack", "pitch_shift": 1.05, "text": "This is an energetic and clear male conversation voice sample."},
    "Andrew_Kasch": {"model_spk": "Abrahan Mack", "pitch_shift": 0.92, "text": "This is a smooth professional male broadcast voice sample."},
    "Baldur_Otto": {"model_spk": "Abrahan Mack", "pitch_shift": 0.84, "text": "This is a rich, resonant male storyteller voice sample."},
    "Adalberto_Santos": {"model_spk": "Damien Black", "pitch_shift": 0.98, "text": "This is a clear professional male speech sample."},
    "Gideon_Keel": {"model_spk": "Damien Black", "pitch_shift": 0.94, "text": "This is a warm male conversational voice sample."}
}

FEMALE_VOICE_MAP = {
    "Ana_Florence": {"model_spk": "Ana Florence", "pitch_shift": 1.00, "text": "This is a professional and clear female voice sample."},
    "Claribel_Dervux": {"model_spk": "Claribel Dervla", "pitch_shift": 0.96, "text": "This is a warm and articulate female voice sample."},
    "Daisy_Soft": {"model_spk": "Daisy Studious", "pitch_shift": 1.04, "text": "This is a soft and calm female voice sample."},
    "Gracie_MacArthur": {"model_spk": "Gracie Wise", "pitch_shift": 1.02, "text": "This is an expressive female narration voice sample."},
    "Sofia_Medina": {"model_spk": "Sofia Hellen", "pitch_shift": 1.08, "text": "This is a bright and cheerful female voice sample."},
    "Tammie_Smith": {"model_spk": "Tammie Ema", "pitch_shift": 0.98, "text": "This is a natural female voice sample."},
    "Alison_Vervaecke": {"model_spk": "Alison Dietlinde", "pitch_shift": 0.94, "text": "This is a smooth female narrator voice sample."},
    "Brenda_Stenaker": {"model_spk": "Brenda Stern", "pitch_shift": 1.01, "text": "This is a clear female broadcast voice sample."}
}

def modify_pitch(audio_data, factor):
    """Simple speed/pitch modulation via resampling for distinct voice differentiation."""
    if factor == 1.0 or len(audio_data) == 0:
        return audio_data
    indices = np.round(np.arange(0, len(audio_data), factor)).astype(int)
    indices = indices[indices < len(audio_data)]
    return audio_data[indices]

def generate_all():
    print("==================================================")
    print("   Generating Categorized Speaker Audio Samples   ")
    print("==================================================")

    mgr = XTTSEngineManager()
    mgr.initialize()

    # 1. Generate Male Voices
    print("\n--- Generating Male Voice Samples ---")
    for clean_name, cfg in MALE_VOICE_MAP.items():
        wav_path = os.path.join(MALE_DIR, f"{clean_name}.wav")
        print(f"[Male] Generating '{clean_name}' using model '{cfg['model_spk']}'...")
        temp_wav = os.path.join(MALE_DIR, f"temp_{clean_name}.wav")
        try:
            mgr.tts.tts_to_file(
                text=cfg["text"],
                speaker=cfg["model_spk"],
                language="en",
                file_path=temp_wav
            )
            data, sr = sf.read(temp_wav)
            if cfg["pitch_shift"] != 1.0:
                data = modify_pitch(data, cfg["pitch_shift"])
            sf.write(wav_path, data, sr)
            if os.path.exists(temp_wav):
                os.remove(temp_wav)
            print(f"  -> SUCCESS: Created {wav_path}")
        except Exception as e:
            print(f"  -> ERROR generating {clean_name}: {e}")
            sr = 24000
            tone = (np.sin(2 * np.pi * 220 * np.linspace(0, 2, sr * 2)) * 0.1).astype(np.float32)
            sf.write(wav_path, tone, sr)

    # 2. Generate Female Voices
    print("\n--- Generating Female Voice Samples ---")
    for clean_name, cfg in FEMALE_VOICE_MAP.items():
        wav_path = os.path.join(FEMALE_DIR, f"{clean_name}.wav")
        print(f"[Female] Generating '{clean_name}' using model '{cfg['model_spk']}'...")
        temp_wav = os.path.join(FEMALE_DIR, f"temp_{clean_name}.wav")
        try:
            mgr.tts.tts_to_file(
                text=cfg["text"],
                speaker=cfg["model_spk"],
                language="en",
                file_path=temp_wav
            )
            data, sr = sf.read(temp_wav)
            if cfg["pitch_shift"] != 1.0:
                data = modify_pitch(data, cfg["pitch_shift"])
            sf.write(wav_path, data, sr)
            if os.path.exists(temp_wav):
                os.remove(temp_wav)
            print(f"  -> SUCCESS: Created {wav_path}")
        except Exception as e:
            print(f"  -> ERROR generating {clean_name}: {e}")
            sr = 24000
            tone = (np.sin(2 * np.pi * 440 * np.linspace(0, 2, sr * 2)) * 0.1).astype(np.float32)
            sf.write(wav_path, tone, sr)

    print("\n==================================================")
    print(" Categorized Speaker Samples Generation Finished!")
    print(f" Male Directory:   {MALE_DIR}")
    print(f" Female Directory: {FEMALE_DIR}")
    print("==================================================")

if __name__ == "__main__":
    generate_all()
