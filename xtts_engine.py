r"""
xtts_engine.py - Coqui XTTS v2 Engine Manager
---------------------------------------------
Handles multilingual speech synthesis, long-form text chunking, real-time
progress updates, and seamless audio concatenation.
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

if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w", encoding="utf-8")

# Explicit static imports to guarantee PyInstaller bundles all speech/audio dependencies
try:
    import mutagen
    import pydub
    import pysbd
    import librosa
    import scipy
    import numba
    import einops
    import torchaudio
    import trainer
    import pandas
    import gruut
    import g2pkk
    import bangla
    import bnnumerizer
    import bnunicodenormalizer
    import hangul_romanize
    import jamo
    import jieba
    import pypinyin
    import anyascii
    import coqpit
    import encodec
    import inflect
    import nltk
    import unidecode
    import audioread
    import soxr
    import lazy_loader
except ImportError:
    pass

from text_splitter import split_text_into_chunks
from arabic_text_processor import normalize_arabic_text


def resolve_base_app_dir() -> str:
    """
    Dynamically resolves the application root directory for both source execution
    and standalone PyInstaller (.exe) distribution.
    """
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(os.path.abspath(sys.executable))
        if os.path.exists(os.path.join(exe_dir, "tts_models")):
            return exe_dir
        parent_root = os.path.abspath(os.path.join(exe_dir, "..", ".."))
        if os.path.exists(os.path.join(parent_root, "tts_models")):
            return parent_root
        return exe_dir
    return os.path.dirname(os.path.abspath(__file__))


BASE_APP_DIR = resolve_base_app_dir()
TTS_MODELS_DIR = os.path.join(BASE_APP_DIR, "tts_models")
HF_MODELS_DIR = os.path.join(BASE_APP_DIR, "hf_models")
TORCH_CACHE_DIR = os.path.join(BASE_APP_DIR, "torch_cache")
TEMP_AUDIO_DIR = os.path.join(BASE_APP_DIR, "temp_audio")
EXPORTS_DIR = os.path.join(BASE_APP_DIR, "exports")

if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    _bundled_speakers = os.path.join(sys._MEIPASS, "speakers")
    SPEAKERS_DIR = _bundled_speakers if os.path.exists(_bundled_speakers) else os.path.join(BASE_APP_DIR, "speakers")
else:
    SPEAKERS_DIR = os.path.join(BASE_APP_DIR, "speakers")

MALE_DIR = os.path.join(SPEAKERS_DIR, "male")
FEMALE_DIR = os.path.join(SPEAKERS_DIR, "female")
CUSTOM_DIR = os.path.join(SPEAKERS_DIR, "custom")

for _folder in (TTS_MODELS_DIR, HF_MODELS_DIR, TORCH_CACHE_DIR, TEMP_AUDIO_DIR, EXPORTS_DIR, SPEAKERS_DIR, MALE_DIR, FEMALE_DIR, CUSTOM_DIR):
    os.makedirs(_folder, exist_ok=True)

os.environ["TTS_HOME"] = TTS_MODELS_DIR
os.environ["COQUI_MODEL_PATH"] = TTS_MODELS_DIR
os.environ["HF_HOME"] = HF_MODELS_DIR
os.environ["HUGGINGFACE_HUB_CACHE"] = HF_MODELS_DIR
os.environ["TORCH_HOME"] = TORCH_CACHE_DIR
os.environ["COQUI_TOS_AGREED"] = "1"

# Monkey-patch torch.load to set weights_only=False for PyTorch 2.6+ compatibility with Coqui checkpoints
_original_torch_load = torch.load


def _safe_torch_load(*args, **kwargs):
    kwargs["weights_only"] = False
    return _original_torch_load(*args, **kwargs)


torch.load = _safe_torch_load

# Monkey-patch torchaudio.load to use soundfile
try:
    import torchaudio
    _original_torchaudio_load = torchaudio.load

    def _soundfile_torchaudio_load(filepath, *args, **kwargs):
        try:
            data, sr = sf.read(filepath, dtype="float32")
            if data.ndim == 1:
                tensor = torch.from_numpy(data).unsqueeze(0)
            else:
                tensor = torch.from_numpy(data.T)
            return tensor, sr
        except Exception:
            return _original_torchaudio_load(filepath, *args, **kwargs)

    torchaudio.load = _soundfile_torchaudio_load
except Exception:
    pass

# Transformers 5.x backward-compatibility shim for Coqui XTTS streaming generator
try:
    import transformers
    import transformers.utils
    if not hasattr(transformers.utils, "is_numba_available"):
        transformers.utils.is_numba_available = lambda: False
    import transformers.generation.utils as _gu
    import transformers.utils.versions as _tuv
    _tuv.require_version = lambda *args, **kwargs: None
    _tuv.require_version_core = lambda *args, **kwargs: None

    class _DummyScorer:
        def __init__(self, *args, **kwargs):
            pass

    for _cls_name in (
        "BeamSearchScorer",
        "ConstrainedBeamSearchScorer",
        "DisjunctiveConstraint",
        "PhrasalConstraint",
    ):
        for _dict_attr in ("_objects", "_extra_objects"):
            if hasattr(transformers, _dict_attr) and isinstance(getattr(transformers, _dict_attr), dict):
                getattr(transformers, _dict_attr)[_cls_name] = _DummyScorer
        try:
            setattr(transformers, _cls_name, _DummyScorer)
        except Exception:
            pass

    if not hasattr(_gu, "SampleOutput"):
        setattr(_gu, "SampleOutput", getattr(_gu, "GenerateOutput", _DummyScorer))
except Exception:
    pass


def _get_coqui_tts_class():
    """Safely resolves the Coqui TTS API class and ensures GenerationMixin inheritance on Transformers 5.x."""
    try:
        import TTS.api
        try:
            from transformers import GenerationMixin
            from TTS.tts.layers.xtts.gpt_inference import GPT2InferenceModel
            if GenerationMixin not in GPT2InferenceModel.__mro__:
                GPT2InferenceModel.__bases__ = GPT2InferenceModel.__bases__ + (GenerationMixin,)
        except Exception:
            pass
        if hasattr(TTS.api, "TTS"):
            return TTS.api.TTS
    except Exception as err:
        print(f"[XTTS Engine] Direct import warning: {err}, falling back to importlib...")

    import importlib
    tts_api_module = importlib.import_module("TTS.api")
    return getattr(tts_api_module, "TTS")


class XTTSEngineManager:
    """
    Coqui XTTS v2 long-form speech synthesis engine with Arabic & English support.
    """

    LANGUAGES = {
        "العربية": "ar",
        "English": "en",
        "العربية 🇸🇦": "ar",
        "English 🇬🇧": "en",
        "Arabic 🇸🇦": "ar",
    }

    LANGUAGE_MENU_ITEMS = [
        "العربية",
        "English",
    ]

    GENDERS = {
        "أصوات رجالية": "male",
        "أصوات نسائية": "female",
        "Male Voices": "male",
        "Female Voices": "female",
        "👨 الرجال / Male Voices": "male",
        "👩 النساء / Female Voices": "female",
        "👨 أصوات رجالية": "male",
        "👩 أصوات نسائية": "female",
        "👨 Male Voices": "male",
        "👩 Female Voices": "female",
    }

    CATEGORY_LABELS_BY_LANG = {
        "ar": {
            "all": "🌐 كافة الأصوات",
            "custom": "⭐ أصوات مخصصة",
            "male": "👨 أصوات رجالية",
            "female": "👩 أصوات نسائية",
        },
        "en": {
            "all": "🌐 All Voices",
            "custom": "⭐ Custom Voices",
            "male": "👨 Male Voices",
            "female": "👩 Female Voices",
        },
    }

    GENDER_LABELS_BY_LANG = {
        "ar": {
            "male": "أصوات رجالية",
            "female": "أصوات نسائية",
            "custom": "أصوات مخصصة",
            "all": "كافة الأصوات",
        },
        "en": {
            "male": "Male Voices",
            "female": "Female Voices",
            "custom": "Custom Voices",
            "all": "All Voices",
        },
    }

    SPEAKER_CATALOG = {
        "male": [
            {
                "id": "Damien_Black",
                "raw": "Damien Black",
                "ar": "Damien Black — رخيم",
                "en": "Damien Black — Deep",
                "bilingual": "Damien Black — Deep",
                "gender": "male",
            },
            {
                "id": "Abrahan_Mack",
                "raw": "Abrahan Mack",
                "ar": "Abrahan Mack — حيوي",
                "en": "Abrahan Mack — Energetic",
                "bilingual": "Abrahan Mack — Energetic",
                "gender": "male",
            },
            {
                "id": "Andrew_Kasch",
                "raw": "Andrew Kasch",
                "ar": "Andrew Kasch — راوي",
                "en": "Andrew Kasch — Narrator",
                "bilingual": "Andrew Kasch — Narrator",
                "gender": "male",
            },
            {
                "id": "Baldur_Otto",
                "raw": "Baldur Otto",
                "ar": "Baldur Otto — جهوري",
                "en": "Baldur Otto — Resonant",
                "bilingual": "Baldur Otto — Resonant",
                "gender": "male",
            },
            {
                "id": "Adalberto_Santos",
                "raw": "Adalberto Santos",
                "ar": "Adalberto Santos — واضح",
                "en": "Adalberto Santos — Clear",
                "bilingual": "Adalberto Santos — Clear",
                "gender": "male",
            },
            {
                "id": "Gideon_Keel",
                "raw": "Gideon Keel",
                "ar": "Gideon Keel — دافئ",
                "en": "Gideon Keel — Warm",
                "bilingual": "Gideon Keel — Warm",
                "gender": "male",
            },
        ],
        "female": [
            {
                "id": "Ana_Florence",
                "raw": "Ana Florence",
                "ar": "Ana Florence — احترافي",
                "en": "Ana Florence — Professional",
                "bilingual": "Ana Florence — Professional",
                "gender": "female",
            },
            {
                "id": "Claribel_Dervux",
                "raw": "Claribel Dervux",
                "ar": "Claribel Dervux — دافئ",
                "en": "Claribel Dervux — Warm",
                "bilingual": "Claribel Dervux — Warm",
                "gender": "female",
            },
            {
                "id": "Daisy_Soft",
                "raw": "Daisy Soft",
                "ar": "Daisy Soft — هادئ",
                "en": "Daisy Soft — Soft",
                "bilingual": "Daisy Soft — Soft",
                "gender": "female",
            },
            {
                "id": "Gracie_MacArthur",
                "raw": "Gracie MacArthur",
                "ar": "Gracie MacArthur — معبر",
                "en": "Gracie MacArthur — Expressive",
                "bilingual": "Gracie MacArthur — Expressive",
                "gender": "female",
            },
            {
                "id": "Sofia_Medina",
                "raw": "Sofia Medina",
                "ar": "Sofia Medina — مشرق",
                "en": "Sofia Medina — Bright",
                "bilingual": "Sofia Medina — Bright",
                "gender": "female",
            },
            {
                "id": "Tammie_Smith",
                "raw": "Tammie Smith",
                "ar": "Tammie Smith — طبيعي",
                "en": "Tammie Smith — Natural",
                "bilingual": "Tammie Smith — Natural",
                "gender": "female",
            },
            {
                "id": "Alison_Vervaecke",
                "raw": "Alison Vervaecke",
                "ar": "Alison Vervaecke — راوية",
                "en": "Alison Vervaecke — Narrator",
                "bilingual": "Alison Vervaecke — Narrator",
                "gender": "female",
            },
            {
                "id": "Brenda_Stenaker",
                "raw": "Brenda Stenaker",
                "ar": "Brenda Stenaker — سلس",
                "en": "Brenda Stenaker — Smooth",
                "bilingual": "Brenda Stenaker — Smooth",
                "gender": "female",
            },
        ],
        "custom": [],
    }

    MODEL_NAME = "tts_models/multilingual/multi-dataset/xtts_v2"

    def __init__(self, temp_dir: str = TEMP_AUDIO_DIR):
        self.temp_dir = os.path.abspath(temp_dir)
        os.makedirs(self.temp_dir, exist_ok=True)
        self.tts = None
        self.is_ready = False
        self.loading_error = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device_label = "GPU" if self.device == "cuda" else "CPU"
        self._init_lock = threading.Lock()
        self.refresh_custom_speakers()

    @classmethod
    def refresh_custom_speakers(cls) -> List[Dict[str, Any]]:
        """Scans custom directory and metadata to dynamically register user-recorded voices."""
        import json
        custom_items = []
        meta_file = os.path.join(SPEAKERS_DIR, "voices_metadata.json")
        meta = {}
        if os.path.exists(meta_file):
            try:
                with open(meta_file, "r", encoding="utf-8") as f:
                    meta = json.load(f)
            except Exception:
                meta = {}

        if os.path.exists(CUSTOM_DIR):
            for fname in os.listdir(CUSTOM_DIR):
                if fname.lower().endswith(".wav"):
                    cid = os.path.splitext(fname)[0]
                    vmeta = meta.get(cid, {})
                    display_name = vmeta.get("name", cid.replace("_", " "))
                    gender = vmeta.get("gender", "male")
                    item = {
                        "id": cid,
                        "raw": display_name,
                        "ar": f"⭐ {display_name} — صوت مخصص",
                        "en": f"⭐ {display_name} — Custom Voice",
                        "bilingual": f"⭐ {display_name} — Custom Voice",
                        "gender": gender,
                        "is_custom": True,
                        "wav_path": os.path.join(CUSTOM_DIR, fname),
                    }
                    custom_items.append(item)

        cls.SPEAKER_CATALOG["custom"] = custom_items
        return custom_items

    @classmethod
    def get_category_options(cls, lang_code: str = "ar") -> List[str]:
        lang = "en" if lang_code == "en" else "ar"
        mapping = cls.CATEGORY_LABELS_BY_LANG[lang]
        return [mapping["all"], mapping["custom"], mapping["male"], mapping["female"]]

    @classmethod
    def resolve_category_key(cls, category_label: str) -> str:
        if not category_label:
            return "all"
        l = category_label.lower()
        if "custom" in l or "مخصص" in l:
            return "custom"
        if "female" in l or "نسائ" in l:
            return "female"
        if "male" in l or "رجال" in l:
            return "male"
        return "all"

    @classmethod
    def get_gender_options(cls, lang_code: str = "ar") -> List[str]:
        lang = "en" if lang_code == "en" else "ar"
        mapping = cls.GENDER_LABELS_BY_LANG[lang]
        return [mapping["all"], mapping["custom"], mapping["male"], mapping["female"]]

    @classmethod
    def resolve_gender_key(cls, gender_label: str) -> str:
        return cls.resolve_category_key(gender_label)

    @classmethod
    def get_gender_display_label(cls, gender_key: str, lang_code: str = "ar") -> str:
        lang = "en" if lang_code == "en" else "ar"
        key = gender_key if gender_key in cls.CATEGORY_LABELS_BY_LANG[lang] else "all"
        return cls.CATEGORY_LABELS_BY_LANG[lang][key]

    @classmethod
    def get_speaker_options(cls, category_key: str = "all", lang_code: str = "ar") -> List[str]:
        cls.refresh_custom_speakers()
        lang = "en" if lang_code == "en" else "ar"
        cat = cls.resolve_category_key(category_key)
        if cat == "all":
            all_items = cls.SPEAKER_CATALOG["custom"] + cls.SPEAKER_CATALOG["male"] + cls.SPEAKER_CATALOG["female"]
            return [item[lang] for item in all_items]
        return [item[lang] for item in cls.SPEAKER_CATALOG.get(cat, [])]

    @classmethod
    def get_all_installed_voices(cls) -> List[Dict[str, Any]]:
        cls.refresh_custom_speakers()
        voices = []
        for cat in ("custom", "male", "female"):
            for item in cls.SPEAKER_CATALOG.get(cat, []):
                voices.append({
                    "id": item["id"],
                    "name": item["raw"],
                    "category": cat,
                    "gender": item.get("gender", cat),
                    "is_custom": item.get("is_custom", False),
                    "display_ar": item["ar"],
                    "display_en": item["en"],
                    "wav_path": item.get("wav_path") or os.path.join(SPEAKERS_DIR, f"{item['id']}.wav"),
                })
        return voices

    @classmethod
    def delete_custom_voice(cls, voice_id: str) -> bool:
        """Deletes custom voice audio and metadata."""
        clean_id = cls.resolve_speaker_id(voice_id)
        deleted = False
        for p in (
            os.path.join(CUSTOM_DIR, f"{clean_id}.wav"),
            os.path.join(MALE_DIR, f"{clean_id}.wav"),
            os.path.join(FEMALE_DIR, f"{clean_id}.wav"),
            os.path.join(SPEAKERS_DIR, f"{clean_id}.wav"),
            os.path.join(SAVED_PROMPTS_DIR, f"{clean_id}.pt"),
        ):
            if os.path.exists(p):
                try:
                    os.remove(p)
                    deleted = True
                except Exception:
                    pass

        meta_file = os.path.join(SPEAKERS_DIR, "voices_metadata.json")
        if os.path.exists(meta_file):
            import json
            try:
                with open(meta_file, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                if clean_id in meta:
                    del meta[clean_id]
                    with open(meta_file, "w", encoding="utf-8") as f:
                        json.dump(meta, f, ensure_ascii=False, indent=2)
            except Exception:
                pass

        cls.refresh_custom_speakers()
        return deleted

    @classmethod
    def _extract_raw_speaker_name(cls, speaker_display: str) -> str:
        if not speaker_display:
            return "Damien Black"
        text = speaker_display
        if text.startswith("⭐"):
            text = text[1:].strip()
        for sep in ("—", "(", "-"):
            if sep in text:
                text = text.split(sep)[0]
        return text.strip()

    @classmethod
    def resolve_speaker_id(cls, speaker_display: str) -> str:
        if not speaker_display:
            return "Damien_Black"
        cls.refresh_custom_speakers()
        raw_name = cls._extract_raw_speaker_name(speaker_display)
        clean_name = raw_name.replace(" ", "_")
        for group in cls.SPEAKER_CATALOG.values():
            for item in group:
                if item["id"].lower() == clean_name.lower() or item["raw"].lower() == raw_name.lower():
                    return item["id"]
        return clean_name

    @classmethod
    def get_speaker_display_name(cls, speaker_identifier: str, lang_code: str = "ar") -> str:
        cls.refresh_custom_speakers()
        lang = "en" if lang_code == "en" else "ar"
        speaker_id = cls.resolve_speaker_id(speaker_identifier)
        for group in cls.SPEAKER_CATALOG.values():
            for item in group:
                if item["id"].lower() == speaker_id.lower():
                    return item[lang]
        return speaker_identifier

    def initialize(self):
        """Loads the Coqui XTTS v2 model safely across threads."""
        with self._init_lock:
            if self.is_ready and self.tts is not None:
                return True

            try:
                CoquiTTS = _get_coqui_tts_class()
                print(f"[XTTS Engine] Initializing '{self.MODEL_NAME}' on {self.device_label}...")
                self.tts = CoquiTTS(model_name=self.MODEL_NAME, progress_bar=False).to(self.device)
                self.is_ready = True
                print("[XTTS Engine] Engine ready.")
                return True
            except Exception as e:
                self.loading_error = str(e)
                self.is_ready = False
                print(f"[XTTS Engine] ERROR initializing model: {e}")
                raise e

    def generate_speech(
        self,
        text: str,
        language: str = "ar",
        speaker: str = "Ana Florence",
        speed: float = 1.0,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ) -> Dict[str, Any]:
        """Alias to generate_long_speech."""
        return self.generate_long_speech(
            text=text,
            language=language,
            speaker=speaker,
            speed=speed,
            progress_callback=progress_callback,
        )

    def generate_long_speech(
        self,
        text: str,
        language: str = "ar",
        speaker: str = "Ana Florence",
        speed: float = 1.0,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ) -> Dict[str, Any]:
        """
        Processes multi-paragraph text by splitting into sentence chunks, synthesizing
        chunks sequentially, and concatenating audio into a unified WAV file.
        """
        if not self.is_ready or self.tts is None:
            self.initialize()

        if not text or not text.strip():
            raise ValueError("Text input cannot be empty.")

        if language == "ar":
            text_clean = normalize_arabic_text(text)
        else:
            text_clean = text.strip()

        chunks = split_text_into_chunks(text_clean, max_chars=180)
        total_chunks = len(chunks)
        print(f"[XTTS Engine] Synthesizing ({total_chunks} chunks, lang={language}): \"{text_clean[:30]}...\"")

        chunk_audio_arrays = []
        sample_rate = 24000
        silence_padding = np.zeros(int(sample_rate * 0.15), dtype=np.float32)

        speaker_kwargs = {}
        raw_name = self._extract_raw_speaker_name(speaker)
        clean_name = self.resolve_speaker_id(speaker)

        candidates = [
            os.path.join(CUSTOM_DIR, f"{clean_name}.wav"),
            os.path.join(CUSTOM_DIR, f"{raw_name}.wav"),
            os.path.join(MALE_DIR, f"{clean_name}.wav"),
            os.path.join(FEMALE_DIR, f"{clean_name}.wav"),
            os.path.join(SPEAKERS_DIR, f"{clean_name}.wav"),
            os.path.join(SPEAKERS_DIR, f"{raw_name}.wav"),
        ]

        found_wav = None
        for cand in candidates:
            if os.path.exists(cand):
                found_wav = cand
                break

        if found_wav:
            speaker_kwargs["speaker_wav"] = found_wav
        else:
            model_speakers = []
            if (
                hasattr(self.tts, "synthesizer")
                and self.tts.synthesizer
                and hasattr(self.tts.synthesizer, "tts_model")
                and self.tts.synthesizer.tts_model
                and hasattr(self.tts.synthesizer.tts_model, "speaker_manager")
                and self.tts.synthesizer.tts_model.speaker_manager
            ):
                model_speakers = list(self.tts.synthesizer.tts_model.speaker_manager.speakers.keys())

            matched = [s for s in model_speakers if s.lower() == raw_name.lower()]
            if matched:
                speaker_kwargs["speaker"] = matched[0]
            else:
                any_wavs = []
                for d in [MALE_DIR, FEMALE_DIR, SPEAKERS_DIR]:
                    if os.path.exists(d):
                        any_wavs.extend([os.path.join(d, f) for f in os.listdir(d) if f.endswith(".wav")])
                if any_wavs:
                    speaker_kwargs["speaker_wav"] = any_wavs[0]
                elif "Ana Florence" in model_speakers:
                    speaker_kwargs["speaker"] = "Ana Florence"
                else:
                    speaker_kwargs["speaker"] = model_speakers[0] if model_speakers else "Ana Florence"

        for idx, chunk in enumerate(chunks):
            if progress_callback:
                progress_callback(idx + 1, total_chunks, chunk)

            chunk_filename = f"temp_chunk_{idx}_{uuid.uuid4().hex[:4]}.wav"
            chunk_filepath = os.path.abspath(os.path.join(self.temp_dir, chunk_filename))

            try:
                self.tts.tts_to_file(
                    text=chunk,
                    language=language,
                    file_path=chunk_filepath,
                    **speaker_kwargs,
                )

                audio_data, sr = sf.read(chunk_filepath)
                sample_rate = sr
                chunk_audio_arrays.append(audio_data)
                chunk_audio_arrays.append(silence_padding)

            finally:
                if os.path.exists(chunk_filepath):
                    try:
                        os.remove(chunk_filepath)
                    except Exception:
                        pass

        if not chunk_audio_arrays:
            raise RuntimeError("Failed to generate audio for any text chunk.")

        final_audio = np.concatenate(chunk_audio_arrays, axis=0)
        duration = len(final_audio) / float(sample_rate)

        out_filename = f"voice_{language}_{int(time.time())}_{uuid.uuid4().hex[:6]}.wav"
        out_filepath = os.path.abspath(os.path.join(self.temp_dir, out_filename))

        sf.write(out_filepath, final_audio, sample_rate)
        print(f"[XTTS Engine] Saved audio: {out_filepath} ({duration:.2f}s)")

        return {
            "filepath": out_filepath,
            "filename": out_filename,
            "duration": duration,
            "chunk_count": total_chunks,
            "text": text_clean,
            "language": language,
            "speaker": speaker,
        }
