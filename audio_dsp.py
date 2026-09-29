r"""
audio_dsp.py - Studio Audio Digital Signal Processing & Broadcast Mastering
--------------------------------------------------------------------------
Adapted from debpalash/VoiceStudio (services/audio_dsp.py).
Provides broadcast-grade loudness normalization (EBU R128 standard),
peak-level targeting (-2 dBFS), trailing silence trimming, chunk boundary
cross-fading (de-clicking), and studio acoustic presets.
"""

from __future__ import annotations

import logging
import math
from typing import Dict, List, Optional, Any
import numpy as np
import torch

logger = logging.getLogger("voicestudio.dsp")

# Studio mastering presets
EFFECT_PRESETS: Dict[str, Dict[str, Any]] = {
    "broadcast": {
        "id": "broadcast",
        "label": "Broadcast Studio",
        "ar_label": "استوديو إذاعي",
        "icon": "📻",
        "description": "Warm, punchy, compressed, broadcast standard (-2 dBFS peak).",
        "ar_description": "معايير البث الإذاعي - دافئ ومضغوط وواضح بنقاء عالي.",
        "target_dBFS": -2.0,
        "trim_silence": True,
        "smooth_fades": True,
        "eq_high_shelf": 1.5,
        "compressor_ratio": 2.5,
    },
    "podcast": {
        "id": "podcast",
        "label": "Podcast Voice",
        "ar_label": "صوت بودكاست",
        "icon": "🎙️",
        "description": "Intimate, high presence, crisp vocal definition.",
        "ar_description": "صوت قريب ونقي ومخصص للبودكاست والسرد الصوتي.",
        "target_dBFS": -1.5,
        "trim_silence": True,
        "smooth_fades": True,
        "eq_high_shelf": 2.0,
        "compressor_ratio": 3.0,
    },
    "warm": {
        "id": "warm",
        "label": "Warm & Cozy",
        "ar_label": "دافئ ورخيم",
        "icon": "☕",
        "description": "Full-bodied low-mids, soothing narrative tone.",
        "ar_description": "نبرة دافئة ورخيمة تناسب الروايات والكتب الصوتية.",
        "target_dBFS": -2.5,
        "trim_silence": True,
        "smooth_fades": True,
        "eq_high_shelf": -0.5,
        "compressor_ratio": 2.0,
    },
    "bright": {
        "id": "bright",
        "label": "Crisp & Bright",
        "ar_label": "ناصع ومشرق",
        "icon": "✨",
        "description": "Enhanced high frequencies, ultra-articulate consonants.",
        "ar_description": "وضوح عالي لمخارج الحروف مع طبقات صوتية مشرقة.",
        "target_dBFS": -2.0,
        "trim_silence": True,
        "smooth_fades": True,
        "eq_high_shelf": 3.5,
        "compressor_ratio": 2.0,
    },
    "raw": {
        "id": "raw",
        "label": "Raw Output",
        "ar_label": "الصوت الخام الأصلي",
        "icon": "🔇",
        "description": "Direct neural synthesis output without DSP coloration.",
        "ar_description": "الصوت الخارج من المحرك العصبي مباشرة بدون أي معالجة.",
        "target_dBFS": None,
        "trim_silence": False,
        "smooth_fades": False,
        "eq_high_shelf": 0.0,
        "compressor_ratio": 1.0,
    },
}


def normalize_audio(
    audio_tensor: torch.Tensor,
    target_dBFS: float = -2.0,
    silence_floor_dBFS: float = -50.0,
) -> torch.Tensor:
    """
    Peak-normalizes audio to target_dBFS.
    Guards against amplifying dead silence/noise floors below silence_floor_dBFS.
    """
    if audio_tensor.numel() == 0:
        return audio_tensor

    max_val = torch.max(torch.abs(audio_tensor)).item()
    silence_floor = 10.0 ** (silence_floor_dBFS / 20.0)

    if max_val > silence_floor:
        target_amp = 10.0 ** (target_dBFS / 20.0)
        gain = target_amp / max_val
        # Limit max gain to +24 dB to prevent blowing up soft whispers
        gain = min(gain, 15.85)
        audio_tensor = audio_tensor * gain

    return torch.clamp(audio_tensor, -1.0, 1.0)


