r"""
generate_speakers.py - Generates reference .wav sample files for all dropdown voices.
"""

import os
import sys
import numpy as np
import soundfile as sf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xtts_engine import XTTSEngineManager, BASE_APP_DIR

SPEAKERS_DIR = os.path.join(BASE_APP_DIR, "speakers")
os.makedirs(SPEAKERS_DIR, exist_ok=True)

def generate_speaker_samples():
    print("==================================================")
    print("      Generating Reference Speaker Audio Files    ")
    print("==================================================")

    mgr = XTTSEngineManager()
    mgr.initialize()

    sm = mgr.tts.synthesizer.tts_model.speaker_manager
    model_speakers = list(sm.speakers.keys()) if sm and hasattr(sm, "speakers") else []
    print(f"Available XTTS model speakers: {len(model_speakers)}")

    # Mapping dropdown display names to model native speaker names or reference sample generation
    SPEAKER_MAP = {
        "Ana Florence": "Ana Florence",
        "Claribel Dervux": "Claribel Dervla",
        "Daisy Soft": "Daisy Studious",
        "Damien Black": "Damien Black",
        "Gideon Keel": "Ana Florence",  # fallback or clone
        "Gracie MacArthur": "Gracie Wise",
        "Sofia Medina": "Sofia Hellen",
        "Tammie Smith": "Tammie Ema",
        "Abrahan Mack": "Abrahan Mack",
        "Adalberto Santos": "Abrahan Mack",
        "Alison Vervaecke": "Alison Dietlinde",
        "Andrew Kasch": "Abrahan Mack",
        "Baldur Otto": "Abrahan Mack",
        "Brenda Stenaker": "Brenda Stern"
    }

    sample_text = "This is a reference voice sample for speech generation."
    
    for display_name in mgr.BUILTIN_SPEAKERS:
        clean_name = display_name.replace(" ", "_")
        wav_path = os.path.join(SPEAKERS_DIR, f"{clean_name}.wav")

        model_spk = SPEAKER_MAP.get(display_name, "Ana Florence")
        if model_spk not in model_speakers:
            model_spk = "Ana Florence"

        print(f"[Generating Sample] '{display_name}' using model voice '{model_spk}' -> {wav_path}")
        try:
            mgr.tts.tts_to_file(
                text=sample_text,
                speaker=model_spk,
                language="en",
                file_path=wav_path
            )
            print(f"  -> SUCCESS: Created {os.path.basename(wav_path)}")
        except Exception as e:
            print(f"  -> ERROR generating for {display_name}: {e}")
            # Fallback: create synthetic silent/tone wav if TTS fails
            sr = 24000
            tone = (np.sin(2 * np.pi * 440 * np.linspace(0, 2, sr * 2)) * 0.1).astype(np.float32)
            sf.write(wav_path, tone, sr)
            print(f"  -> FALLBACK: Created synthetic reference wav at {wav_path}")

    print("==================================================")
    print("   Speaker audio samples generation complete!     ")
    print(f"   Directory: {SPEAKERS_DIR}")
    print("==================================================")

if __name__ == "__main__":
    generate_speaker_samples()
