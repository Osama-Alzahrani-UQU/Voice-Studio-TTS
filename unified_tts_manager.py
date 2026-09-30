r"""
unified_tts_manager.py - Unified Speech Engine Facade
------------------------------------------------------
Provides a clean, unified facade managing both Coqui XTTS v2 and k2-fsa OmniVoice
engines with seamless switching, unified playback handling, and cross-engine status.
"""

import os
import sys
import threading
from typing import Dict, List, Optional, Callable, Any

from xtts_engine import XTTSEngineManager
from omnivoice_engine import OmniVoiceEngineManager


class UnifiedTTSManager:
    """
    Facade managing dual neural engines:
    - 'xtts': Coqui XTTS v2 (14 built-in studio voices, voice cloning)
    - 'omnivoice': k2-fsa OmniVoice (600+ languages, diffusion speed, Voice Design)
    """

    ENGINES = {
        "xtts": {
            "id": "xtts",
            "en": "XTTS v2 (Studio Voices)",
            "ar": "XTTS v2 (أصوات استوديو)",
        },
        "omnivoice": {
            "id": "omnivoice",
            "en": "OmniVoice (600+ Langs & Voice Design)",
            "ar": "OmniVoice (أكثر من 600 لغة وتصميم الأصوات)",
        },
    }

    def __init__(self):
        self.active_engine_name = "xtts"
        self.xtts_engine = XTTSEngineManager()
        self.omnivoice_engine = OmniVoiceEngineManager()
        self._lock = threading.Lock()

    def set_engine(self, engine_key: str):
        """Switches the active speech engine ('xtts' or 'omnivoice')."""
        with self._lock:
            key = "omnivoice" if "omni" in engine_key.lower() else "xtts"
            self.active_engine_name = key
            print(f"[Unified TTS] Active engine switched to: {self.active_engine_name.upper()}")

    def get_active_engine_name(self) -> str:
        return self.active_engine_name

    def get_available_engines(self) -> List[str]:
        """Returns list of configured engine identifiers."""
        return list(self.ENGINES.keys())

    def get_active_engine(self):
        if self.active_engine_name == "omnivoice":
            return self.omnivoice_engine
        return self.xtts_engine

    def is_active_engine_ready(self) -> bool:
        return self.get_active_engine().is_ready

    def get_all_installed_voices(self) -> List[Dict[str, Any]]:
        return self.xtts_engine.get_all_installed_voices()

    def delete_custom_voice(self, voice_id: str) -> bool:
        return self.xtts_engine.delete_custom_voice(voice_id)

    def get_active_device_label(self) -> str:
        return self.get_active_engine().device_label

    def initialize_active_engine_async(self, on_ready: Optional[Callable[[], None]] = None, on_error: Optional[Callable[[str], None]] = None):
        """Asynchronously pre-loads the currently active engine."""
        engine = self.get_active_engine()

        def task():
            try:
                engine.initialize()
                if on_ready:
                    on_ready()
            except Exception as e:
                if on_error:
                    on_error(str(e))

        t = threading.Thread(target=task, daemon=True)
        t.start()

    def generate_speech(
        self,
        text: str,
        language: str = "en",
        speaker_or_instruct: str = "Ana Florence",
        speed: float = 1.0,
        omnivoice_mode: str = "design",  # 'design', 'clone', or 'auto'
        omnivoice_ref_audio: Optional[str] = None,
        omnivoice_ref_text: Optional[str] = None,
        omnivoice_prompt_path: Optional[str] = None,
        omnivoice_num_step: int = 32,
        dsp_preset: str = "broadcast",
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ) -> Dict[str, Any]:
        """
        Unified dispatch: routes speech synthesis to active engine with broadcast DSP mastering.
        """
        if self.active_engine_name == "omnivoice":
            # If a speaker voice is passed and no custom ref audio given, resolve speaker reference WAV and prompt
            ref_audio = omnivoice_ref_audio
            ref_prompt = omnivoice_prompt_path
            mode = omnivoice_mode

            if not ref_audio and not ref_prompt and speaker_or_instruct:
                clean_id = self.xtts_engine.resolve_speaker_id(speaker_or_instruct)
                candidates = [
                    os.path.join(self.xtts_engine.temp_dir, "..", "speakers", "custom", f"{clean_id}.wav"),
                    os.path.join(self.xtts_engine.temp_dir, "..", "speakers", "male", f"{clean_id}.wav"),
                    os.path.join(self.xtts_engine.temp_dir, "..", "speakers", "female", f"{clean_id}.wav"),
                    os.path.join(self.xtts_engine.temp_dir, "..", "speakers", f"{clean_id}.wav"),
                ]
                for cand in candidates:
                    norm_cand = os.path.abspath(cand)
                    if os.path.exists(norm_cand):
                        ref_audio = norm_cand
                        mode = "clone"
                        break

                cand_pt = os.path.abspath(os.path.join(self.xtts_engine.temp_dir, "..", "saved_prompts", f"{clean_id}.pt"))
                if os.path.exists(cand_pt):
                    ref_prompt = cand_pt

            result = self.omnivoice_engine.generate_speech(
                text=text,
                language=language,
                mode=mode,
                instruct=speaker_or_instruct if mode == "design" else None,
                ref_audio=ref_audio,
                ref_text=omnivoice_ref_text,
                voice_prompt_path=ref_prompt,
                speed=speed,
                num_step=omnivoice_num_step,
                progress_callback=progress_callback,
            )
        else:
            result = self.xtts_engine.generate_long_speech(
                text=text,
                language=language,
                speaker=speaker_or_instruct,
                speed=speed,
                progress_callback=progress_callback,
            )

        # Apply Broadcast Audio DSP Mastering (debpalash/VoiceStudio pipeline)
        if dsp_preset and dsp_preset.lower() != "raw":
            wav_path = result.get("output_path") or result.get("filepath")
            if wav_path and os.path.exists(wav_path):
                try:
                    import soundfile as sf
                    import torch
                    from audio_dsp import apply_effects_preset
                    data, sr = sf.read(wav_path, dtype="float32")
                    tensor = torch.from_numpy(data)
                    mastered = apply_effects_preset(tensor, sample_rate=sr, preset_name=dsp_preset)
                    sf.write(wav_path, mastered.cpu().numpy(), sr)
                    result["dsp_preset"] = dsp_preset
                except Exception as dsp_err:
                    print(f"[Unified TTS] DSP Mastering warning: {dsp_err}")

        return result
