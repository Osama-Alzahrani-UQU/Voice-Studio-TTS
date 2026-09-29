r"""
mcp_server.py - Model Context Protocol (MCP) Server for Voice Studio
-------------------------------------------------------------------
Adapted from debpalash/VoiceStudio (backend/mcp_server.py).
Exposes neural speech synthesis, voice design, cloning, and DSP mastering
as standardized tools for AI agents (Claude Code, Cursor, Antigravity, Codex).

Usage:
  python mcp_server.py          # stdio transport (default)
  python mcp_server.py --port 3900  # SSE / HTTP transport
"""

from __future__ import annotations

import argparse
import base64
import os
import sys
from typing import Dict, Any, Optional, List

# Ensure LocalTTS_App directory is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from mcp.server.fastmcp import FastMCP
from unified_tts_manager import UnifiedTTSManager
from audio_dsp import apply_effects_preset, EFFECT_PRESETS

# Initialize FastMCP Server
mcp = FastMCP(
    "VoiceStudio",
    dependencies=["torch", "transformers", "soundfile"],
)

_manager: Optional[UnifiedTTSManager] = None


def get_manager() -> UnifiedTTSManager:
    global _manager
    if _manager is None:
        _manager = UnifiedTTSManager()
    return _manager


@mcp.tool()
def synthesize_speech(
    text: str,
    engine: str = "xtts",
    language: str = "en",
    speaker_or_instruct: str = "Damien_Black",
    speed: float = 1.0,
    dsp_preset: str = "broadcast",
    omnivoice_mode: str = "design",
    ref_audio_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Synthesize high-fidelity speech from text using XTTS v2 or OmniVoice.

    Args:
        text: The text to be converted to speech.
        engine: 'xtts' (XTTS v2 studio voices) or 'omnivoice' (600+ languages & diffusion).
        language: Language code ('en', 'ar', 'fr', 'es', etc.).
        speaker_or_instruct: Speaker voice name for XTTS, or voice design instruction for OmniVoice.
        speed: Speech rate multiplier (0.5 to 2.0).
        dsp_preset: Audio mastering preset ('broadcast', 'podcast', 'warm', 'bright', 'raw').
        omnivoice_mode: 'design' (prompt-driven), 'clone' (reference-driven), or 'auto'.
        ref_audio_path: Optional path to reference WAV for voice cloning.

    Returns:
        JSON with audio file path, sample rate, duration, and engine info.
    """
    mgr = get_manager()
    mgr.set_engine(engine)

    result = mgr.generate_speech(
        text=text,
        language=language,
        speaker_or_instruct=speaker_or_instruct,
        speed=speed,
        omnivoice_mode=omnivoice_mode,
        omnivoice_ref_audio=ref_audio_path,
        dsp_preset=dsp_preset,
    )

    return {
        "status": "success",
        "audio_path": result.get("output_path", ""),
        "engine": mgr.get_active_engine_name(),
        "device": mgr.get_active_device_label(),
        "sample_rate": result.get("sample_rate", 24000),
        "duration_seconds": result.get("duration", 0.0),
        "dsp_preset_applied": dsp_preset,
    }


@mcp.tool()
def list_voices(engine: str = "xtts") -> Dict[str, Any]:
    """
    Enumerate available voice profiles, speakers, and design presets.

    Args:
        engine: 'xtts' or 'omnivoice'.
    """
    mgr = get_manager()
    if "omni" in engine.lower():
        omni = mgr.omnivoice_engine
        return {
            "engine": "omnivoice",
            "genders": omni.GENDER_OPTIONS["en"],
            "age_brackets": omni.AGE_OPTIONS["en"],
            "pitch_levels": omni.PITCH_OPTIONS["en"],
            "styles": omni.STYLE_OPTIONS["en"],
            "accents": omni.ACCENT_OPTIONS["en"],
            "popular_languages": [item[0] for item in omni.POPULAR_LANGUAGES],
        }
    else:
        xtts = mgr.xtts_engine
        return {
            "engine": "xtts",
            "male_speakers": [s.get("raw", s.get("id", "")) for s in xtts.SPEAKER_CATALOG["male"]],
            "female_speakers": [s.get("raw", s.get("id", "")) for s in xtts.SPEAKER_CATALOG["female"]],
        }


@mcp.tool()
def list_dsp_presets() -> List[Dict[str, str]]:
    """
    List available broadcast DSP mastering presets.
    """
    return [
        {
            "id": k,
            "label": v["label"],
            "icon": v["icon"],
            "description": v["description"],
        }
        for k, v in EFFECT_PRESETS.items()
    ]


@mcp.tool()
def check_system_status() -> Dict[str, Any]:
    """
    Check hardware acceleration, memory status, and speech engines readiness.
    """
    mgr = get_manager()
    return {
        "status": "online",
        "active_engine": mgr.get_active_engine_name(),
        "device": mgr.get_active_device_label(),
        "is_active_engine_ready": mgr.is_active_engine_ready(),
        "available_engines": mgr.get_available_engines(),
    }


def main():
    parser = argparse.ArgumentParser(description="Voice Studio MCP Server")
    parser.add_argument("--sse", action="store_true", help="Run with SSE transport")
    parser.add_argument("--port", type=int, default=3900, help="Port for SSE transport")
    args = parser.parse_args()

    if args.sse:
        mcp.settings.port = args.port
        mcp.run(transport="sse")
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
