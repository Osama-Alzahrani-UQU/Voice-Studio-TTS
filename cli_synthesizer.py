r"""
cli_synthesizer.py - Command-Line Batch Speech Synthesizer
---------------------------------------------------------
Allows terminal, script, and headless automated batch speech synthesis
using Coqui XTTS v2 or k2-fsa OmniVoice with broadcast DSP mastering.

Examples:
  python cli_synthesizer.py --text "Welcome to Voice Studio" --engine xtts --output out.wav
  python cli_synthesizer.py --text "مرحباً بكم في استوديو الصوت" --lang ar --dsp broadcast
  python cli_synthesizer.py --file book_chapter.txt --engine omnivoice --output chapter1.wav
"""

from __future__ import annotations

import argparse
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from unified_tts_manager import UnifiedTTSManager


def main():
    parser = argparse.ArgumentParser(description="Voice Studio CLI Speech Synthesizer")
    parser.add_argument("--text", type=str, help="Text to synthesize")
    parser.add_argument("--file", type=str, help="Path to text file to synthesize")
    parser.add_argument("--engine", choices=["xtts", "omnivoice"], default="xtts", help="Engine to use")
    parser.add_argument("--lang", default="en", help="Language code ('en', 'ar', etc.)")
    parser.add_argument("--speaker", default="Damien_Black", help="Speaker voice or design instruction")
    parser.add_argument("--speed", type=float, default=1.0, help="Speech speed multiplier")
    parser.add_argument("--dsp", default="broadcast", help="DSP preset: broadcast, podcast, warm, bright, raw")
    parser.add_argument("--output", type=str, default=None, help="Target output WAV path")
    parser.add_argument("--ref-audio", type=str, default=None, help="Reference audio for voice cloning")
    args = parser.parse_args()

    content = args.text
    if args.file:
        if not os.path.exists(args.file):
            print(f"[CLI Error] File not found: {args.file}")
            sys.exit(1)
        with open(args.file, "r", encoding="utf-8") as f:
            content = f.read()

    if not content or not content.strip():
        print("[CLI Error] No input text provided. Use --text or --file.")
        sys.exit(1)

    print(f"[Voice Studio CLI] Initializing speech engine: {args.engine.upper()}...")
    mgr = UnifiedTTSManager()
    mgr.set_engine(args.engine)
    mgr.get_active_engine().initialize()

    print(f"[Voice Studio CLI] Synthesizing ({len(content)} characters, lang: {args.lang}, dsp: {args.dsp})...")
    res = mgr.generate_speech(
        text=content,
        language=args.lang,
        speaker_or_instruct=args.speaker,
        speed=args.speed,
        omnivoice_mode="clone" if args.ref_audio else "design",
        omnivoice_ref_audio=args.ref_audio,
        dsp_preset=args.dsp,
    )

    out_file = res.get("output_path")
    if args.output and out_file and os.path.exists(out_file):
        import shutil
        shutil.copy2(out_file, args.output)
        out_file = args.output

    print(f"[Voice Studio CLI] Success! Audio generated at: {out_file}")
    print(f"  Duration: {res.get('duration', 0.0):.2f}s | Sample Rate: {res.get('sample_rate', 24000)}Hz")


if __name__ == "__main__":
    main()
