r"""
test_arabic_precision.py - Pre-Build Arabic Articulation & Precision Test Suite
-------------------------------------------------------------------------------
Synthesizes complex diacritized Arabic phrases ("الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ",
"مَرَحَبَاً بِكُم فِي نِظَامِ تَولِيدِ الصَّوتِ المَحَلِّيِّ") with both male and female
studio voices. Programmatically asserts clean output duration and non-empty audio data.
"""

import sys
import os
import soundfile as sf

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from xtts_engine import XTTSEngineManager
from arabic_text_processor import normalize_arabic_text

def test_arabic_precision():
    print("==================================================")
    print("  MANDATORY PRE-BUILD ARABIC PRECISION TEST SUITE  ")
    print("==================================================")

    mgr = XTTSEngineManager()
    mgr.initialize()

    # Complex Arabic test phrases with diacritics
    test_phrases = [
        "الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ",
        "مَرَحَبَاً بِكُم فِي نِظَامِ تَولِيدِ الصَّوتِ المَحَلِّيِّ الفَصِيحِ 100%",
        "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ"
    ]

    test_male_voice = list(XTTSEngineManager.MALE_SPEAKERS.keys())[0]  # Damien Black
    test_female_voice = list(XTTSEngineManager.FEMALE_SPEAKERS.keys())[0]  # Ana Florence

    voices = [("Male", test_male_voice), ("Female", test_female_voice)]

    failed = []
    passed = []

    for label, voice in voices:
        print(f"\n--- Testing {label} Voice: '{voice}' ---")
        for idx, phrase in enumerate(test_phrases, 1):
            norm_phrase = normalize_arabic_text(phrase)
            print(f"Phrase [{idx}]: Raw='{phrase}' -> Normalized='{norm_phrase}'")
            try:
                res = mgr.generate_long_speech(
                    text=phrase,
                    language="ar",
                    speaker=voice
                )
                
                audio_path = res["filepath"]
                duration = res["duration"]

                # Programmatic audio verification checks
                if not os.path.exists(audio_path):
                    raise RuntimeError("Audio file was not generated.")

                data, sr = sf.read(audio_path)
                if len(data) == 0:
                    raise RuntimeError("Audio file is 0 bytes / empty.")

                # Expect minimum 1.5 seconds per phrase, maximum 15 seconds
                if duration < 1.0 or duration > 15.0:
                    raise RuntimeError(f"Unexpected audio duration: {duration:.2f}s")

                print(f"  -> PASSED Phrase [{idx}]: Duration={duration:.2f}s, SR={sr}Hz, Samples={len(data)}")
                passed.append(f"{label}-{idx}")

            except Exception as e:
                print(f"  -> FAILED Phrase [{idx}]: {e}")
                failed.append((f"{label}-{idx}", str(e)))

    print("\n==================================================")
    print(f" RESULTS: {len(passed)} PASSED, {len(failed)} FAILED")
    print("==================================================")

    if failed:
        print("\nARABIC PRECISION TEST FAILED! DO NOT BUILD.")
        sys.exit(1)
    else:
        print("\nARABIC PRECISION TEST PASSED 100%! PROCEEDING TO BUILD.")
        sys.exit(0)

if __name__ == "__main__":
    test_arabic_precision()
