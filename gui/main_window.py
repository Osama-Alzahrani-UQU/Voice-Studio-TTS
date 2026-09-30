r"""
main_window.py - Unified Luxury Voice Studio Main Application Window
---------------------------------------------------------------------
CustomTkinter desktop GUI window featuring luxury studio aesthetics,
generated branding graphics, full bidirectional English (LTR) <-> Arabic (RTL)
localization, an integrated live Microphone Recording Studio with real-time
soundwave animation, a 4-Stage Voice Readiness Diagnostic Suite, an Installed
Voices Library, and unified speech generation.
"""

import os
import sys
import json
import time
import threading
from typing import Dict, List, Optional, Callable, Any, Tuple
import tkinter as tk
from tkinter import messagebox, filedialog
import customtkinter as ctk
from PIL import Image

from xtts_engine import XTTSEngineManager, BASE_APP_DIR
from omnivoice_engine import OmniVoiceEngineManager
from unified_tts_manager import UnifiedTTSManager
from audio_player import AudioPlayerController
from gui.chat_bubble import UserChatBubble, AIChatBubble, LoadingChatBubble
from gui.waveform_visualizer import WaveformVisualizer
from audio_dsp import EFFECT_PRESETS
import voice_studio_recorder as vsr

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

ASSETS_DIR = os.path.join(BASE_APP_DIR, "assets")


