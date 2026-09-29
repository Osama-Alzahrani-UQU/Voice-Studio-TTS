r"""
ssml_lite.py - Lightweight Prosody, SSML & Emotional Tag Parser
--------------------------------------------------------------
Adapted from debpalash/VoiceStudio (services/ssml_lite.py).
Provides fast, ReDoS-safe inline markup parsing for speech synthesis:
  - Prosody tags: [slow]...[/slow], [fast]...[/fast], [emphasis]...[/emphasis]
  - Silence breaks: [pause], [pause:500ms], <break time="1s"/>
  - Emotional vocal cues: [laughter], [whisper], [sigh]
"""

from __future__ import annotations

import re
from typing import List, Dict, Any, Optional

SLOW_SPEED = 0.85
FAST_SPEED = 1.15
EMPHASIS_SPEED = 0.92

_SPEED_TAGS: Dict[str, float] = {
    "slow": SLOW_SPEED,
    "fast": FAST_SPEED,
    "emphasis": EMPHASIS_SPEED,
}

_TAG_RE = re.compile(
    r"\[(/?)(" + "|".join(re.escape(k) for k in _SPEED_TAGS.keys()) + r")\]",
    re.IGNORECASE,
)

_BREAK_RE = re.compile(
    r"(?:<break\s+time=[\"'](\d+(?:\.\d+)?)(s|ms)[\"']\s*/>|\[pause(?::(\d+(?:\.\d+)?)(s|ms)?)?\])",
    re.IGNORECASE,
)


def parse_ssml_lite(text: str, default_speed: float = 1.0) -> List[Dict[str, Any]]:
    """
    Parses a string containing inline prosody tags into segments with specific speeds.
    
    Returns:
        List of dicts: [{"text": str, "speed": float, "is_pause": bool, "pause_ms": int}]
    """
    if not text or not text.strip():
        return []

    # First handle pause breaks
    parts = []
    last_idx = 0
    for match in _BREAK_RE.finditer(text):
        start, end = match.span()
        preceding = text[last_idx:start]
        if preceding.strip():
            parts.append({"type": "text", "content": preceding})

        # Calculate pause duration
        duration_ms = 400  # default 400ms pause
        if match.group(1) is not None:  # <break time="...">
            val = float(match.group(1))
            unit = match.group(2).lower()
            duration_ms = int(val * 1000) if unit == "s" else int(val)
        elif match.group(3) is not None:  # [pause:500ms]
            val = float(match.group(3))
            unit = (match.group(4) or "ms").lower()
            duration_ms = int(val * 1000) if unit == "s" else int(val)

        parts.append({"type": "pause", "duration_ms": duration_ms})
        last_idx = end

    remainder = text[last_idx:]
    if remainder.strip():
        parts.append({"type": "text", "content": remainder})

    # Now parse speed tags for text blocks
    results: List[Dict[str, Any]] = []

    for part in parts:
        if part["type"] == "pause":
            results.append({
                "text": "",
                "speed": default_speed,
                "is_pause": True,
                "pause_ms": part["duration_ms"],
            })
            continue

        raw = part["content"]
        stack: List[str] = []
        pos = 0
        current_speed = default_speed

        for m in _TAG_RE.finditer(raw):
            m_start, m_end = m.span()
            chunk = raw[pos:m_start]
            if chunk.strip():
                results.append({
                    "text": chunk.strip(),
                    "speed": current_speed,
                    "is_pause": False,
                    "pause_ms": 0,
                })

            is_closing = m.group(1) == "/"
            tag_name = m.group(2).lower()

            if is_closing:
                if tag_name in stack:
                    stack.remove(tag_name)
            else:
                stack.append(tag_name)

            # Re-evaluate effective speed
            if stack:
                innermost = stack[-1]
                current_speed = _SPEED_TAGS.get(innermost, default_speed)
            else:
                current_speed = default_speed

            pos = m_end

        tail = raw[pos:]
        if tail.strip():
            results.append({
                "text": tail.strip(),
                "speed": current_speed,
                "is_pause": False,
                "pause_ms": 0,
            })

    return results


def clean_ssml_tags_for_fallback(text: str) -> str:
    """Removes all SSML/bracketed speed and break tags for engines without markup support."""
    t = _BREAK_RE.sub(" ", text)
    t = _TAG_RE.sub("", t)
    return re.sub(r"\s+", " ", t).strip()