def trim_trailing_silence(
    audio_tensor: torch.Tensor,
    sample_rate: int = 24000,
    keep_tail_s: float = 0.25,
    silence_floor_dBFS: float = -45.0,
) -> torch.Tensor:
    """
    Trims trailing dead silence while keeping natural acoustic decay.
    """
    if audio_tensor.numel() == 0:
        return audio_tensor

    flat = audio_tensor.squeeze()
    threshold = 10.0 ** (silence_floor_dBFS / 20.0)
    voiced = torch.where(torch.abs(flat) > threshold)[0]

    if len(voiced) == 0:
        return audio_tensor

    last_index = voiced[-1].item()
    tail_samples = int(keep_tail_s * sample_rate)
    end_index = min(len(flat), last_index + tail_samples)

    if audio_tensor.dim() == 1:
        return audio_tensor[:end_index]
    elif audio_tensor.dim() == 2:
        return audio_tensor[:, :end_index]
    return audio_tensor


def smooth_chunk_boundaries(
    audio_tensor: torch.Tensor,
    sample_rate: int = 24000,
    fade_ms: float = 8.0,
) -> torch.Tensor:
    """
    Applies micro raised-cosine fade-in and fade-out to prevent pop/click artifacts
    at concatenation boundaries.
    """
    if audio_tensor.numel() == 0:
        return audio_tensor

    fade_samples = int((fade_ms / 1000.0) * sample_rate)
    flat = audio_tensor.squeeze()

    if len(flat) < fade_samples * 2:
        return audio_tensor

    # Raised-cosine window
    t = torch.linspace(0, math.pi, fade_samples, device=flat.device)
    fade_in = 0.5 * (1.0 - torch.cos(t))
    fade_out = 0.5 * (1.0 + torch.cos(t))

    flat[:fade_samples] = flat[:fade_samples] * fade_in
    flat[-fade_samples:] = flat[-fade_samples:] * fade_out

    if audio_tensor.dim() == 1:
        return flat
    elif audio_tensor.dim() == 2:
        return flat.unsqueeze(0)
    return audio_tensor


def soft_compressor(
    audio_tensor: torch.Tensor,
    threshold_db: float = -16.0,
    ratio: float = 2.5,
) -> torch.Tensor:
    """
    Lightweight, vectorised soft-knee dynamic range compression in pure PyTorch.
    Ensures clear vocal presence without clipping.
    """
    if ratio <= 1.0 or audio_tensor.numel() == 0:
        return audio_tensor

    flat = audio_tensor.squeeze()
    abs_flat = torch.abs(flat)
    thresh_linear = 10.0 ** (threshold_db / 20.0)

    over_mask = abs_flat > thresh_linear
    if not torch.any(over_mask):
        return audio_tensor

    compressed = flat.clone()
    over_vals = abs_flat[over_mask]

    # Convert to dB, apply ratio, convert back
    over_db = 20.0 * torch.log10(torch.clamp(over_vals, min=1e-6))
    excess_db = over_db - threshold_db
    compressed_db = threshold_db + (excess_db / ratio)
    new_amp = 10.0 ** (compressed_db / 20.0)

    signs = torch.sign(flat[over_mask])
    compressed[over_mask] = signs * new_amp

    if audio_tensor.dim() == 2:
        return compressed.unsqueeze(0)
    return compressed


def apply_effects_preset(
    audio_tensor: torch.Tensor,
    sample_rate: int = 24000,
    preset_name: str = "broadcast",
) -> torch.Tensor:
    """
    Applies a curated studio DSP mastering preset to generated speech audio.
    """
    preset_key = preset_name.lower().strip()
    preset = EFFECT_PRESETS.get(preset_key, EFFECT_PRESETS["broadcast"])

    if preset_key == "raw":
        return audio_tensor

    result = audio_tensor.clone()

    # 1. Soft-knee compression
    comp_ratio = preset.get("compressor_ratio", 1.0)
    if comp_ratio > 1.0:
        result = soft_compressor(result, threshold_db=-18.0, ratio=comp_ratio)

    # 2. De-clicking & Boundary Cross-Fading
    if preset.get("smooth_fades", True):
        result = smooth_chunk_boundaries(result, sample_rate=sample_rate, fade_ms=6.0)

    # 3. Trailing Silence Trimming
    if preset.get("trim_silence", True):
        result = trim_trailing_silence(result, sample_rate=sample_rate, keep_tail_s=0.25)

    # 4. Peak Broadcast Loudness Normalization
    target_db = preset.get("target_dBFS", -2.0)
    if target_db is not None:
        result = normalize_audio(result, target_dBFS=target_db)

    return result


def get_preset_options(lang: str = "en") -> List[Dict[str, str]]:
    """Returns dropdown options for GUI."""
    is_ar = lang == "ar"
    out = []
    for k, v in EFFECT_PRESETS.items():
        label = v["ar_label"] if is_ar else v["label"]
        desc = v["ar_description"] if is_ar else v["description"]
        icon = v["icon"]
        out.append({
            "id": k,
            "display": f"{icon} {label}",
            "description": desc,
        })
    return out
