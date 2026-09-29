"""
main_window.py - Voice Studio Main Application Window
-----------------------------------------------------
CustomTkinter desktop GUI window featuring sleek studio aesthetics, dynamic
English (LTR) <-> Arabic (RTL) interface & menu localization, dual-engine
switching (Coqui XTTS v2 & k2-fsa OmniVoice Diffusion), Voice Design Studio,
Voice Cloning, and emotional quick chips.
"""

import os
import sys
import threading
import customtkinter as ctk
from tkinter import messagebox, filedialog

from xtts_engine import XTTSEngineManager, BASE_APP_DIR
from omnivoice_engine import OmniVoiceEngineManager
from unified_tts_manager import UnifiedTTSManager
from audio_player import AudioPlayerController
from gui.chat_bubble import UserChatBubble, AIChatBubble, LoadingChatBubble

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class XTTSArabicEnglishChatApp(ctk.CTk):
    """
    Main application window for dual-engine neural speech synthesis
    with full bidirectional English <-> Arabic menu and UI localization.
    """

    TRANSLATIONS = {
        "en": {
            "window_title": "Voice Studio — Neural Multilingual TTS",
            "studio_title": "Voice Studio",
            "engine_label": "Engine:",
            "lang_label": "Language:",
            "toggle_btn": "العربية ⇄",
            "gender_label": "Category:",
            "speaker_label": "Voice:",
            "clear_btn": "Clear",
            "welcome_title": "Neural Text-to-Speech Studio",
            "welcome_desc": "Select an engine (XTTS v2 or OmniVoice 600+ Langs), customize voice parameters or reference audio, and generate studio-quality speech.",
            "placeholder": "Enter your text here to synthesize speech (e.g. Hello world! [laughter])...",
            "send_btn": "Generate",
            "status_analyzing": "Processing text & preparing neural diffusion...",
            "status_chunk_fmt": "Synthesizing segment {idx} of {total} ({pct}%)...",
            "error_title": "Synthesis Error",
            "error_prefix": "Failed to generate audio:\n",
            "ready_suffix": "Ready",
            "mode_label": "Mode:",
            "mode_design": "Voice Design",
            "mode_clone": "Voice Cloning",
            "mode_auto": "Auto Voice",
            "age_label": "Age:",
            "pitch_label": "Pitch:",
            "style_label": "Style:",
            "accent_label": "Accent:",
            "browse_btn": "Browse Audio...",
            "save_prompt_btn": "Save Voice (.pt)",
            "no_ref_audio": "No reference audio selected",
            "select_ref_audio_dlg": "Select Reference Audio File (3-10s)",
            "cloned_saved_title": "Voice Profile Saved",
            "cloned_saved_msg": "Cloned voice prompt saved successfully to:\n",
        },
        "ar": {
            "window_title": "Voice Studio — استوديو الصوت والذكاء الاصطناعي",
            "studio_title": "استوديو الصوت",
            "engine_label": "المحرك:",
            "lang_label": "اللغة:",
            "toggle_btn": "English ⇄",
            "gender_label": "الفئة:",
            "speaker_label": "الصوت:",
            "clear_btn": "مسح",
            "welcome_title": "استوديو تحويل النص إلى كلام متعدد اللغات",
            "welcome_desc": "اختر المحرك (XTTS v2 أو OmniVoice لأكثر من 600 لغة)، وحدد خصائص الصوت أو مقطع الاستنساخ، ثم اكتب النص بالأسفل لتوليد الصوت.",
            "placeholder": "اكتب النص هنا لتحويله إلى مقطع صوتي (مثال: مرحباً بكم [laughter])...",
            "send_btn": "توليد الصوت",
            "status_analyzing": "جاري معالجة النص وبدء التوليد الصوتي...",
            "status_chunk_fmt": "جاري توليد المقطع {idx} من {total} ({pct}%)...",
            "error_title": "خطأ في التوليد",
            "error_prefix": "تعذر توليد المقطع الصوتي:\n",
            "ready_suffix": "جاهز",
            "mode_label": "النمط:",
            "mode_design": "تصميم صوت",
            "mode_clone": "استنساخ صوت",
            "mode_auto": "صوت تلقائي",
            "age_label": "العمر:",
            "pitch_label": "الطبقة:",
            "style_label": "الأسلوب:",
            "accent_label": "اللهجة:",
            "browse_btn": "استعراض صوت...",
            "save_prompt_btn": "حفظ البصمة (.pt)",
            "no_ref_audio": "لم يتم اختيار ملف صوتي مرجعي",
            "select_ref_audio_dlg": "اختر مقطعاً صوتياً مرجعياً (3-10 ثوانٍ)",
            "cloned_saved_title": "تم حفظ البصمة الصوتية",
            "cloned_saved_msg": "تم حفظ موجه الصوت المستنسخ بنجاح في:\n",
        },
    }

    ENGINE_DISPLAY_NAMES = {
        "en": {
            "xtts": "XTTS v2 (Studio Cloned)",
            "omnivoice": "OmniVoice (600+ Langs & Design)",
        },
        "ar": {
            "xtts": "XTTS v2 (أصوات استوديو)",
            "omnivoice": "OmniVoice (أكثر من 600 لغة وتصميم الأصوات)",
        },
    }

    def __init__(self):
        super().__init__()

        self.geometry("1120x800")
        self.minsize(920, 640)

        # Core dual-engine manager
        self.tts_manager = UnifiedTTSManager()

        # Default settings
        self.current_lang_code = "en"
        self.current_engine_key = "xtts"
        self.current_gender_key = "male"
        self.current_speaker_id = "Damien_Black"

        # OmniVoice specific variables
        self.current_omni_mode = "design"  # 'design', 'clone', 'auto'
        self.current_omni_gender = "female"
        self.current_omni_age = "young adult"
        self.current_omni_pitch = "moderate pitch"
        self.current_omni_style = "normal"
        self.current_omni_accent = "auto"
        self.selected_ref_audio_path = None

        # Interactive StringVars
        self.selected_engine_label = ctk.StringVar(
            value=self.ENGINE_DISPLAY_NAMES["en"]["xtts"]
        )
        self.selected_lang_label = ctk.StringVar(value="English")
        self.selected_gender = ctk.StringVar(
            value=XTTSEngineManager.get_gender_display_label("male", "en")
        )
        self.selected_speaker = ctk.StringVar(
            value=XTTSEngineManager.get_speaker_display_name("Damien_Black", "en")
        )

        # OmniVoice UI StringVars
        self.selected_omni_mode = ctk.StringVar(value="Voice Design")
        self.selected_omni_gender = ctk.StringVar(value="Female")
        self.selected_omni_age = ctk.StringVar(value="Young Adult")
        self.selected_omni_pitch = ctk.StringVar(value="Moderate Pitch")
        self.selected_omni_style = ctk.StringVar(value="Normal")
        self.selected_omni_accent = ctk.StringVar(value="Auto / Standard")
        self.ref_audio_status_text = ctk.StringVar(
            value=self.TRANSLATIONS["en"]["no_ref_audio"]
        )

        self.is_processing = False
        self.active_loading_bubble = None
        self.chat_bubbles = []

        # Build Main UI Components
        self._create_header_frame()
        self._create_sub_toolbar_frame()
        self._create_chat_frame()
        self._create_input_frame()

        # Apply initial language across all widgets
        self._apply_ui_language("en")

        # Start async model initialization for default engine
        self._initialize_active_engine_async()

    def _create_header_frame(self):
        """Top menu bar featuring engine selector, hardware status, and language switcher."""
        top_container = ctk.CTkFrame(self, fg_color="#181825", corner_radius=0)
        top_container.pack(side="top", fill="x", padx=0, pady=0)

        header = ctk.CTkFrame(top_container, fg_color="#1e1e2e", height=58, corner_radius=0)
        header.pack(side="top", fill="x", padx=0, pady=0)
        header.grid_columnconfigure(1, weight=1)

        # Studio Title Label
        self.title_label = ctk.CTkLabel(
            header,
            text="Voice Studio",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#cba6f7",
        )
        self.title_label.grid(row=0, column=0, padx=(18, 8), pady=12, sticky="w")

        # Engine & Hardware Status Badges
        badges_frame = ctk.CTkFrame(header, fg_color="transparent")
        badges_frame.grid(row=0, column=1, padx=4, pady=12, sticky="w")

        badge_color = "#a6e3a1" if self.tts_manager.get_active_engine().device == "cuda" else "#89b4fa"
        self.hardware_badge = ctk.CTkLabel(
            badges_frame,
            text=f"● {self.tts_manager.get_active_device_label()}",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=badge_color,
            fg_color="#313244",
            corner_radius=6,
            padx=10,
            pady=4,
        )
        self.hardware_badge.pack(side="left", padx=(0, 6))

        # Controls Container (Right Aligned Header Menu)
        controls_frame = ctk.CTkFrame(header, fg_color="transparent")
        controls_frame.grid(row=0, column=2, padx=16, pady=12, sticky="e")

        # Engine Dropdown Label
        self.engine_label = ctk.CTkLabel(
            controls_frame,
            text="Engine:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#cdd6f4",
        )
        self.engine_label.pack(side="left", padx=(0, 4))

        # Engine Dropdown (XTTS v2 vs OmniVoice)
        self.engine_dropdown = ctk.CTkOptionMenu(
            controls_frame,
            values=[
                self.ENGINE_DISPLAY_NAMES["en"]["xtts"],
                self.ENGINE_DISPLAY_NAMES["en"]["omnivoice"],
            ],
            variable=self.selected_engine_label,
            width=220,
            height=32,
            fg_color="#313244",
            button_color="#45475a",
            button_hover_color="#585b70",
            dropdown_fg_color="#1e1e2e",
            text_color="#cdd6f4",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self._on_engine_change,
        )
        self.engine_dropdown.pack(side="left", padx=(0, 10))

        # Language Dropdown Label
        self.lang_label = ctk.CTkLabel(
            controls_frame,
            text="Language:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#cdd6f4",
        )
        self.lang_label.pack(side="left", padx=(0, 4))

        # Language Dropdown Menu
        self.lang_dropdown = ctk.CTkOptionMenu(
            controls_frame,
            values=["English", "العربية"],
            variable=self.selected_lang_label,
            width=120,
            height=32,
            fg_color="#313244",
            button_color="#45475a",
            button_hover_color="#585b70",
            dropdown_fg_color="#1e1e2e",
            text_color="#cdd6f4",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._on_language_change,
        )
        self.lang_dropdown.pack(side="left", padx=(0, 6))

        # Quick One-Click Language Switch Button (English ⇄ العربية)
        self.lang_toggle_btn = ctk.CTkButton(
            controls_frame,
            text="العربية ⇄",
            width=96,
            height=32,
            corner_radius=8,
            fg_color="#cba6f7",
            text_color="#11111b",
            hover_color="#b4befe",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.toggle_language,
        )
        self.lang_toggle_btn.pack(side="left", padx=(0, 10))

        # Clear Button
        self.clear_btn = ctk.CTkButton(
            controls_frame,
            text="Clear",
            width=64,
            height=32,
            corner_radius=8,
            fg_color="#313244",
            text_color="#f38ba8",
            hover_color="#45475a",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self.clear_chat,
        )
        self.clear_btn.pack(side="left")

    def _create_sub_toolbar_frame(self):
        """Secondary toolbar dynamically showing XTTS voice controls or OmniVoice Voice Design studio."""
        self.sub_toolbar = ctk.CTkFrame(self, fg_color="#181825", height=48, corner_radius=0)
        self.sub_toolbar.pack(side="top", fill="x", padx=0, pady=0)

        # 1. XTTS Sub-toolbar Container
        self.xtts_controls = ctk.CTkFrame(self.sub_toolbar, fg_color="transparent")
        self.xtts_controls.pack(side="left", fill="both", expand=True, padx=16, pady=6)

        self.gender_label = ctk.CTkLabel(
            self.xtts_controls,
            text="Category:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#cdd6f4",
        )
        self.gender_label.pack(side="left", padx=(0, 4))

        self.gender_dropdown = ctk.CTkOptionMenu(
            self.xtts_controls,
            values=XTTSEngineManager.get_gender_options("en"),
            variable=self.selected_gender,
            width=130,
            height=30,
            fg_color="#313244",
            button_color="#45475a",
            button_hover_color="#585b70",
            dropdown_fg_color="#1e1e2e",
            text_color="#cdd6f4",
            font=ctk.CTkFont(size=11),
            command=self._on_gender_change,
        )
        self.gender_dropdown.pack(side="left", padx=(0, 10))

        self.speaker_label = ctk.CTkLabel(
            self.xtts_controls,
            text="Voice:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#cdd6f4",
        )
        self.speaker_label.pack(side="left", padx=(0, 4))

        self.speaker_dropdown = ctk.CTkOptionMenu(
            self.xtts_controls,
            values=XTTSEngineManager.get_speaker_options("male", "en"),
            variable=self.selected_speaker,
            width=200,
            height=30,
            fg_color="#313244",
            button_color="#45475a",
            button_hover_color="#585b70",
            dropdown_fg_color="#1e1e2e",
            text_color="#cdd6f4",
            font=ctk.CTkFont(size=11),
            command=self._on_speaker_change,
        )
        self.speaker_dropdown.pack(side="left", padx=(0, 8))

        # 2. OmniVoice Sub-toolbar Container (Voice Design & Cloning)
        self.omni_controls = ctk.CTkFrame(self.sub_toolbar, fg_color="transparent")

        # Mode label & dropdown
        self.omni_mode_label = ctk.CTkLabel(
            self.omni_controls,
            text="Mode:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#cdd6f4",
        )
        self.omni_mode_label.pack(side="left", padx=(0, 4))

        self.omni_mode_dropdown = ctk.CTkOptionMenu(
            self.omni_controls,
            values=["Voice Design", "Voice Cloning", "Auto Voice"],
            variable=self.selected_omni_mode,
            width=135,
            height=30,
            fg_color="#313244",
            button_color="#45475a",
            button_hover_color="#585b70",
            dropdown_fg_color="#1e1e2e",
            text_color="#cba6f7",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self._on_omni_mode_change,
        )
        self.omni_mode_dropdown.pack(side="left", padx=(0, 10))

        # Voice Design attribute widgets container
        self.design_attr_frame = ctk.CTkFrame(self.omni_controls, fg_color="transparent")
        self.design_attr_frame.pack(side="left", fill="both", expand=True)

        # Gender
        self.omni_gender_dropdown = ctk.CTkOptionMenu(
            self.design_attr_frame,
            values=OmniVoiceEngineManager.GENDER_OPTIONS["en"],
            variable=self.selected_omni_gender,
            width=90,
            height=30,
            fg_color="#313244",
            dropdown_fg_color="#1e1e2e",
            text_color="#cdd6f4",
            font=ctk.CTkFont(size=11),
            command=lambda v: setattr(self, "current_omni_gender", OmniVoiceEngineManager.GENDER_MAP.get(v, "female")),
        )
        self.omni_gender_dropdown.pack(side="left", padx=(0, 6))

        # Age
        self.omni_age_dropdown = ctk.CTkOptionMenu(
            self.design_attr_frame,
            values=OmniVoiceEngineManager.AGE_OPTIONS["en"],
            variable=self.selected_omni_age,
            width=115,
            height=30,
            fg_color="#313244",
            dropdown_fg_color="#1e1e2e",
            text_color="#cdd6f4",
            font=ctk.CTkFont(size=11),
            command=lambda v: setattr(self, "current_omni_age", OmniVoiceEngineManager.AGE_MAP.get(v, "young adult")),
        )
        self.omni_age_dropdown.pack(side="left", padx=(0, 6))

        # Pitch
        self.omni_pitch_dropdown = ctk.CTkOptionMenu(
            self.design_attr_frame,
            values=OmniVoiceEngineManager.PITCH_OPTIONS["en"],
            variable=self.selected_omni_pitch,
            width=120,
            height=30,
            fg_color="#313244",
            dropdown_fg_color="#1e1e2e",
            text_color="#cdd6f4",
            font=ctk.CTkFont(size=11),
            command=lambda v: setattr(self, "current_omni_pitch", OmniVoiceEngineManager.PITCH_MAP.get(v, "moderate pitch")),
        )
        self.omni_pitch_dropdown.pack(side="left", padx=(0, 6))

        # Style (Normal / Whisper)
        self.omni_style_dropdown = ctk.CTkOptionMenu(
            self.design_attr_frame,
            values=OmniVoiceEngineManager.STYLE_OPTIONS["en"],
            variable=self.selected_omni_style,
            width=90,
            height=30,
            fg_color="#313244",
            dropdown_fg_color="#1e1e2e",
            text_color="#cdd6f4",
            font=ctk.CTkFont(size=11),
            command=lambda v: setattr(self, "current_omni_style", OmniVoiceEngineManager.STYLE_MAP.get(v, "normal")),
        )
        self.omni_style_dropdown.pack(side="left", padx=(0, 6))

        # Accent
        self.omni_accent_dropdown = ctk.CTkOptionMenu(
            self.design_attr_frame,
            values=OmniVoiceEngineManager.ACCENT_OPTIONS["en"],
            variable=self.selected_omni_accent,
            width=135,
            height=30,
            fg_color="#313244",
            dropdown_fg_color="#1e1e2e",
            text_color="#cdd6f4",
            font=ctk.CTkFont(size=11),
            command=lambda v: setattr(self, "current_omni_accent", OmniVoiceEngineManager.ACCENT_MAP.get(v, "auto")),
        )
        self.omni_accent_dropdown.pack(side="left", padx=(0, 6))

        # Voice Cloning Container (when mode == 'clone')
        self.clone_attr_frame = ctk.CTkFrame(self.omni_controls, fg_color="transparent")

        self.browse_ref_btn = ctk.CTkButton(
            self.clone_attr_frame,
            text="Browse Audio...",
            width=120,
            height=30,
            corner_radius=6,
            fg_color="#89b4fa",
            text_color="#11111b",
            hover_color="#b4befe",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self._on_browse_ref_audio,
        )
        self.browse_ref_btn.pack(side="left", padx=(0, 8))

        self.ref_audio_label = ctk.CTkLabel(
            self.clone_attr_frame,
            textvariable=self.ref_audio_status_text,
            font=ctk.CTkFont(size=11),
            text_color="#a6adc8",
        )
        self.ref_audio_label.pack(side="left", padx=(0, 10))

    def _create_chat_frame(self):
        """Scrollable workspace container."""
        self.chat_container = ctk.CTkScrollableFrame(
            self,
            fg_color="#11111b",
            corner_radius=0,
        )
        self.chat_container.pack(side="top", fill="both", expand=True, padx=0, pady=0)
        self.chat_container.grid_columnconfigure(0, weight=1)

        self._add_welcome_banner()

    def _add_welcome_banner(self):
        """Adds a clean, minimal studio header card."""
        self.welcome_frame = ctk.CTkFrame(
            self.chat_container,
            fg_color="#1e1e2e",
            corner_radius=12,
            border_width=1,
            border_color="#313244",
        )
        self.welcome_frame.pack(fill="x", padx=20, pady=(16, 10))

        self.welcome_title = ctk.CTkLabel(
            self.welcome_frame,
            text="",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#cba6f7",
        )
        self.welcome_title.pack(fill="x", padx=16, pady=(12, 2))

        self.welcome_desc = ctk.CTkLabel(
            self.welcome_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="#a6adc8",
            justify="left",
        )
        self.welcome_desc.pack(fill="x", padx=16, pady=(0, 12))

    def _create_input_frame(self):
        """Bottom text entry bar with Emotional Quick Chips and generate button."""
        input_container = ctk.CTkFrame(self, fg_color="#181825", height=125, corner_radius=0)
        input_container.pack(side="bottom", fill="x", padx=0, pady=0)
        input_container.pack_propagate(False)

        input_container.grid_columnconfigure(0, weight=1)

        # Emotional & Non-Verbal Quick Chips Row
        chips_frame = ctk.CTkFrame(input_container, fg_color="transparent")
        chips_frame.grid(row=0, column=0, columnspan=2, padx=16, pady=(8, 4), sticky="ew")

        chips = [
            ("😂 [laughter]", "[laughter] "),
            ("🤫 [whisper]", "[whisper] "),
            ("⏸️ [pause]", " ... "),
            ("💨 [sigh]", "[sigh] "),
        ]

        for label, token in chips:
            btn = ctk.CTkButton(
                chips_frame,
                text=label,
                width=88,
                height=26,
                corner_radius=12,
                fg_color="#313244",
                text_color="#cdd6f4",
                hover_color="#45475a",
                font=ctk.CTkFont(size=11),
                command=lambda t=token: self._insert_chip_token(t),
            )
            btn.pack(side="left", padx=(0, 6))

        # Bottom Input Row
        self.text_entry = ctk.CTkEntry(
            input_container,
            placeholder_text=self.TRANSLATIONS["en"]["placeholder"],
            height=46,
            corner_radius=10,
            fg_color="#313244",
            text_color="#cdd6f4",
            placeholder_text_color="#6c7086",
            border_color="#45475a",
            font=ctk.CTkFont(size=14),
            justify="left",
        )
        self.text_entry.grid(row=1, column=0, padx=(16, 10), pady=(4, 14), sticky="ew")
        self.text_entry.bind("<Return>", lambda event: self.send_message())

        self.send_button = ctk.CTkButton(
            input_container,
            text=self.TRANSLATIONS["en"]["send_btn"],
            width=120,
            height=46,
            corner_radius=10,
            fg_color="#cba6f7",
            text_color="#11111b",
            hover_color="#b4befe",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.send_message,
        )
        self.send_button.grid(row=1, column=1, padx=(0, 16), pady=(4, 14), sticky="e")

    def _insert_chip_token(self, token: str):
        """Inserts token into the text entry at current cursor position."""
        try:
            curr_pos = self.text_entry.index("insert")
            self.text_entry.insert(curr_pos, token)
            self.text_entry.focus_set()
        except Exception:
            self.text_entry.insert("end", token)

    def _on_browse_ref_audio(self):
        """Opens file dialog to choose a reference WAV or MP3 audio file for voice cloning."""
        dlg_title = self.TRANSLATIONS[self.current_lang_code]["select_ref_audio_dlg"]
        path = filedialog.askopenfilename(
            title=dlg_title,
            filetypes=[("Audio Files", "*.wav;*.mp3;*.flac;*.m4a;*.ogg"), ("All Files", "*.*")],
        )
        if path:
            self.selected_ref_audio_path = path
            fname = os.path.basename(path)
            self.ref_audio_status_text.set(f"🎵 {fname}")

    def _on_engine_change(self, choice: str):
        """Switches active engine between Coqui XTTS v2 and k2-fsa OmniVoice."""
        if "omni" in choice.lower():
            self.current_engine_key = "omnivoice"
            self.tts_manager.set_engine("omnivoice")
            self.xtts_controls.pack_forget()
            self.omni_controls.pack(side="left", fill="both", expand=True, padx=16, pady=6)
            self._update_language_dropdown_for_engine()
        else:
            self.current_engine_key = "xtts"
            self.tts_manager.set_engine("xtts")
            self.omni_controls.pack_forget()
            self.xtts_controls.pack(side="left", fill="both", expand=True, padx=16, pady=6)
            self._update_language_dropdown_for_engine()

        self._refresh_hardware_badge()
        self._initialize_active_engine_async()

    def _on_omni_mode_change(self, choice: str):
        """Switches OmniVoice mode between Voice Design, Voice Cloning, and Auto."""
        val = choice.lower()
        if "clon" in val or "استنساخ" in val:
            self.current_omni_mode = "clone"
            self.design_attr_frame.pack_forget()
            self.clone_attr_frame.pack(side="left", fill="both", expand=True)
        elif "auto" in val or "تلقائي" in val:
            self.current_omni_mode = "auto"
            self.design_attr_frame.pack_forget()
            self.clone_attr_frame.pack_forget()
        else:
            self.current_omni_mode = "design"
            self.clone_attr_frame.pack_forget()
            self.design_attr_frame.pack(side="left", fill="both", expand=True)

    def _update_language_dropdown_for_engine(self):
        """Configures available language choices depending on selected engine."""
        if self.current_engine_key == "omnivoice":
            options = [item[0] for item in OmniVoiceEngineManager.POPULAR_LANGUAGES]
            self.lang_dropdown.configure(values=options)
            if self.current_lang_code == "ar":
                self.selected_lang_label.set("العربية (Arabic)")
            else:
                self.selected_lang_label.set("English")
        else:
            options = ["English", "العربية"]
            self.lang_dropdown.configure(values=options)
            self.selected_lang_label.set("العربية" if self.current_lang_code == "ar" else "English")

    def _get_current_lang_code(self) -> str:
        """Returns ISO language code based on current selection."""
        val = self.selected_lang_label.get()
        if self.current_engine_key == "omnivoice":
            return OmniVoiceEngineManager.resolve_language_code(val)
        if "English" in val or val.strip().lower() == "en":
            return "en"
        return "ar"

    def toggle_language(self):
        """Switches the application language from English to Arabic and vice versa."""
        if self.is_processing:
            return
        new_lang = "en" if self.current_lang_code == "ar" else "ar"
        self._apply_ui_language(new_lang)

    def _on_language_change(self, choice: str):
        """Handles language selection from the menu dropdown."""
        lang_code = "ar" if ("العربية" in choice or "arab" in choice.lower()) else "en"
        self._apply_ui_language(lang_code)

    def _apply_ui_language(self, lang_code: str):
        """Applies full English or Arabic localization across the entire window, menu, and cards."""
        lang = "en" if lang_code == "en" else "ar"
        self.current_lang_code = lang
        tr = self.TRANSLATIONS[lang]

        # 1. Window & Header Titles
        self.title(tr["window_title"])
        self.title_label.configure(text=tr["studio_title"])
        self._refresh_hardware_badge()

        # 2. Engine Labels & Options
        self.engine_label.configure(text=tr["engine_label"])
        engine_vals = [
            self.ENGINE_DISPLAY_NAMES[lang]["xtts"],
            self.ENGINE_DISPLAY_NAMES[lang]["omnivoice"],
        ]
        self.engine_dropdown.configure(values=engine_vals)
        self.selected_engine_label.set(self.ENGINE_DISPLAY_NAMES[lang][self.current_engine_key])

        # 3. Menu Controls & Toggle Button
        self.lang_label.configure(text=tr["lang_label"])
        self.lang_toggle_btn.configure(text=tr["toggle_btn"])
        self.gender_label.configure(text=tr["gender_label"])
        self.speaker_label.configure(text=tr["speaker_label"])
        self.clear_btn.configure(text=tr["clear_btn"])

        self._update_language_dropdown_for_engine()

        # 4. Localize XTTS Gender & Speaker Options
        gender_options = XTTSEngineManager.get_gender_options(lang)
        self.gender_dropdown.configure(values=gender_options)
        self.selected_gender.set(
            XTTSEngineManager.get_gender_display_label(self.current_gender_key, lang)
        )

        speaker_options = XTTSEngineManager.get_speaker_options(self.current_gender_key, lang)
        self.speaker_dropdown.configure(values=speaker_options)
        localized_speaker = XTTSEngineManager.get_speaker_display_name(self.current_speaker_id, lang)
        if localized_speaker in speaker_options:
            self.selected_speaker.set(localized_speaker)
        elif speaker_options:
            self.selected_speaker.set(speaker_options[0])
            self.current_speaker_id = XTTSEngineManager.resolve_speaker_id(speaker_options[0])

        # 5. Localize OmniVoice Controls
        self.omni_mode_label.configure(text=tr["mode_label"])
        mode_vals = [tr["mode_design"], tr["mode_clone"], tr["mode_auto"]]
        self.omni_mode_dropdown.configure(values=mode_vals)
        if self.current_omni_mode == "clone":
            self.selected_omni_mode.set(tr["mode_clone"])
        elif self.current_omni_mode == "auto":
            self.selected_omni_mode.set(tr["mode_auto"])
        else:
            self.selected_omni_mode.set(tr["mode_design"])

        self.omni_gender_dropdown.configure(values=OmniVoiceEngineManager.GENDER_OPTIONS[lang])
        self.omni_age_dropdown.configure(values=OmniVoiceEngineManager.AGE_OPTIONS[lang])
        self.omni_pitch_dropdown.configure(values=OmniVoiceEngineManager.PITCH_OPTIONS[lang])
        self.omni_style_dropdown.configure(values=OmniVoiceEngineManager.STYLE_OPTIONS[lang])
        self.omni_accent_dropdown.configure(values=OmniVoiceEngineManager.ACCENT_OPTIONS[lang])
        self.browse_ref_btn.configure(text=tr["browse_btn"])

        # 6. Welcome Card Localization & Alignment
        is_rtl = lang == "ar"
        self.welcome_title.configure(
            text=tr["welcome_title"],
            anchor="e" if is_rtl else "w",
            justify="right" if is_rtl else "left",
        )
        self.welcome_desc.configure(
            text=tr["welcome_desc"],
            anchor="e" if is_rtl else "w",
            justify="right" if is_rtl else "left",
        )

        # 7. Bottom Text Input & Send Button
        self.text_entry.configure(
            placeholder_text=tr["placeholder"],
            justify="right" if is_rtl else "left",
        )
        self.send_button.configure(text=tr["send_btn"])

        # 8. Update all existing cards & audio widgets
        for bubble in list(self.chat_bubbles):
            if bubble and bubble.winfo_exists() and hasattr(bubble, "update_ui_language"):
                bubble.update_ui_language(lang)

    def _on_gender_change(self, selected_gender: str):
        """Dynamically updates the voice dropdown based on chosen gender category."""
        self.current_gender_key = XTTSEngineManager.resolve_gender_key(selected_gender)
        voices = XTTSEngineManager.get_speaker_options(
            self.current_gender_key, self.current_lang_code
        )
        self.speaker_dropdown.configure(values=voices)
        if voices:
            self.selected_speaker.set(voices[0])
            self.current_speaker_id = XTTSEngineManager.resolve_speaker_id(voices[0])

    def _on_speaker_change(self, selected_speaker: str):
        """Tracks canonical speaker ID when user picks a voice."""
        self.current_speaker_id = XTTSEngineManager.resolve_speaker_id(selected_speaker)

    def clear_chat(self):
        """Stops active playback and clears all generated audio cards."""
        if self.is_processing:
            return
        try:
            AudioPlayerController().stop_audio()
        except Exception:
            pass
        for bubble in list(self.chat_bubbles):
            try:
                if bubble and bubble.winfo_exists():
                    bubble.destroy()
            except Exception:
                pass
        self.chat_bubbles.clear()

    def _initialize_active_engine_async(self):
        """Pre-loads the active speech model on a background thread."""
        def on_ready():
            self.after(0, self._refresh_hardware_badge)

        self.tts_manager.initialize_active_engine_async(on_ready=on_ready)

    def _refresh_hardware_badge(self):
        """Updates hardware badge text in the active UI language."""
        if not hasattr(self, "hardware_badge"):
            return
        tr = self.TRANSLATIONS[self.current_lang_code]
        engine = self.tts_manager.get_active_engine()
        engine_tag = "OmniVoice" if self.current_engine_key == "omnivoice" else "XTTS"
        device_label = engine.device_label

        if engine.is_ready:
            self.hardware_badge.configure(
                text=f"● {engine_tag} • {device_label} • {tr['ready_suffix']}",
                text_color="#a6e3a1",
            )
        else:
            badge_color = "#a6e3a1" if engine.device == "cuda" else "#89b4fa"
            self.hardware_badge.configure(
                text=f"● {engine_tag} • {device_label}",
                text_color=badge_color,
            )

    def send_message(self, event=None):
        """Captures long-form text input and starts async audio generation."""
        if self.is_processing:
            return

        text = self.text_entry.get().strip()
        if not text:
            return

        lang_code = self._get_current_lang_code()
        is_rtl = lang_code == "ar"

        # Determine speaker or instruct based on engine
        if self.current_engine_key == "omnivoice":
            if self.current_omni_mode == "design":
                speaker_or_instruct = OmniVoiceEngineManager.resolve_instruct(
                    gender=self.current_omni_gender,
                    age=self.current_omni_age,
                    pitch=self.current_omni_pitch,
                    style=self.current_omni_style,
                    accent=self.current_omni_accent,
                )
            elif self.current_omni_mode == "clone":
                speaker_or_instruct = "Cloned Voice"
            else:
                speaker_or_instruct = "Auto Voice"
        else:
            speaker_or_instruct = self.selected_speaker.get()
            self.current_speaker_id = XTTSEngineManager.resolve_speaker_id(speaker_or_instruct)

        self.text_entry.delete(0, "end")
        self._set_input_enabled(False)
        self.is_processing = True

        user_bubble = UserChatBubble(
            self.chat_container,
            text=text,
            is_rtl=is_rtl,
            ui_lang=self.current_lang_code,
        )
        user_bubble.pack(fill="x", padx=20, pady=6)
        self.chat_bubbles.append(user_bubble)

        initial_status = self.TRANSLATIONS[self.current_lang_code]["status_analyzing"]
        self.active_loading_bubble = LoadingChatBubble(
            self.chat_container, initial_text=initial_status, is_rtl=is_rtl
        )
        self.active_loading_bubble.pack(fill="x", padx=20, pady=6)

        self._scroll_to_bottom()

        thread = threading.Thread(
            target=self._run_generation_thread,
            args=(text, lang_code, speaker_or_instruct),
            daemon=True,
        )
        thread.start()

    def _run_generation_thread(self, text: str, lang_code: str, speaker_or_instruct: str):
        """Background execution handler with chunk progress callback."""
        def progress_callback(chunk_idx: int, total_chunks: int, chunk_text: str):
            pct = int((chunk_idx / float(total_chunks)) * 100)
            tr = self.TRANSLATIONS[self.current_lang_code]
            status_str = tr["status_chunk_fmt"].format(
                idx=chunk_idx, total=total_chunks, pct=pct
            )
            if self.active_loading_bubble:
                self.active_loading_bubble.update_status(status_str)

        try:
            result = self.tts_manager.generate_speech(
                text=text,
                language=lang_code,
                speaker_or_instruct=speaker_or_instruct,
                speed=1.0,
                omnivoice_mode=self.current_omni_mode,
                omnivoice_ref_audio=self.selected_ref_audio_path,
                progress_callback=progress_callback,
            )
            self.after(0, lambda: self._on_generation_success(result))
        except Exception as e:
            err_text = str(e)
            self.after(0, lambda: self._on_generation_error(err_text))

    def _on_generation_success(self, result: dict):
        """Callback on successful generation."""
        if self.active_loading_bubble:
            self.active_loading_bubble.destroy()
            self.active_loading_bubble = None

        ai_bubble = AIChatBubble(
            self.chat_container,
            text=result["text"],
            audio_filepath=result["filepath"],
            duration=result["duration"],
            speaker=result["speaker"],
            language=result["language"],
            ui_lang=self.current_lang_code,
            engine=result.get("engine", self.current_engine_key),
        )
        ai_bubble.pack(fill="x", padx=20, pady=6)
        self.chat_bubbles.append(ai_bubble)

        self.is_processing = False
        self._set_input_enabled(True)
        self._scroll_to_bottom()

    def _on_generation_error(self, error_msg: str):
        """Callback on generation error."""
        if self.active_loading_bubble:
            self.active_loading_bubble.destroy()
            self.active_loading_bubble = None

        self.is_processing = False
        self._set_input_enabled(True)

        tr = self.TRANSLATIONS[self.current_lang_code]
        messagebox.showerror(tr["error_title"], f"{tr['error_prefix']}{error_msg}")

    def _set_input_enabled(self, enabled: bool):
        """Locks or unlocks all interactive controls during speech synthesis."""
        state = "normal" if enabled else "disabled"
        self.text_entry.configure(state=state)
        self.send_button.configure(state=state)
        self.engine_dropdown.configure(state=state)
        self.lang_dropdown.configure(state=state)
        self.lang_toggle_btn.configure(state=state)
        self.gender_dropdown.configure(state=state)
        self.speaker_dropdown.configure(state=state)
        self.clear_btn.configure(state=state)

    def _scroll_to_bottom(self):
        """Scrolls workspace to bottom."""
        self.after(100, lambda: self.chat_container._parent_canvas.yview_moveto(1.0))