class XTTSArabicEnglishChatApp(ctk.CTk):
    """
    Unified luxury desktop studio for neural speech synthesis, live microphone
    recording, voice readiness verification, and voice library management.
    """

    TRANSLATIONS = {
        "en": {
            "window_title": "Voice Studio — Unified Neural Speech & Recording Studio",
            "studio_title": "Voice Studio",
            "nav_synthesis": "🎛️ Speech Studio",
            "nav_recorder": "🎙️ Voice Recording Lab",
            "nav_library": "📚 Installed Voices",
            "toggle_btn": "العربية ⇄",
            "clear_btn": "Clear Studio",
            "category_label": "Category:",
            "speaker_label": "Active Voice:",
            "lang_label": "Language:",
            "dsp_label": "Mastering:",
            "welcome_title": "Unified Neural Voice Studio",
            "welcome_desc": "Type any text below to synthesize studio-grade speech. You can record your own voice in the Voice Lab, run 4-stage readiness tests, and pin it to your library!",
            "placeholder": "Enter your text here to synthesize speech (e.g. Hello world! [laughter])...",
            "send_btn": "Generate Speech",
            "status_analyzing": "Processing text & synthesizing speech...",
            "status_chunk_fmt": "Synthesizing segment {idx} of {total} ({pct}%)...",
            "error_title": "Studio Error",
            "error_prefix": "Operation failed:\n",
            "ready_suffix": "Ready",
            "mic_selector_label": "Input Microphone:",
            "btn_start_rec": "🎙️ Start Recording",
            "btn_stop_rec": "⏹️ Stop Recording",
            "btn_import_audio": "📁 Import Audio File...",
            "btn_play_rec": "▶️ Play Current Recording",
            "reading_prompt_title": "💡 Suggested Reading Prompt (Read for 5-10s):",
            "reading_prompt_text": "In the era of artificial intelligence, high-fidelity neural voices bring human expression to life with unmatched clarity, emotion, and nuance.",
            "diag_title": "🧪 Multi-Stage Voice Readiness Diagnostic Suite",
            "diag_btn_run": "⚡ Run Complete Readiness Diagnostics",
            "diag_status_pending": "⏳ Awaiting diagnostic tests",
            "diag_status_running": "🔄 Running tests...",
            "diag_status_passed": "✅ Passed 100%",
            "diag_status_failed": "❌ Quality Warning",
            "play_test_ar": "▶️ Play Arabic Test",
            "play_test_en": "▶️ Play English Test",
            "install_title": "📌 Pin & Install Voice to Permanent Library",
            "install_name_placeholder": "Enter Voice Name (e.g. My Studio Voice)...",
            "install_gender_male": "Male Voice",
            "install_gender_female": "Female Voice",
            "install_btn": "📌 Install & Pin Voice to Library",
            "install_success_title": "Voice Installed!",
            "install_success_msg": "Successfully installed voice to library! You can now use it to synthesize any text.",
            "lib_filter_all": "All Voices",
            "lib_filter_custom": "⭐ Custom Voices",
            "lib_filter_male": "Male Voices",
            "lib_filter_female": "Female Voices",
            "lib_play_btn": "▶️ Preview",
            "lib_select_btn": "✅ Use This Voice",
            "lib_delete_btn": "🗑️ Delete",
            "dsp_presets": {
                "broadcast": "📻 Broadcast",
                "podcast": "🎙️ Podcast",
                "warm": "☕ Warm",
                "bright": "✨ Bright",
                "raw": "🔇 Raw",
            },
        },
        "ar": {
            "window_title": "Voice Studio — استوديو الصوت الشامل والتسجيل المتقدم",
            "studio_title": "استوديو الصوت",
            "nav_synthesis": "🎛️ استوديو التوليد",
            "nav_recorder": "🎙️ استوديو التسجيل والفحص",
            "nav_library": "📚 مكتبة الأصوات المثبتة",
            "toggle_btn": "English ⇄",
            "clear_btn": "مسح المحادثة",
            "category_label": "الفئة:",
            "speaker_label": "الصوت النشط:",
            "lang_label": "اللغة:",
            "dsp_label": "المعالجة الصوتية:",
            "welcome_title": "استوديو الصوت والذكاء الاصطناعي الشامل",
            "welcome_desc": "اكتب النص بالأسفل لتوليد صوت فائق النقاء. يمكنك أيضاً تسجيل صوتك في استوديو التسجيل، وعمل اختبارات الجاهزية المتعددة، وتثبيته في مكتبتك!",
            "placeholder": "اكتب النص هنا لتحويله إلى مقطع صوتي (مثال: مرحباً بكم [laughter])...",
            "send_btn": "توليد الصوت",
            "status_analyzing": "جاري معالجة النص وبدء التوليد الصوتي...",
            "status_chunk_fmt": "جاري توليد المقطع {idx} من {total} ({pct}%)...",
            "error_title": "خطأ في الاستوديو",
            "error_prefix": "تعذر إتمام العملية:\n",
            "ready_suffix": "جاهز",
            "mic_selector_label": "ميكروفون الإدخال:",
            "btn_start_rec": "🎙️ بدء التسجيل الصوتي",
            "btn_stop_rec": "⏹️ إيقاف التسجيل",
            "btn_import_audio": "📁 استيراد ملف صوتي...",
            "btn_play_rec": "▶️ استماع للتسجيل الحالي",
            "reading_prompt_title": "💡 نص مقترح للقراءة أثناء التسجيل (اقرأ لمدة 5-10 ثوانٍ):",
            "reading_prompt_text": "في عصر الذكاء الاصطناعي، يولد الصوت البشري بأعلى درجات الدقة والوضوح، ليعبر عن المشاعر والنبرات بانسيابية وتأثير لا مثيل له.",
            "diag_title": "🧪 منظومة اختبارات جاهزية الصوت المتعددة",
            "diag_btn_run": "⚡ بدء كافة اختبارات جاهزية الصوت",
            "diag_status_pending": "⏳ بانتظار إجراء الفحص",
            "diag_status_running": "🔄 جاري فحص واختبار الصوت...",
            "diag_status_passed": "✅ تم الاجتياز بنجاح 100%",
            "diag_status_failed": "❌ تنبيه في الجودة",
            "play_test_ar": "▶️ استماع لاختبار النطق العربي",
            "play_test_en": "▶️ استماع لاختبار النطق الإنجليزي",
            "install_title": "📌 تثبيت وحفظ الصوت في مكتبة الأصوات الدائمة",
            "install_name_placeholder": "اكتب اسم الصوت (مثال: صوتي المخصص)...",
            "install_gender_male": "صوت رجالي",
            "install_gender_female": "صوت نسائي",
            "install_btn": "📌 تثبيت الصوت واعتماده في المكتبة",
            "install_success_title": "تم تثبيت الصوت!",
            "install_success_msg": "تم حفظ الصوت وتثبيته بنجاح في المكتبة! يمكنك الآن استخدامه فوراً لنطق أي نص.",
            "lib_filter_all": "كافة الأصوات",
            "lib_filter_custom": "⭐ أصوات مخصصة",
            "lib_filter_male": "أصوات رجالية",
            "lib_filter_female": "أصوات نسائية",
            "lib_play_btn": "▶️ استماع للعينة",
            "lib_select_btn": "✅ اختيار كصوت نشط",
            "lib_delete_btn": "🗑️ حذف",
            "dsp_presets": {
                "broadcast": "📻 إذاعي",
                "podcast": "🎙️ بودكاست",
                "warm": "☕ دافئ",
                "bright": "✨ مشرق",
                "raw": "🔇 خام",
            },
        },
    }

    def __init__(self):
        super().__init__()

        self.geometry("1180x860")
        self.minsize(980, 680)

        # Core unified manager & audio engine
        self.tts_manager = UnifiedTTSManager()
        self.recorder = vsr.AudioRecorder(sample_rate=24000)
        self.player = AudioPlayerController()

        # UI State Variables
        self.current_lang_code = "ar"  # Default to Arabic as requested by user
        self.current_tab = "synthesis"  # 'synthesis', 'recorder', 'library'
        self.current_category_key = "all"
        self.current_speaker_id = "Damien_Black"
        self.current_dsp_preset = "broadcast"
        self.is_processing = False

        # Audio recording & diagnostics state
        self.recorded_audio_path = None
        self.diagnostic_results = None
        self.test_audio_ar_path = None
        self.test_audio_en_path = None
        self.is_running_diag = False

        # Interactive StringVars
        self.selected_category = ctk.StringVar(value=XTTSEngineManager.get_gender_display_label("all", "ar"))
        self.selected_speaker = ctk.StringVar(value=XTTSEngineManager.get_speaker_display_name("Damien_Black", "ar"))
        self.selected_dsp_preset = ctk.StringVar(value=self.TRANSLATIONS["ar"]["dsp_presets"]["broadcast"])
        self.selected_speech_lang = ctk.StringVar(value="العربية")
        self.selected_mic_name = ctk.StringVar(value="Default Microphone")
        self.voice_install_name = ctk.StringVar(value="")
        self.voice_install_gender = ctk.StringVar(value=self.TRANSLATIONS["ar"]["install_gender_male"])

        self.chat_bubbles = []
        self.active_loading_bubble = None

        # Build Main UI Shell
        self._load_branding_assets()
        self._create_header_card()
        self._create_navigation_bar()

        # Main Workspace Container
        self.workspace_frame = ctk.CTkFrame(self, fg_color="#181825", corner_radius=0)
        self.workspace_frame.pack(side="top", fill="both", expand=True)

        # Create the 3 Workspaces
        self._create_synthesis_workspace()
        self._create_recorder_workspace()
        self._create_library_workspace()

        # Show initial workspace
        self._switch_workspace("synthesis")
        self._apply_ui_language(self.current_lang_code)
        self._initialize_models_async()

    def _load_branding_assets(self):
        """Loads generated 3D neon soundwave artwork for header and banners."""
        self.header_banner_image = None
        self.rec_studio_image = None
        try:
            h_path = os.path.join(ASSETS_DIR, "header_banner.jpg")
            if os.path.exists(h_path):
                img = Image.open(h_path)
                self.header_banner_image = ctk.CTkImage(light_image=img, dark_image=img, size=(1160, 68))

            r_path = os.path.join(ASSETS_DIR, "recording_studio_banner.jpg")
            if os.path.exists(r_path):
                rimg = Image.open(r_path)
                self.rec_studio_image = ctk.CTkImage(light_image=rimg, dark_image=rimg, size=(480, 140))
        except Exception as e:
            print(f"[Main Window] Note loading banner assets: {e}")

    def _create_header_card(self):
        """Top luxury header bar displaying generated artwork and status."""
        self.header_card = ctk.CTkFrame(self, fg_color="#11111b", height=72, corner_radius=0)
        self.header_card.pack(side="top", fill="x", padx=0, pady=0)
        self.header_card.grid_columnconfigure(1, weight=1)

        # Optional Art Banner Background
        if self.header_banner_image:
            self.banner_art_label = ctk.CTkLabel(
                self.header_card,
                image=self.header_banner_image,
                text="",
            )
            self.banner_art_label.place(relx=0.5, rely=0.5, anchor="center")

        # Glass Overlay Container
        glass_overlay = ctk.CTkFrame(self.header_card, fg_color=("#11111b", "#11111b"), corner_radius=0)
        glass_overlay.pack(fill="both", expand=True, padx=12, pady=6)
        glass_overlay.grid_columnconfigure(1, weight=1)

        # Title with glowing violet accent
        self.title_label = ctk.CTkLabel(
            glass_overlay,
            text="🎙️ Voice Studio",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color="#cba6f7",
        )
        self.title_label.grid(row=0, column=0, padx=14, pady=10, sticky="w")

        # Neural Engine / Hardware Ready Pill
        dev_label = self.tts_manager.get_active_device_label()
        badge_col = "#a6e3a1" if self.tts_manager.get_active_engine().device == "cuda" else "#89b4fa"
        self.hardware_pill = ctk.CTkLabel(
            glass_overlay,
            text=f"● Neural Core Active • {dev_label}",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=badge_col,
            fg_color="#1e1e2e",
            corner_radius=8,
            padx=12,
            pady=4,
        )
        self.hardware_pill.grid(row=0, column=1, padx=8, pady=10, sticky="w")

        # Header Right Actions
        right_box = ctk.CTkFrame(glass_overlay, fg_color="transparent")
        right_box.grid(row=0, column=2, padx=12, pady=10, sticky="e")

        self.lang_toggle_btn = ctk.CTkButton(
            right_box,
            text="English ⇄",
            width=90,
            height=30,
            corner_radius=8,
            fg_color="#313244",
            hover_color="#45475a",
            text_color="#cdd6f4",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self.toggle_language,
        )
        self.lang_toggle_btn.pack(side="left", padx=4)

        self.clear_btn = ctk.CTkButton(
            right_box,
            text="Clear",
            width=70,
            height=30,
            corner_radius=8,
            fg_color="#313244",
            hover_color="#f38ba8",
            text_color="#f38ba8",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self.clear_chat,
        )
        self.clear_btn.pack(side="left", padx=4)

    def _create_navigation_bar(self):
        """Luxury studio menu bar with custom cards for the 3 workspaces."""
        self.nav_bar = ctk.CTkFrame(self, fg_color="#181825", height=46, corner_radius=0)
        self.nav_bar.pack(side="top", fill="x", padx=0, pady=0)

        nav_inner = ctk.CTkFrame(self.nav_bar, fg_color="transparent")
        nav_inner.pack(fill="x", padx=16, pady=4)

        self.btn_tab_synthesis = ctk.CTkButton(
            nav_inner,
            text=self.TRANSLATIONS[self.current_lang_code]["nav_synthesis"],
            height=34,
            corner_radius=8,
            fg_color="#cba6f7",
            hover_color="#b4befe",
            text_color="#11111b",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda: self._switch_workspace("synthesis"),
        )
        self.btn_tab_synthesis.pack(side="left", padx=(0, 8))

        self.btn_tab_recorder = ctk.CTkButton(
            nav_inner,
            text=self.TRANSLATIONS[self.current_lang_code]["nav_recorder"],
            height=34,
            corner_radius=8,
            fg_color="#313244",
            hover_color="#45475a",
            text_color="#cdd6f4",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda: self._switch_workspace("recorder"),
        )
        self.btn_tab_recorder.pack(side="left", padx=8)

        self.btn_tab_library = ctk.CTkButton(
            nav_inner,
            text=self.TRANSLATIONS[self.current_lang_code]["nav_library"],
            height=34,
            corner_radius=8,
            fg_color="#313244",
            hover_color="#45475a",
            text_color="#cdd6f4",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda: self._switch_workspace("library"),
        )
        self.btn_tab_library.pack(side="left", padx=8)

    def _switch_workspace(self, tab_name: str):
        """Switches active view container between Synthesis, Voice Lab, and Library."""
        self.current_tab = tab_name

        # Reset button styles
        for tab_id, btn in (
            ("synthesis", self.btn_tab_synthesis),
            ("recorder", self.btn_tab_recorder),
            ("library", self.btn_tab_library),
        ):
            if tab_id == tab_name:
                btn.configure(fg_color="#cba6f7", text_color="#11111b")
            else:
                btn.configure(fg_color="#313244", text_color="#cdd6f4")

        # Hide all
        self.synthesis_frame.pack_forget()
        self.recorder_frame.pack_forget()
        self.library_frame.pack_forget()

        if tab_name == "synthesis":
            self.synthesis_frame.pack(fill="both", expand=True)
            self._refresh_voice_selectors()
        elif tab_name == "recorder":
            self.recorder_frame.pack(fill="both", expand=True)
            self._refresh_microphones()
        elif tab_name == "library":
            self.library_frame.pack(fill="both", expand=True)
            self._refresh_library_cards()

    # =========================================================================
    # 1. SYNTHESIS WORKSPACE
    # =========================================================================
    def _create_synthesis_workspace(self):
        """Builds speech synthesis workspace with toolbar, bubbles, and text input."""
        self.synthesis_frame = ctk.CTkFrame(self.workspace_frame, fg_color="transparent")

        # Settings Toolbar
        toolbar = ctk.CTkFrame(self.synthesis_frame, fg_color="#1e1e2e", height=50, corner_radius=0)
        toolbar.pack(side="top", fill="x", padx=0, pady=0)
        tb_inner = ctk.CTkFrame(toolbar, fg_color="transparent")
        tb_inner.pack(fill="x", padx=16, pady=8)

        # Category Filter
        self.lbl_cat = ctk.CTkLabel(tb_inner, text="Category:", font=ctk.CTkFont(size=11, weight="bold"), text_color="#a6adc8")
        self.lbl_cat.pack(side="left", padx=(0, 4))

        self.dropdown_cat = ctk.CTkOptionMenu(
            tb_inner,
            values=XTTSEngineManager.get_category_options(self.current_lang_code),
            variable=self.selected_category,
            width=135,
            height=30,
            fg_color="#313244",
            button_color="#45475a",
            dropdown_fg_color="#1e1e2e",
            command=self._on_category_change,
        )
        self.dropdown_cat.pack(side="left", padx=(0, 10))

        # Voice Selector
        self.lbl_spk = ctk.CTkLabel(tb_inner, text="Voice:", font=ctk.CTkFont(size=11, weight="bold"), text_color="#a6adc8")
        self.lbl_spk.pack(side="left", padx=(0, 4))

        self.dropdown_speaker = ctk.CTkOptionMenu(
            tb_inner,
            values=XTTSEngineManager.get_speaker_options("all", self.current_lang_code),
            variable=self.selected_speaker,
            width=220,
            height=30,
            fg_color="#313244",
            button_color="#45475a",
            dropdown_fg_color="#1e1e2e",
            command=self._on_speaker_change,
        )
        self.dropdown_speaker.pack(side="left", padx=(0, 10))

        # Speech Language
        self.lbl_lang = ctk.CTkLabel(tb_inner, text="Language:", font=ctk.CTkFont(size=11, weight="bold"), text_color="#a6adc8")
        self.lbl_lang.pack(side="left", padx=(0, 4))

        self.dropdown_speech_lang = ctk.CTkOptionMenu(
            tb_inner,
            values=["العربية", "English", "Español", "Français", "Deutsch", "Italiano", "Türkçe"],
            variable=self.selected_speech_lang,
            width=105,
            height=30,
            fg_color="#313244",
            button_color="#45475a",
            dropdown_fg_color="#1e1e2e",
        )
        self.dropdown_speech_lang.pack(side="left", padx=(0, 10))

        # DSP Mastering
        self.lbl_dsp = ctk.CTkLabel(tb_inner, text="Mastering:", font=ctk.CTkFont(size=11, weight="bold"), text_color="#a6adc8")
        self.lbl_dsp.pack(side="left", padx=(0, 4))

        self.dropdown_dsp = ctk.CTkOptionMenu(
            tb_inner,
            values=list(self.TRANSLATIONS[self.current_lang_code]["dsp_presets"].values()),
            variable=self.selected_dsp_preset,
            width=120,
            height=30,
            fg_color="#313244",
            button_color="#45475a",
            dropdown_fg_color="#1e1e2e",
            command=self._on_dsp_change,
        )
        self.dropdown_dsp.pack(side="left", padx=(0, 6))

        # Chat Bubble History
        self.chat_container = ctk.CTkScrollableFrame(self.synthesis_frame, fg_color="#181825")
        self.chat_container.pack(fill="both", expand=True, padx=12, pady=8)

        # Welcome Card
        self.welcome_card = ctk.CTkFrame(self.chat_container, fg_color="#1e1e2e", corner_radius=12)
        self.welcome_card.pack(fill="x", padx=16, pady=12)

        self.welcome_title = ctk.CTkLabel(
            self.welcome_card,
            text=self.TRANSLATIONS[self.current_lang_code]["welcome_title"],
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#cba6f7",
        )
        self.welcome_title.pack(anchor="w", padx=16, pady=(12, 4))

        self.welcome_desc = ctk.CTkLabel(
            self.welcome_card,
            text=self.TRANSLATIONS[self.current_lang_code]["welcome_desc"],
            font=ctk.CTkFont(size=12),
            text_color="#a6adc8",
            wraplength=850,
            justify="left",
        )
        self.welcome_desc.pack(anchor="w", padx=16, pady=(0, 12))

        # Bottom Input Bar
        input_bar = ctk.CTkFrame(self.synthesis_frame, fg_color="#1e1e2e", corner_radius=0)
        input_bar.pack(side="bottom", fill="x", padx=0, pady=0)

        # Emotion & Prosody Quick Chips
        chips_frame = ctk.CTkFrame(input_bar, fg_color="transparent")
        chips_frame.pack(fill="x", padx=16, pady=(8, 4))

        for chip_text, insert_val in (
            ("😄 ضحك", " [laughter] "),
            ("🤫 همس", " [whisper] "),
            ("⏸️ توقف", " [pause] "),
            ("😮‍💨 تنهد", " [sigh] "),
            ("⚡ سريع", " [fast] "),
            ("🐢 بطيء", " [slow] "),
            ("🎯 تأكيد", " [emphasis] "),
        ):
            c_btn = ctk.CTkButton(
                chips_frame,
                text=chip_text,
                width=76,
                height=24,
                corner_radius=6,
                fg_color="#313244",
                hover_color="#45475a",
                text_color="#cdd6f4",
                font=ctk.CTkFont(size=10),
                command=lambda val=insert_val: self._insert_chip_text(val),
            )
            c_btn.pack(side="left", padx=3)

        # Text input & Generate Button
        in_row = ctk.CTkFrame(input_bar, fg_color="transparent")
        in_row.pack(fill="x", padx=16, pady=(0, 12))
        in_row.grid_columnconfigure(0, weight=1)

        self.text_entry = ctk.CTkEntry(
            in_row,
            placeholder_text=self.TRANSLATIONS[self.current_lang_code]["placeholder"],
            height=44,
            corner_radius=10,
            fg_color="#181825",
            border_color="#313244",
            text_color="#cdd6f4",
            font=ctk.CTkFont(size=13),
        )
        self.text_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.text_entry.bind("<Return>", lambda e: self.send_message())

        self.send_button = ctk.CTkButton(
            in_row,
            text=self.TRANSLATIONS[self.current_lang_code]["send_btn"],
            width=130,
            height=44,
            corner_radius=10,
            fg_color="#cba6f7",
            hover_color="#b4befe",
            text_color="#11111b",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.send_message,
        )
        self.send_button.grid(row=0, column=1)

    def _insert_chip_text(self, tag: str):
        self.text_entry.insert("insert", tag)
        self.text_entry.focus()

    # =========================================================================
    # 2. VOICE RECORDING & READINESS LAB WORKSPACE
    # =========================================================================
    def _create_recorder_workspace(self):
        """Builds live microphone recording studio, animated visualizer, and 4-stage test suite."""
        self.recorder_frame = ctk.CTkScrollableFrame(self.workspace_frame, fg_color="#181825")

        # Top Studio Banner Card with Art
        rec_header_card = ctk.CTkFrame(self.recorder_frame, fg_color="#1e1e2e", corner_radius=12)
        rec_header_card.pack(fill="x", padx=16, pady=(12, 8))
        rec_header_card.grid_columnconfigure(1, weight=1)

        if self.rec_studio_image:
            art_lbl = ctk.CTkLabel(rec_header_card, image=self.rec_studio_image, text="")
            art_lbl.grid(row=0, column=0, rowspan=2, padx=12, pady=12)

        hdr_info = ctk.CTkFrame(rec_header_card, fg_color="transparent")
        hdr_info.grid(row=0, column=1, sticky="nsew", padx=12, pady=14)

        self.lbl_rec_title = ctk.CTkLabel(
            hdr_info,
            text="🎙️ Voice Recording & Quality Diagnostic Lab",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#cba6f7",
        )
        self.lbl_rec_title.pack(anchor="w")

        self.lbl_rec_desc = ctk.CTkLabel(
            hdr_info,
            text="Record high-fidelity reference audio directly from your microphone. Run multi-stage phonetic & acoustic tests to guarantee the voice is ready to articulate any arbitrary text, then install it permanently!",
            font=ctk.CTkFont(size=12),
            text_color="#a6adc8",
            wraplength=550,
            justify="left",
        )
        self.lbl_rec_desc.pack(anchor="w", pady=(4, 8))

        # Microphone Input Selector
        mic_row = ctk.CTkFrame(hdr_info, fg_color="transparent")
        mic_row.pack(anchor="w", fill="x")

        self.lbl_mic = ctk.CTkLabel(mic_row, text="Microphone:", font=ctk.CTkFont(size=11, weight="bold"), text_color="#cdd6f4")
        self.lbl_mic.pack(side="left", padx=(0, 6))

        self.dropdown_mic = ctk.CTkOptionMenu(
            mic_row,
            values=["Default Microphone"],
            variable=self.selected_mic_name,
            width=280,
            height=30,
            fg_color="#313244",
            dropdown_fg_color="#1e1e2e",
        )
        self.dropdown_mic.pack(side="left", padx=4)

        # Animated Soundwave Visualizer Canvas
        vis_container = ctk.CTkFrame(self.recorder_frame, fg_color="#1e1e2e", corner_radius=12)
        vis_container.pack(fill="x", padx=16, pady=8)

        self.visualizer = WaveformVisualizer(vis_container, height=135)
        self.visualizer.pack(fill="x", expand=True, padx=12, pady=12)

        # Recording Actions Controls
        rec_ctrls = ctk.CTkFrame(self.recorder_frame, fg_color="#1e1e2e", corner_radius=12)
        rec_ctrls.pack(fill="x", padx=16, pady=8)
        rc_inner = ctk.CTkFrame(rec_ctrls, fg_color="transparent")
        rc_inner.pack(fill="x", padx=14, pady=12)

        self.btn_rec_toggle = ctk.CTkButton(
            rc_inner,
            text=self.TRANSLATIONS[self.current_lang_code]["btn_start_rec"],
            height=38,
            corner_radius=8,
            fg_color="#f38ba8",
            hover_color="#eba0ac",
            text_color="#11111b",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._toggle_recording,
        )
        self.btn_rec_toggle.pack(side="left", padx=(0, 8))

        self.btn_import_audio = ctk.CTkButton(
            rc_inner,
            text=self.TRANSLATIONS[self.current_lang_code]["btn_import_audio"],
            height=38,
            corner_radius=8,
            fg_color="#313244",
            hover_color="#45475a",
            text_color="#cdd6f4",
            font=ctk.CTkFont(size=12),
            command=self._import_audio_file,
        )
        self.btn_import_audio.pack(side="left", padx=6)

        self.btn_play_rec = ctk.CTkButton(
            rc_inner,
            text=self.TRANSLATIONS[self.current_lang_code]["btn_play_rec"],
            height=38,
            corner_radius=8,
            fg_color="#313244",
            hover_color="#45475a",
            text_color="#a6e3a1",
            font=ctk.CTkFont(size=12),
            command=self._play_current_recording,
        )
        self.btn_play_rec.pack(side="left", padx=6)

        self.lbl_rec_status = ctk.CTkLabel(
            rc_inner,
            text="No audio recorded yet",
            font=ctk.CTkFont(size=11),
            text_color="#a6adc8",
        )
        self.lbl_rec_status.pack(side="right", padx=10)

        # Guided Reading Prompt Card
        self.prompt_card = ctk.CTkFrame(self.recorder_frame, fg_color="#1e1e2e", corner_radius=12)
        self.prompt_card.pack(fill="x", padx=16, pady=8)

        self.lbl_reading_title = ctk.CTkLabel(
            self.prompt_card,
            text=self.TRANSLATIONS[self.current_lang_code]["reading_prompt_title"],
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#f9e2af",
        )
        self.lbl_reading_title.pack(anchor="w", padx=16, pady=(10, 4))

        self.lbl_reading_text = ctk.CTkLabel(
            self.prompt_card,
            text=self.TRANSLATIONS[self.current_lang_code]["reading_prompt_text"],
            font=ctk.CTkFont(size=13),
            text_color="#cdd6f4",
            wraplength=900,
            justify="left",
        )
        self.lbl_reading_text.pack(anchor="w", padx=16, pady=(0, 12))

        # 4-Stage Diagnostics Section
        self.diag_frame = ctk.CTkFrame(self.recorder_frame, fg_color="#1e1e2e", corner_radius=12)
        self.diag_frame.pack(fill="x", padx=16, pady=8)

        diag_hdr = ctk.CTkFrame(self.diag_frame, fg_color="transparent")
        diag_hdr.pack(fill="x", padx=16, pady=(12, 6))

        self.lbl_diag_header = ctk.CTkLabel(
            diag_hdr,
            text=self.TRANSLATIONS[self.current_lang_code]["diag_title"],
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#cba6f7",
        )
        self.lbl_diag_header.pack(side="left")

        self.btn_run_diag = ctk.CTkButton(
            diag_hdr,
            text=self.TRANSLATIONS[self.current_lang_code]["diag_btn_run"],
            height=32,
            corner_radius=8,
            fg_color="#89b4fa",
            hover_color="#74c7ec",
            text_color="#11111b",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._start_diagnostics_suite,
        )
        self.btn_run_diag.pack(side="right")

        # 4 Test Cards
        self.test_cards = {}
        for idx, (t_id, t_title_en, t_title_ar) in enumerate([
            ("acoustic", "1. Signal & Acoustic Quality", "١. نقاء وجودة الإشارة الصوتية"),
            ("arabic", "2. Arabic Phonetic Articulation", "٢. اختبار نطق النص العربي الفصيح"),
            ("english", "3. English & Bilingual Prosody", "٣. اختبار نطق النص الإنجليزي والتناغم"),
            ("universal", "4. Universal Text Readiness", "٤. الجاهزية الشاملة لنطق أي نص"),
        ]):
            card = ctk.CTkFrame(self.diag_frame, fg_color="#181825", corner_radius=8)
            card.pack(fill="x", padx=16, pady=4)
            card.grid_columnconfigure(1, weight=1)

            title_txt = t_title_ar if self.current_lang_code == "ar" else t_title_en
            lbl_t = ctk.CTkLabel(card, text=title_txt, font=ctk.CTkFont(size=12, weight="bold"), text_color="#cdd6f4")
            lbl_t.grid(row=0, column=0, padx=12, pady=8, sticky="w")

            lbl_d = ctk.CTkLabel(card, text=self.TRANSLATIONS[self.current_lang_code]["diag_status_pending"], font=ctk.CTkFont(size=11), text_color="#6c7086")
            lbl_d.grid(row=0, column=1, padx=8, pady=8, sticky="w")

            status_badge = ctk.CTkLabel(card, text="PENDING", font=ctk.CTkFont(size=10, weight="bold"), text_color="#89b4fa", fg_color="#313244", corner_radius=6, padx=8, pady=2)
            status_badge.grid(row=0, column=2, padx=12, pady=8, sticky="e")

            # Inline playback button (for synthesis tests)
            play_btn = None
            if t_id in ("arabic", "english"):
                btn_txt = self.TRANSLATIONS[self.current_lang_code]["play_test_ar"] if t_id == "arabic" else self.TRANSLATIONS[self.current_lang_code]["play_test_en"]
                play_btn = ctk.CTkButton(
                    card,
                    text=btn_txt,
                    width=140,
                    height=26,
                    corner_radius=6,
                    fg_color="#313244",
                    hover_color="#45475a",
                    text_color="#a6e3a1",
                    font=ctk.CTkFont(size=10),
                    state="disabled",
                    command=lambda tid=t_id: self._play_test_audio(tid),
                )
                play_btn.grid(row=0, column=3, padx=8, pady=8, sticky="e")

            self.test_cards[t_id] = {
                "frame": card,
                "title_lbl": lbl_t,
                "desc_lbl": lbl_d,
                "badge": status_badge,
                "play_btn": play_btn,
                "title_en": t_title_en,
                "title_ar": t_title_ar,
            }

        # Overall Score Meter
        self.score_container = ctk.CTkFrame(self.diag_frame, fg_color="transparent")
        self.score_container.pack(fill="x", padx=16, pady=(6, 12))

        self.lbl_overall_score = ctk.CTkLabel(
            self.score_container,
            text="Readiness Score: --",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#cba6f7",
        )
        self.lbl_overall_score.pack(side="left")

        # Voice Installation Card
        self.install_card = ctk.CTkFrame(self.recorder_frame, fg_color="#1e1e2e", corner_radius=12)
        self.install_card.pack(fill="x", padx=16, pady=(8, 16))

        self.lbl_install_hdr = ctk.CTkLabel(
            self.install_card,
            text=self.TRANSLATIONS[self.current_lang_code]["install_title"],
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#a6e3a1",
        )
        self.lbl_install_hdr.pack(anchor="w", padx=16, pady=(12, 8))

        inst_row = ctk.CTkFrame(self.install_card, fg_color="transparent")
        inst_row.pack(fill="x", padx=16, pady=(0, 14))
        inst_row.grid_columnconfigure(0, weight=1)

        self.entry_voice_name = ctk.CTkEntry(
            inst_row,
            placeholder_text=self.TRANSLATIONS[self.current_lang_code]["install_name_placeholder"],
            textvariable=self.voice_install_name,
            height=38,
            corner_radius=8,
            fg_color="#181825",
            border_color="#313244",
            text_color="#cdd6f4",
        )
        self.entry_voice_name.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        self.dropdown_install_gender = ctk.CTkOptionMenu(
            inst_row,
            values=[
                self.TRANSLATIONS[self.current_lang_code]["install_gender_male"],
                self.TRANSLATIONS[self.current_lang_code]["install_gender_female"],
            ],
            variable=self.voice_install_gender,
            width=130,
            height=38,
            fg_color="#313244",
            dropdown_fg_color="#1e1e2e",
        )
        self.dropdown_install_gender.grid(row=0, column=1, padx=(0, 10))

        self.btn_install_voice = ctk.CTkButton(
            inst_row,
            text=self.TRANSLATIONS[self.current_lang_code]["install_btn"],
            height=38,
            corner_radius=8,
            fg_color="#a6e3a1",
            hover_color="#94e2d5",
            text_color="#11111b",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._install_verified_voice,
        )
        self.btn_install_voice.grid(row=0, column=2)

    def _refresh_microphones(self):
        """Discovers input audio devices and populates dropdown."""
        devs = vsr.get_input_devices()
        dev_names = [f"[{d['id']}] {d['name'][:36]}" if d["id"] is not None else d["name"] for d in devs]
        self.dropdown_mic.configure(values=dev_names)
        if dev_names:
            self.selected_mic_name.set(dev_names[0])

    def _toggle_recording(self):
        """Starts or stops live microphone recording."""
        if not self.recorder.is_recording:
            # Start Recording
            try:
                selected_txt = self.selected_mic_name.get()
                dev_id = None
                if selected_txt.startswith("["):
                    try:
                        dev_id = int(selected_txt.split("]")[0][1:])
                    except Exception:
                        dev_id = None

                self.btn_rec_toggle.configure(text=self.TRANSLATIONS[self.current_lang_code]["btn_stop_rec"], fg_color="#f38ba8")
                self.visualizer.set_recording_state(True)
                self.lbl_rec_status.configure(text="Recording live audio from microphone...", text_color="#f38ba8")

                def on_chunk(chunk, rms, peak_db, elapsed):
                    self.after(0, lambda: self.visualizer.update_audio_chunk(chunk, rms, peak_db, elapsed))

                self.recorder.start_recording(device_id=dev_id, on_chunk=on_chunk)
            except Exception as e:
                messagebox.showerror("Recording Error", f"Failed to start recording:\n{e}")
                self.visualizer.set_recording_state(False)
        else:
            # Stop Recording
            out_file = self.recorder.stop_recording()
            self.visualizer.set_recording_state(False)
            self.btn_rec_toggle.configure(text=self.TRANSLATIONS[self.current_lang_code]["btn_start_rec"], fg_color="#cba6f7")
            if out_file and os.path.exists(out_file):
                self.recorded_audio_path = out_file
                dur = os.path.getsize(out_file) / (24000 * 4)
                self.lbl_rec_status.configure(text=f"Recorded: {os.path.basename(out_file)} ({dur:.1f}s)", text_color="#a6e3a1")
                # Auto-run acoustic check
                self.after(100, lambda: self._run_single_test("acoustic"))

    def _import_audio_file(self):
        """Imports reference audio file from local disk."""
        path = filedialog.askopenfilename(
            title="Select Voice Reference Audio",
            filetypes=[("Audio Files", "*.wav;*.mp3;*.m4a;*.ogg;*.flac")],
        )
        if path and os.path.exists(path):
            self.recorded_audio_path = path
            self.lbl_rec_status.configure(text=f"Loaded: {os.path.basename(path)}", text_color="#a6e3a1")
            self._run_single_test("acoustic")

    def _play_current_recording(self):
        """Plays the active recorded audio."""
        if not self.recorded_audio_path or not os.path.exists(self.recorded_audio_path):
            messagebox.showwarning("No Recording", "Please record or import an audio clip first.")
            return
        try:
            self.player.play_audio(self.recorded_audio_path)
        except Exception as e:
            messagebox.showerror("Playback Error", f"Failed to play recording:\n{e}")

    def _run_single_test(self, test_id: str):
        """Runs the acoustic quality check on recorded audio."""
        if not self.recorded_audio_path:
            return
        res = vsr.VoiceReadinessDiagnostic.test_acoustic_quality(self.recorded_audio_path)
        card = self.test_cards.get("acoustic")
        if card:
            detail = res["details_ar"] if self.current_lang_code == "ar" else res["details_en"]
            card["desc_lbl"].configure(text=detail, text_color="#cdd6f4")
            if res["passed"]:
                card["badge"].configure(text=f"PASSED ({res['score']}%)", text_color="#a6e3a1")
            else:
                card["badge"].configure(text="WARNING", text_color="#f38ba8")

    def _start_diagnostics_suite(self):
        """Executes the complete 4-stage readiness diagnostic suite on a background thread."""
        if self.is_running_diag:
            return
        if not self.recorded_audio_path or not os.path.exists(self.recorded_audio_path):
            messagebox.showwarning("No Audio", "Please record or load an audio file first before running tests.")
            return

        self.is_running_diag = True
        self.btn_run_diag.configure(state="disabled")

        # Set all to running
        for t_id, card in self.test_cards.items():
            card["desc_lbl"].configure(text=self.TRANSLATIONS[self.current_lang_code]["diag_status_running"], text_color="#89b4fa")
            card["badge"].configure(text="TESTING", text_color="#f9e2af")

        def worker():
            def progress(step, total, msg):
                self.after(0, lambda: self.lbl_overall_score.configure(text=f"Running Test {step}/{total}: {msg}"))

            suite_res = vsr.VoiceReadinessDiagnostic.run_full_suite(
                self.recorded_audio_path,
                self.tts_manager,
                progress_callback=progress,
            )
            self.after(0, lambda: self._on_diagnostics_complete(suite_res))

        threading.Thread(target=worker, daemon=True).start()

    def _on_diagnostics_complete(self, suite_res: Dict[str, Any]):
        """Renders 4-stage diagnostic results and unlocks installation."""
        self.is_running_diag = False
        self.btn_run_diag.configure(state="normal")
        self.diagnostic_results = suite_res

        for test in suite_res.get("tests", []):
            tid = test["id"]
            card = None
            if tid == "acoustic":
                card = self.test_cards.get("acoustic")
            elif "arabic" in tid:
                card = self.test_cards.get("arabic")
                if test.get("audio_path"):
                    self.test_audio_ar_path = test["audio_path"]
                    if card and card.get("play_btn"):
                        card["play_btn"].configure(state="normal")
            elif "english" in tid:
                card = self.test_cards.get("english")
                if test.get("audio_path"):
                    self.test_audio_en_path = test["audio_path"]
                    if card and card.get("play_btn"):
                        card["play_btn"].configure(state="normal")
            elif "universal" in tid:
                card = self.test_cards.get("universal")

            if card:
                detail = test.get("details_ar") if self.current_lang_code == "ar" else test.get("details_en", "")
                card["desc_lbl"].configure(text=detail, text_color="#cdd6f4")
                if test.get("passed"):
                    card["badge"].configure(text=f"PASSED ({test.get('score', 100)}%)", text_color="#a6e3a1")
                else:
                    card["badge"].configure(text="FAILED", text_color="#f38ba8")

        score = suite_res.get("overall_score", 0)
        passed = suite_res.get("passed", False)
        summary = suite_res.get("summary_ar") if self.current_lang_code == "ar" else suite_res.get("summary_en")

        color = "#a6e3a1" if passed else "#f38ba8"
        self.lbl_overall_score.configure(text=f"🏆 {summary}", text_color=color)

    def _play_test_audio(self, test_id: str):
        """Plays Arabic or English diagnostic test speech audio."""
        target = self.test_audio_ar_path if test_id == "arabic" else self.test_audio_en_path
        if target and os.path.exists(target):
            try:
                self.player.play_audio(target)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to play test audio:\n{e}")

    def _install_verified_voice(self):
        """Installs and pins current recorded voice to the permanent voice library."""
        if not self.recorded_audio_path or not os.path.exists(self.recorded_audio_path):
            messagebox.showwarning("No Recording", "Please record or import a voice first.")
            return

        name = self.voice_install_name.get().strip()
        if not name:
            messagebox.showwarning("Voice Name Required", "Please enter a name for your custom voice.")
            return

        gender_str = self.voice_install_gender.get()
        gender = "female" if "نسائ" in gender_str or "fem" in gender_str.lower() else "male"

        try:
            profile = vsr.install_voice_profile(name, self.recorded_audio_path, gender=gender)
            self._refresh_voice_selectors()

            tr = self.TRANSLATIONS[self.current_lang_code]
            msg = f"{tr['install_success_msg']}\n\nVoice: {name}\nID: {profile['id']}"
            if messagebox.askyesno(tr["install_success_title"], f"{msg}\n\nWould you like to switch to the Speech Studio now?"):
                self.current_speaker_id = profile["id"]
                self.selected_speaker.set(profile["id"])
                self._switch_workspace("synthesis")
        except Exception as e:
            messagebox.showerror("Installation Error", f"Failed to install voice:\n{e}")

    # =========================================================================
    # 3. INSTALLED VOICES LIBRARY WORKSPACE
    # =========================================================================
    def _create_library_workspace(self):
        """Builds visual catalog of all 14+ built-in studio voices and custom installed voices."""
        self.library_frame = ctk.CTkScrollableFrame(self.workspace_frame, fg_color="#181825")

        # Library Filter Pills
        filter_bar = ctk.CTkFrame(self.library_frame, fg_color="#1e1e2e", corner_radius=10)
        filter_bar.pack(fill="x", padx=16, pady=(12, 8))

        flt_inner = ctk.CTkFrame(filter_bar, fg_color="transparent")
        flt_inner.pack(fill="x", padx=12, pady=8)

        self.lib_filter_buttons = {}
        for f_key, f_label_key in (
            ("all", "lib_filter_all"),
            ("custom", "lib_filter_custom"),
            ("male", "lib_filter_male"),
            ("female", "lib_filter_female"),
        ):
            btn = ctk.CTkButton(
                flt_inner,
                text=self.TRANSLATIONS[self.current_lang_code][f_label_key],
                height=30,
                corner_radius=8,
                fg_color="#cba6f7" if f_key == "all" else "#313244",
                text_color="#11111b" if f_key == "all" else "#cdd6f4",
                font=ctk.CTkFont(size=11, weight="bold"),
                command=lambda k=f_key: self._on_library_filter(k),
            )
            btn.pack(side="left", padx=4)
            self.lib_filter_buttons[f_key] = btn

        # Container for voice cards
        self.cards_grid = ctk.CTkFrame(self.library_frame, fg_color="transparent")
        self.cards_grid.pack(fill="both", expand=True, padx=16, pady=6)

    def _on_library_filter(self, filter_key: str):
        for k, b in self.lib_filter_buttons.items():
            if k == filter_key:
                b.configure(fg_color="#cba6f7", text_color="#11111b")
            else:
                b.configure(fg_color="#313244", text_color="#cdd6f4")
        self._refresh_library_cards(filter_key)

    def _refresh_library_cards(self, filter_key: str = "all"):
        """Populates cards grid with all installed voices."""
        for widget in self.cards_grid.winfo_children():
            widget.destroy()

        voices = self.tts_manager.get_all_installed_voices()
        if filter_key != "all":
            if filter_key == "custom":
                voices = [v for v in voices if v.get("is_custom")]
            else:
                voices = [v for v in voices if v.get("gender") == filter_key or v.get("category") == filter_key]

        if not voices:
            empty_lbl = ctk.CTkLabel(
                self.cards_grid,
                text="No voices found in this category. Use the Voice Recording Lab to record and pin custom voices!",
                font=ctk.CTkFont(size=12),
                text_color="#a6adc8",
            )
            empty_lbl.pack(pady=40)
            return

        for v in voices:
            card = ctk.CTkFrame(self.cards_grid, fg_color="#1e1e2e", corner_radius=10)
            card.pack(fill="x", pady=4)
            card.grid_columnconfigure(1, weight=1)

            # Icon / Avatar
            is_custom = v.get("is_custom", False)
            avatar_txt = "⭐" if is_custom else ("👨" if v.get("gender") == "male" else "👩")
            av_lbl = ctk.CTkLabel(card, text=avatar_txt, font=ctk.CTkFont(size=20))
            av_lbl.grid(row=0, column=0, padx=12, pady=10)

            # Voice Name and Info
            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.grid(row=0, column=1, sticky="w", padx=6, pady=8)

            display_name = v.get("display_ar") if self.current_lang_code == "ar" else v.get("display_en")
            v_name_lbl = ctk.CTkLabel(
                info_frame,
                text=display_name or v["name"],
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#cdd6f4",
            )
            v_name_lbl.pack(anchor="w")

            tag_txt = "Custom Voice (Pinned)" if is_custom else f"Studio {v.get('gender', '').capitalize()} Voice"
            v_tag = ctk.CTkLabel(
                info_frame,
                text=tag_txt,
                font=ctk.CTkFont(size=10),
                text_color="#89b4fa" if is_custom else "#a6adc8",
            )
            v_tag.pack(anchor="w")

            # Actions
            btn_box = ctk.CTkFrame(card, fg_color="transparent")
            btn_box.grid(row=0, column=2, padx=12, pady=8, sticky="e")

            # Play Sample
            wav_path = v.get("wav_path")
            if wav_path and os.path.exists(wav_path):
                p_btn = ctk.CTkButton(
                    btn_box,
                    text="▶️ Preview",
                    width=80,
                    height=28,
                    corner_radius=6,
                    fg_color="#313244",
                    hover_color="#45475a",
                    text_color="#a6e3a1",
                    font=ctk.CTkFont(size=10),
                    command=lambda p=wav_path: self._play_audio_file(p),
                )
                p_btn.pack(side="left", padx=4)

            # Use This Voice
            sel_btn = ctk.CTkButton(
                btn_box,
                text="✅ Use Voice",
                width=90,
                height=28,
                corner_radius=6,
                fg_color="#cba6f7",
                hover_color="#b4befe",
                text_color="#11111b",
                font=ctk.CTkFont(size=10, weight="bold"),
                command=lambda vid=v["id"]: self._select_voice_from_library(vid),
            )
            sel_btn.pack(side="left", padx=4)

            # Delete (only for custom voices)
            if is_custom:
                del_btn = ctk.CTkButton(
                    btn_box,
                    text="🗑️",
                    width=32,
                    height=28,
                    corner_radius=6,
                    fg_color="#313244",
                    hover_color="#f38ba8",
                    text_color="#f38ba8",
                    font=ctk.CTkFont(size=11),
                    command=lambda vid=v["id"], n=v["name"]: self._delete_voice_from_library(vid, n),
                )
                del_btn.pack(side="left", padx=4)

    def _play_audio_file(self, filepath: str):
        try:
            self.player.play_audio(filepath)
        except Exception as e:
            messagebox.showerror("Playback Error", f"Failed to play audio:\n{e}")

    def _select_voice_from_library(self, voice_id: str):
        self.current_speaker_id = voice_id
        disp = XTTSEngineManager.get_speaker_display_name(voice_id, self.current_lang_code)
        self.selected_speaker.set(disp)
        self._switch_workspace("synthesis")

    def _delete_voice_from_library(self, voice_id: str, name: str):
        if messagebox.askyesno("Delete Voice", f"Are you sure you want to delete custom voice '{name}'?"):
            self.tts_manager.delete_custom_voice(voice_id)
            self._refresh_voice_selectors()
            self._refresh_library_cards()

    # =========================================================================
    # CORE DISPATCH, LOCALIZATION & GENERATION
    # =========================================================================
    def _refresh_voice_selectors(self):
        """Updates dropdown options in Synthesis Studio with active custom voices."""
        cat_key = XTTSEngineManager.resolve_category_key(self.selected_category.get())
        voices = XTTSEngineManager.get_speaker_options(cat_key, self.current_lang_code)
        self.dropdown_speaker.configure(values=voices)
        if voices:
            current_disp = XTTSEngineManager.get_speaker_display_name(self.current_speaker_id, self.current_lang_code)
            if current_disp in voices:
                self.selected_speaker.set(current_disp)
            else:
                self.selected_speaker.set(voices[0])
                self.current_speaker_id = XTTSEngineManager.resolve_speaker_id(voices[0])

    def _on_category_change(self, selected_cat: str):
        self.current_category_key = XTTSEngineManager.resolve_category_key(selected_cat)
        self._refresh_voice_selectors()

    def _on_speaker_change(self, selected_speaker: str):
        self.current_speaker_id = XTTSEngineManager.resolve_speaker_id(selected_speaker)

    def _on_dsp_change(self, selected_preset: str):
        for k, v in self.TRANSLATIONS[self.current_lang_code]["dsp_presets"].items():
            if v == selected_preset:
                self.current_dsp_preset = k
                break

    def toggle_language(self):
        """Switches UI language between Arabic (RTL) and English (LTR)."""
        new_lang = "en" if self.current_lang_code == "ar" else "ar"
        self._apply_ui_language(new_lang)

    def _apply_ui_language(self, lang_code: str):
        self.current_lang_code = lang_code
        tr = self.TRANSLATIONS[lang_code]

        self.title(tr["window_title"])
        self.btn_tab_synthesis.configure(text=tr["nav_synthesis"])
        self.btn_tab_recorder.configure(text=tr["nav_recorder"])
        self.btn_tab_library.configure(text=tr["nav_library"])
        self.lang_toggle_btn.configure(text=tr["toggle_btn"])
        self.clear_btn.configure(text=tr["clear_btn"])

        # Synthesis labels
        self.lbl_cat.configure(text=tr["category_label"])
        self.lbl_spk.configure(text=tr["speaker_label"])
        self.lbl_lang.configure(text=tr["lang_label"])
        self.lbl_dsp.configure(text=tr["dsp_label"])
        self.welcome_title.configure(text=tr["welcome_title"])
        self.welcome_desc.configure(text=tr["welcome_desc"])
        self.text_entry.configure(placeholder_text=tr["placeholder"])
        self.send_button.configure(text=tr["send_btn"])

        # Category and DSP Dropdowns
        cat_opts = XTTSEngineManager.get_category_options(lang_code)
        self.dropdown_cat.configure(values=cat_opts)
        self.selected_category.set(XTTSEngineManager.get_gender_display_label(self.current_category_key, lang_code))

        dsp_opts = list(tr["dsp_presets"].values())
        self.dropdown_dsp.configure(values=dsp_opts)
        self.selected_dsp_preset.set(tr["dsp_presets"].get(self.current_dsp_preset, dsp_opts[0]))

        # Voice Lab labels
        self.lbl_rec_title.configure(text="🎙️ استوديو التسجيل والفحص الشامل" if lang_code == "ar" else "🎙️ Voice Recording & Diagnostic Lab")
        self.btn_rec_toggle.configure(text=tr["btn_start_rec"])
        self.btn_import_audio.configure(text=tr["btn_import_audio"])
        self.btn_play_rec.configure(text=tr["btn_play_rec"])
        self.lbl_reading_title.configure(text=tr["reading_prompt_title"])
        self.lbl_reading_text.configure(text=tr["reading_prompt_text"])
        self.lbl_diag_header.configure(text=tr["diag_title"])
        self.btn_run_diag.configure(text=tr["diag_btn_run"])
        self.lbl_install_hdr.configure(text=tr["install_title"])
        self.entry_voice_name.configure(placeholder_text=tr["install_name_placeholder"])
        self.dropdown_install_gender.configure(values=[tr["install_gender_male"], tr["install_gender_female"]])
        self.btn_install_voice.configure(text=tr["install_btn"])

        # Update diagnostic test titles
        for t_id, card in self.test_cards.items():
            t_txt = card["title_ar"] if lang_code == "ar" else card["title_en"]
            card["title_lbl"].configure(text=t_txt)
            if card.get("play_btn"):
                btn_txt = tr["play_test_ar"] if t_id == "arabic" else tr["play_test_en"]
                card["play_btn"].configure(text=btn_txt)

        self._refresh_voice_selectors()
        if self.current_tab == "library":
            self._refresh_library_cards()

    def clear_chat(self):
        """Clears chat bubbles from synthesis history."""
        self.player.stop_audio()
        for b in list(self.chat_bubbles):
            try:
                b.destroy()
            except Exception:
                pass
        self.chat_bubbles.clear()

    def _initialize_models_async(self):
        """Pre-loads speech model on background thread."""
        def on_ready():
            self.after(0, self._on_models_ready)

        self.tts_manager.initialize_active_engine_async(on_ready=on_ready)

    def _on_models_ready(self):
        tr = self.TRANSLATIONS[self.current_lang_code]
        dev_label = self.tts_manager.get_active_device_label()
        self.hardware_pill.configure(
            text=f"● Neural Core Active • {dev_label} • {tr['ready_suffix']}",
            text_color="#a6e3a1",
        )

    def send_message(self, event=None):
        """Synthesizes speech for the entered text."""
        if self.is_processing:
            return

        text = self.text_entry.get().strip()
        if not text:
            return

        # Determine target speech language
        sl_name = self.selected_speech_lang.get().lower()
        if "عرب" in sl_name:
            lang_code = "ar"
        elif "span" in sl_name or "esp" in sl_name:
            lang_code = "es"
        elif "fran" in sl_name:
            lang_code = "fr"
        elif "deut" in sl_name or "germ" in sl_name:
            lang_code = "de"
        elif "ital" in sl_name:
            lang_code = "it"
        elif "turk" in sl_name:
            lang_code = "tr"
        else:
            lang_code = "en"

        is_rtl = lang_code == "ar"
        speaker_id = self.current_speaker_id

        self.text_entry.delete(0, "end")
        self.is_processing = True

        # Render User text bubble
        user_bubble = UserChatBubble(
            self.chat_container,
            text=text,
            is_rtl=is_rtl,
            ui_lang=self.current_lang_code,
        )
        user_bubble.pack(fill="x", padx=20, pady=6)
        self.chat_bubbles.append(user_bubble)

        # Loading animation bubble
        init_status = self.TRANSLATIONS[self.current_lang_code]["status_analyzing"]
        self.active_loading_bubble = LoadingChatBubble(self.chat_container, initial_text=init_status, is_rtl=is_rtl)
        self.active_loading_bubble.pack(fill="x", padx=20, pady=6)

        self._scroll_to_bottom()

        def worker():
            def progress(c_idx, total_c, chunk_txt):
                pct = int((c_idx / float(total_c)) * 100)
                tr = self.TRANSLATIONS[self.current_lang_code]
                status_str = tr["status_chunk_fmt"].format(idx=c_idx, total=total_c, pct=pct)
                if self.active_loading_bubble:
                    self.active_loading_bubble.update_status(status_str)

            try:
                res = self.tts_manager.generate_speech(
                    text=text,
                    language=lang_code,
                    speaker_or_instruct=speaker_id,
                    speed=1.0,
                    dsp_preset=self.current_dsp_preset,
                    progress_callback=progress,
                )
                self.after(0, lambda: self._on_generation_success(res))
            except Exception as e:
                err = str(e)
                self.after(0, lambda: self._on_generation_error(err))

        threading.Thread(target=worker, daemon=True).start()

    def _on_generation_success(self, result: dict):
        if self.active_loading_bubble:
            self.active_loading_bubble.destroy()
            self.active_loading_bubble = None

        ai_bubble = AIChatBubble(
            self.chat_container,
            text=result["text"],
            audio_filepath=result.get("output_path") or result.get("filepath"),
            duration=result["duration"],
            speaker=result["speaker"],
            language=result["language"],
            ui_lang=self.current_lang_code,
            engine="Voice Studio Neural Core",
        )
        ai_bubble.pack(fill="x", padx=20, pady=6)
        self.chat_bubbles.append(ai_bubble)

        self.is_processing = False
        self._scroll_to_bottom()

    def _on_generation_error(self, err_msg: str):
        if self.active_loading_bubble:
            self.active_loading_bubble.destroy()
            self.active_loading_bubble = None

        self.is_processing = False
        tr = self.TRANSLATIONS[self.current_lang_code]
        messagebox.showerror(tr["error_title"], f"{tr['error_prefix']}{err_msg}")

    def _scroll_to_bottom(self):
        self.after(100, lambda: self.chat_container._parent_canvas.yview_moveto(1.0))
