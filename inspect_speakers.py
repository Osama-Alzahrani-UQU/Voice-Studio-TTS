import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from xtts_engine import XTTSEngineManager

def inspect():
    mgr = XTTSEngineManager()
    mgr.initialize()

    sm = mgr.tts.synthesizer.tts_model.speaker_manager
    speakers = list(sm.speakers.keys()) if sm and hasattr(sm, "speakers") else []
    print(f"Total speakers in XTTS v2 model: {len(speakers)}")
    print("Sample speaker names from model:", speakers[:15])

    print("\n--- Checking Dropdown Speakers against Model ---")
    for spk in mgr.BUILTIN_SPEAKERS:
        match = [s for s in speakers if s.lower() == spk.lower()]
        if match:
            print(f"[EXACT/CASE MATCH] '{spk}' -> '{match[0]}'")
        else:
            print(f"[NOT FOUND] '{spk}'")

if __name__ == "__main__":
    inspect()
