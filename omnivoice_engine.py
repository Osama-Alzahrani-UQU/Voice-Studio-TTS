r"""
omnivoice_engine.py - k2-fsa OmniVoice Diffusion Speech Engine Manager
----------------------------------------------------------------------
Manages OmniVoice model loading, multi-lingual zero-shot TTS across 600+ languages,
Voice Design attribute synthesis, reference-based Voice Cloning, and audio export.
"""

import os
import sys
import time
import uuid
import threading
import torch
import numpy as np
import soundfile as sf
from typing import Dict, List, Optional, Callable, Any

from text_splitter import split_text_into_chunks
from arabic_text_processor import normalize_arabic_text
from xtts_engine import (
    BASE_APP_DIR,
    TEMP_AUDIO_DIR,
    EXPORTS_DIR,
    HF_MODELS_DIR,
    TORCH_CACHE_DIR,
)

try:
    import transformers
    import transformers.utils.versions as _tuv
    _tuv.require_version = lambda *args, **kwargs: None
    _tuv.require_version_core = lambda *args, **kwargs: None
except Exception:
    pass

SAVED_PROMPTS_DIR = os.path.join(BASE_APP_DIR, "saved_prompts")
os.makedirs(SAVED_PROMPTS_DIR, exist_ok=True)


class OmniVoiceEngineManager:
    """
    Massively multilingual zero-shot speech synthesis engine supporting 600+ languages,
    diffusion-based high-speed generation, Voice Design, and Voice Cloning.
    """

    MODEL_ID = "k2-fsa/OmniVoice"

    VOICE_DESIGN_DEFAULTS = {
        "gender": "female",
        "age": "young adult",
        "pitch": "moderate pitch",
        "style": "normal",
        "accent": "auto",
    }

    # Bilingual labels for Voice Design attributes
    GENDER_OPTIONS = {
        "en": ["Female", "Male"],
        "ar": ["أنثى", "ذكر"],
    }
    GENDER_MAP = {
        "female": "female",
        "male": "male",
        "أنثى": "female",
        "ذكر": "male",
        "Female": "female",
        "Male": "male",
    }

    AGE_OPTIONS = {
        "en": ["Young Adult", "Child", "Teenager", "Middle-aged", "Elderly"],
        "ar": ["شاب / شابة", "طفل / طفلة", "مراهق / مراهقة", "متوسط العمر", "مسن / مسنة"],
    }
    AGE_MAP = {
        "young adult": "young adult",
        "child": "child",
        "teenager": "teenager",
        "middle-aged": "middle-aged",
        "elderly": "elderly",
        "شاب / شابة": "young adult",
        "طفل / طفلة": "child",
        "مراهق / مراهقة": "teenager",
        "متوسط العمر": "middle-aged",
        "مسن / مسنة": "elderly",
        "Young Adult": "young adult",
        "Child": "child",
        "Teenager": "teenager",
        "Middle-aged": "middle-aged",
        "Elderly": "elderly",
    }

    PITCH_OPTIONS = {
        "en": ["Moderate Pitch", "Low Pitch", "Very Low Pitch", "High Pitch", "Very High Pitch"],
        "ar": ["معتدل", "منخفض", "منخفض جداً", "مرتفع", "مرتفع جداً"],
    }
    PITCH_MAP = {
        "moderate pitch": "moderate pitch",
        "low pitch": "low pitch",
        "very low pitch": "very low pitch",
        "high pitch": "high pitch",
        "very high pitch": "very high pitch",
        "معتدل": "moderate pitch",
        "منخفض": "low pitch",
        "منخفض جداً": "very low pitch",
        "مرتفع": "high pitch",
        "مرتفع جداً": "very high pitch",
        "Moderate Pitch": "moderate pitch",
        "Low Pitch": "low pitch",
        "Very Low Pitch": "very low pitch",
        "High Pitch": "high pitch",
        "Very High Pitch": "very high pitch",
    }

    STYLE_OPTIONS = {
        "en": ["Normal", "Whisper"],
        "ar": ["طبيعي", "همس"],
    }
    STYLE_MAP = {
        "normal": "normal",
        "whisper": "whisper",
        "طبيعي": "normal",
        "همس": "whisper",
        "Normal": "normal",
        "Whisper": "whisper",
    }

    ACCENT_OPTIONS = {
        "en": [
            "Auto / Standard",
            "American Accent",
            "British Accent",
            "Australian Accent",
            "Canadian Accent",
            "Indian Accent",
            "Korean Accent",
            "Russian Accent",
            "Japanese Accent",
            "Chinese Accent",
        ],
        "ar": [
            "تلقائي / قياسي",
            "لهجة أمريكية",
            "لهجة بريطانية",
            "لهجة أسترالية",
            "لهجة كندية",
            "لهجة هندية",
            "لهجة كورية",
            "لهجة روسية",
            "لهجة يابانية",
            "لهجة صينية",
        ],
    }
    ACCENT_MAP = {
        "auto / standard": "auto",
        "american accent": "american accent",
        "british accent": "british accent",
        "australian accent": "australian accent",
        "canadian accent": "canadian accent",
        "indian accent": "indian accent",
        "korean accent": "korean accent",
        "russian accent": "russian accent",
        "japanese accent": "japanese accent",
        "chinese accent": "chinese accent",
        "تلقائي / قياسي": "auto",
        "لهجة أمريكية": "american accent",
        "لهجة بريطانية": "british accent",
        "لهجة أسترالية": "australian accent",
        "لهجة كندية": "canadian accent",
        "لهجة هندية": "indian accent",
        "لهجة كورية": "korean accent",
        "لهجة روسية": "russian accent",
        "لهجة يابانية": "japanese accent",
        "لهجة صينية": "chinese accent",
        "Auto / Standard": "auto",
        "American Accent": "american accent",
        "British Accent": "british accent",
        "Australian Accent": "australian accent",
        "Canadian Accent": "canadian accent",
        "Indian Accent": "indian accent",
        "Korean Accent": "korean accent",
        "Russian Accent": "russian accent",
        "Japanese Accent": "japanese accent",
        "Chinese Accent": "chinese accent",
    }

    # Top popular languages for quick access, plus access to all 600+
    POPULAR_LANGUAGES = [
        ("العربية (Arabic)", "ar"),
        ("English", "en"),
        ("Español (Spanish)", "es"),
        ("Français (French)", "fr"),
        ("Deutsch (German)", "de"),
        ("Italiano (Italian)", "it"),
        ("Türkçe (Turkish)", "tr"),
        ("Русский (Russian)", "ru"),
        ("中文 (Chinese)", "zh"),
        ("日本語 (Japanese)", "ja"),
        ("한국어 (Korean)", "ko"),
        ("Português (Portuguese)", "pt"),
        ("हिन्दी (Hindi)", "hi"),
        ("اردو (Urdu)", "ur"),
        ("فارسی (Persian)", "fa"),
        ("Bahasa Indonesia", "id"),
    ]

    def __init__(self, temp_dir: str = TEMP_AUDIO_DIR):
        self.temp_dir = os.path.abspath(temp_dir)
        os.makedirs(self.temp_dir, exist_ok=True)
        self.model = None
        self.is_ready = False
        self.loading_error = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device_label = "GPU (CUDA)" if self.device == "cuda" else "CPU"
        self.dtype = torch.float16 if self.device == "cuda" else torch.float32
        self._init_lock = threading.Lock()

    def initialize(self):
        """Initializes the OmniVoice diffusion model safely across threads."""
        with self._init_lock:
            if self.is_ready and self.model is not None:
                return True

            try:
                print(f"[OmniVoice Engine] Loading '{self.MODEL_ID}' on {self.device_label} ({self.dtype})...")
                from omnivoice import OmniVoice

                self.model = OmniVoice.from_pretrained(
                    self.MODEL_ID,
                    device_map=self.device,
                    dtype=self.dtype,
                )
                self.is_ready = True
                print("[OmniVoice Engine] OmniVoice ready.")
                return True
            except Exception as e:
                self.loading_error = str(e)
                self.is_ready = False
                print(f"[OmniVoice Engine] ERROR loading model: {e}")
                raise e

    @classmethod
    def resolve_instruct(
        cls,
        gender: str = "female",
        age: str = "young adult",
        pitch: str = "moderate pitch",
        style: str = "normal",
        accent: str = "auto",
    ) -> str:
        """Constructs a validated comma-separated instruct string for Voice Design."""
        canonical_gender = cls.GENDER_MAP.get(gender, "female")
        canonical_age = cls.AGE_MAP.get(age, "young adult")
        canonical_pitch = cls.PITCH_MAP.get(pitch, "moderate pitch")
        canonical_style = cls.STYLE_MAP.get(style, "normal")
        canonical_accent = cls.ACCENT_MAP.get(accent, "auto")

        parts = [canonical_gender, canonical_age]
        if canonical_pitch and canonical_pitch != "moderate pitch":
            parts.append(canonical_pitch)
        if canonical_style == "whisper":
            parts.append("whisper")
        if canonical_accent and canonical_accent != "auto":
            parts.append(canonical_accent)

        return ", ".join(parts)

    @classmethod
    def resolve_language_code(cls, lang_input: str) -> str:
        """Resolves language code from display name or code."""
        if not lang_input:
            return "en"
        val = lang_input.strip().lower()
        if "arab" in val or "عرب" in val or val == "ar":
            return "ar"
        if "eng" in val or val == "en":
            return "en"

        try:
            from omnivoice.utils.lang_map import LANG_NAME_TO_ID, LANG_IDS
            if val in LANG_IDS:
                return val
            if val in LANG_NAME_TO_ID:
                return LANG_NAME_TO_ID[val]
            for name, code in LANG_NAME_TO_ID.items():
                if name.lower() in val or val in name.lower():
                    return code
        except Exception:
            pass

        return "en"

    def generate_speech(
        self,
        text: str,
        language: str = "en",
        mode: str = "design",  # 'design', 'clone', or 'auto'
        instruct: Optional[str] = None,
        ref_audio: Optional[str] = None,
        ref_text: Optional[str] = None,
        voice_prompt_path: Optional[str] = None,
        speed: float = 1.0,
        num_step: int = 32,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ) -> Dict[str, Any]:
        """
        Synthesizes long-form speech using OmniVoice. Splits text into manageable
        sentences, generates audio per chunk, and concatenates with smooth silence padding.
        """
        if not self.is_ready or self.model is None:
            self.initialize()

        if not text or not text.strip():
            raise ValueError("Text input cannot be empty.")

        lang_code = self.resolve_language_code(language)

        if lang_code == "ar":
            text_clean = normalize_arabic_text(text)
        else:
            text_clean = text.strip()

        from omnivoice import OmniVoiceGenerationConfig

        gen_config = OmniVoiceGenerationConfig(
            num_step=int(num_step or 32),
            guidance_scale=2.0,
            denoise=True,
            preprocess_prompt=True,
            postprocess_output=True,
        )

        chunks = split_text_into_chunks(text_clean, max_chars=180)
        total_chunks = len(chunks)
        print(f"[OmniVoice Engine] Synthesizing ({total_chunks} chunks, mode={mode}, lang={lang_code}): \"{text_clean[:30]}...\"")

        voice_clone_prompt = None
        if mode == "clone":
            if voice_prompt_path and os.path.exists(voice_prompt_path):
                from omnivoice import VoiceClonePrompt
                voice_clone_prompt = VoiceClonePrompt.load(voice_prompt_path)
            elif ref_audio and os.path.exists(ref_audio):
                voice_clone_prompt = self.model.create_voice_clone_prompt(
                    ref_audio=ref_audio,
                    ref_text=ref_text or None,
                )

        chunk_audio_arrays = []
        sample_rate = getattr(self.model, "sampling_rate", 24000)
        silence_padding = np.zeros(int(sample_rate * 0.15), dtype=np.float32)

        for idx, chunk in enumerate(chunks, start=1):
            if progress_callback:
                progress_callback(idx, total_chunks, chunk)

            kw: Dict[str, Any] = {
                "text": chunk,
                "language": lang_code,
                "generation_config": gen_config,
            }

            if speed is not None and float(speed) != 1.0:
                kw["speed"] = float(speed)

            if mode == "clone" and voice_clone_prompt is not None:
                kw["voice_clone_prompt"] = voice_clone_prompt
            elif mode == "design" and instruct:
                kw["instruct"] = instruct

            audio_result = self.model.generate(**kw)
            chunk_waveform = audio_result[0]

            if isinstance(chunk_waveform, torch.Tensor):
                chunk_waveform = chunk_waveform.detach().cpu().numpy()
            chunk_waveform = np.asarray(chunk_waveform, dtype=np.float32)

            chunk_audio_arrays.append(chunk_waveform)
            if idx < total_chunks:
                chunk_audio_arrays.append(silence_padding)

        if not chunk_audio_arrays:
            raise RuntimeError("OmniVoice failed to generate any audio chunks.")

        full_audio = np.concatenate(chunk_audio_arrays)
        duration = float(len(full_audio) / sample_rate)

        filename = f"omnivoice_{uuid.uuid4().hex[:8]}_{int(time.time())}.wav"
        output_path = os.path.join(self.temp_dir, filename)
        sf.write(output_path, full_audio, sample_rate)

        speaker_label = instruct if mode == "design" else ("Cloned Voice" if mode == "clone" else "Auto Voice")

        return {
            "filepath": output_path,
            "duration": duration,
            "text": text_clean,
            "speaker": speaker_label,
            "language": lang_code,
            "engine": "omnivoice",
        }

    def save_voice_clone_prompt(
        self,
        ref_audio: str,
        name: str,
        ref_text: Optional[str] = None,
    ) -> str:
        """Encodes reference audio and saves a reusable VoiceClonePrompt (.pt) file."""
        if not self.is_ready or self.model is None:
            self.initialize()

        clean_name = "".join(c for c in name if c.isalnum() or c in ("_", "-")).strip() or "custom_voice"
        target_path = os.path.join(SAVED_PROMPTS_DIR, f"{clean_name}.pt")

        prompt = self.model.create_voice_clone_prompt(
            ref_audio=ref_audio,
            ref_text=ref_text or None,
        )
        prompt.save(target_path)
        print(f"[OmniVoice Engine] Saved cloned voice prompt to: {target_path}")
        return target_path

    @classmethod
    def list_saved_prompts(cls) -> List[Dict[str, str]]:
        """Returns list of saved voice clone prompts (.pt) in SAVED_PROMPTS_DIR."""
        if not os.path.exists(SAVED_PROMPTS_DIR):
            return []
        items = []
        for fname in os.listdir(SAVED_PROMPTS_DIR):
            if fname.endswith(".pt"):
                base_name = os.path.splitext(fname)[0]
                items.append({
                    "id": base_name,
                    "name": base_name.replace("_", " ").title(),
                    "path": os.path.join(SAVED_PROMPTS_DIR, fname),
                })
        return items
