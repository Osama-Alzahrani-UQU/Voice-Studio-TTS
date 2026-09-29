r"""
test_categorized_voices.py - Pre-Build Verification for Male and Female Voices
-------------------------------------------------------------------------------
Tests synthesis for 3 Male voices and 3 Female voices in Arabic and English.
Validates that categorized reference audio files and model fallbacks work cleanly.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xtts_engine import XTTSEngineManager

def test_categorized_voices():
    print("==================================================")
    print("   AUTOMATED PRE-BUILD TEST: Categorized Voices   ")
    print("==================================================")

    mgr = XTTSEngineManager()
    mgr.initialize()

    # Select 3 Male and 3 Female voices to test
    male_test_voices = list(XTTSEngineManager.MALE_SPEAKERS.keys())[:3]
    female_test_voices = list(XTTSEngineManager.FEMALE_SPEAKERS.keys())[:3]

    print(f"Testing Male Voices: {male_test_voices}")
    print(f"Testing Female Voices: {female_test_voices}")

    test_text_ar = "اختبار الصوت المستقل للرجال والنساء."
    test_text_en = "Testing independent voice synthesis for male and female categories."

    failed = []
    passed = []

    # 1. Test Male Voices
    print("\n--- Testing Male Voices ---")
    for voice in male_test_voices:
        print(f"Testing Male Voice: '{voice}'...")
        try:
            res_ar = mgr.generate_long_speech(text=test_text_ar, language="ar", speaker=voice)
            res_en = mgr.generate_long_speech(text=test_text_en, language="en", speaker=voice)
            if os.path.exists(res_ar["filepath"]) and os.path.exists(res_en["filepath"]):
                print(f"  -> PASSED '{voice}' (AR: {res_ar['duration']:.2f}s, EN: {res_en['duration']:.2f}s)")
                passed.append(voice)
            else:
                print(f"  -> FAILED '{voice}': Output audio file missing")
                failed.append((voice, "Output file missing"))
        except Exception as e:
            print(f"  -> FAILED '{voice}': {e}")
            failed.append((voice, str(e)))

    # 2. Test Female Voices
    print("\n--- Testing Female Voices ---")
    for voice in female_test_voices:
        print(f"Testing Female Voice: '{voice}'...")
        try:
            res_ar = mgr.generate_long_speech(text=test_text_ar, language="ar", speaker=voice)
            res_en = mgr.generate_long_speech(text=test_text_en, language="en", speaker=voice)
            if os.path.exists(res_ar["filepath"]) and os.path.exists(res_en["filepath"]):
                print(f"  -> PASSED '{voice}' (AR: {res_ar['duration']:.2f}s, EN: {res_en['duration']:.2f}s)")
                passed.append(voice)
            else:
                print(f"  -> FAILED '{voice}': Output audio file missing")
                failed.append((voice, "Output file missing"))
        except Exception as e:
            print(f"  -> FAILED '{voice}': {e}")
            failed.append((voice, str(e)))

    print("\n==================================================")
    print(f" RESULTS: {len(passed)} PASSED, {len(failed)} FAILED")
    print("==================================================")

    if failed:
        print("\nCATEGORIZED VOICE TEST FAILED! DO NOT BUILD.")
        sys.exit(1)
    else:
        print("\nALL CATEGORIZED VOICES PASSED! PROCEEDING TO BUILD.")
        sys.exit(0)

if __name__ == "__main__":
    test_categorized_voices()
