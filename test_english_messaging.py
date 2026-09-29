r"""
test_english_messaging.py - Test English Message Generation & Language Handling
-------------------------------------------------------------------------------
Verifies that English messages like 'the admin has joined' synthesize smoothly
with male and female voices without thread conflicts or errors.
"""

import sys
import os
import soundfile as sf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xtts_engine import XTTSEngineManager

def test_english():
    print("==================================================")
    print("  Testing English Text Speech Generation           ")
    print("==================================================")

    mgr = XTTSEngineManager()
    mgr.initialize()

    test_messages = [
        "the admin has joined",
        "Welcome to the local text to speech chat system.",
        "This is an English test sentence with 100% offline generation."
    ]

    voices = [
        list(XTTSEngineManager.MALE_SPEAKERS.keys())[0],
        list(XTTSEngineManager.FEMALE_SPEAKERS.keys())[0]
    ]

    passed = []
    failed = []

    for voice in voices:
        print(f"\n--- Testing Voice: '{voice}' ---")
        for idx, text in enumerate(test_messages, 1):
            print(f"Message [{idx}]: '{text}'")
            try:
                res = mgr.generate_long_speech(
                    text=text,
                    language="en",
                    speaker=voice
                )
                audio_path = res["filepath"]
                duration = res["duration"]

                if not os.path.exists(audio_path):
                    raise RuntimeError("Audio file missing.")

                data, sr = sf.read(audio_path)
                if len(data) == 0:
                    raise RuntimeError("Empty audio output.")

                print(f"  -> PASSED: Duration={duration:.2f}s, SR={sr}Hz, File={os.path.basename(audio_path)}")
                passed.append(f"{voice}-{idx}")
            except Exception as e:
                print(f"  -> FAILED: {e}")
                failed.append((f"{voice}-{idx}", str(e)))

    print("\n==================================================")
    print(f" RESULTS: {len(passed)} PASSED, {len(failed)} FAILED")
    print("==================================================")

    if failed:
        print("ENGLISH MESSAGING TEST FAILED!")
        sys.exit(1)
    else:
        print("ALL ENGLISH MESSAGES SYNTHESIZED SUCCESSFULLY!")
        sys.exit(0)

if __name__ == "__main__":
    test_english()
