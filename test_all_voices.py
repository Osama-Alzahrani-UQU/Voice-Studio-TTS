r"""
test_all_voices.py - Automated Test Loop for Every Dropdown Voice
-------------------------------------------------------------------
Tests 1-sentence speech synthesis for EVERY voice in the dropdown menu.
Fails hard (exit code 1) if any voice throws an error or fails to find reference audio.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xtts_engine import XTTSEngineManager

def test_all_voices():
    print("==================================================")
    print("   AUTOMATED TEST STEP: Testing All Dropdown Voices ")
    print("==================================================")

    mgr = XTTSEngineManager()
    mgr.initialize()

    voices = mgr.BUILTIN_SPEAKERS
    print(f"Total dropdown voices to test: {len(voices)}")

    failed_voices = []
    passed_voices = []

    test_text_ar = "مرحباً بكم، هذا اختبار الصوت."
    test_text_en = "Hello, this is a voice test."

    for i, voice in enumerate(voices, 1):
        print(f"\n[{i}/{len(voices)}] Testing voice: '{voice}'...")
        try:
            # Test Arabic synthesis
            res_ar = mgr.generate_long_speech(
                text=test_text_ar,
                language="ar",
                speaker=voice
            )
            
            # Test English synthesis
            res_en = mgr.generate_long_speech(
                text=test_text_en,
                language="en",
                speaker=voice
            )

            if os.path.exists(res_ar["filepath"]) and os.path.exists(res_en["filepath"]):
                print(f"  -> PASSED '{voice}' (AR: {res_ar['duration']:.2f}s, EN: {res_en['duration']:.2f}s)")
                passed_voices.append(voice)
            else:
                print(f"  -> FAILED '{voice}': Output file missing")
                failed_voices.append((voice, "Output file missing"))

        except Exception as e:
            print(f"  -> FAILED '{voice}': {e}")
            failed_voices.append((voice, str(e)))

    print("\n==================================================")
    print(f"   RESULTS: {len(passed_voices)} PASSED, {len(failed_voices)} FAILED")
    print("==================================================")

    if failed_voices:
        print("\nERRORS ENCOUNTERED:")
        for v, err in failed_voices:
            print(f" - Voice '{v}': {err}")
        print("\nTEST SUITE FAILED! DO NOT PROCEED TO BUILD.")
        sys.exit(1)
    else:
        print("\nALL VOICES PASSED FUNCTIONAL TEST! PROCEED TO BUILD.")
        sys.exit(0)

if __name__ == "__main__":
    test_all_voices()
