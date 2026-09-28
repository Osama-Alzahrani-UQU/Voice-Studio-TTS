"""
main_window.py - Voice Studio Main Application Window
-----------------------------------------------------
CustomTkinter desktop GUI window featuring sleek studio aesthetics, dynamic
Arabic (RTL) <-> English (LTR) interface & menu localization, studio voice selection,
and real-time speech synthesis progress tracking.
"""

import os
import sys
import threading
import customtkinter as ctk
from PIL import Image
from tkinter import messagebox

from xtts_engine import XTTSEngineManager, BASE_APP_DIR
from audio_player import AudioPlayerController
from gui.chat_bubble import UserChatBubble, AIChatBubble, LoadingChatBubble

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class XTTSArabicEnglishChatApp(ctk.CTk):
    """
    Main application window for Arabic & English speech synthesis
    with full bidirectional Arabic <-> English menu and UI localization.
    """

    TRANSLATIONS = {
        "ar": {
            "window_title": "استوديو الصوت | Voice Studio",
            "studio_title": "استوديو الصوت",
            "lang_label": "اللغة:",
            "toggle_btn": "English ⇄",
            "gender_label": "الفئة:",
            "speaker_label": "الصوت:",
            "clear_btn": "مسح",
            "welcome_title": "تحويل النص إلى كلام",
            "welcome_desc": "اختر الفئة والصوت من الشريط العلوي، ثم اكتب النص بالأسفل لتوليد المقطع الصوتي.",
            "placeholder": "اكتب النص هنا لتحويله إلى مقطع صوتي...",
            "send_btn": "توليد الصوت",
            "status_analyzing": "جاري معالجة النص...",
            "status_chunk_fmt": "جاري توليد المقطع {idx} من {total} ({pct}%)...",
            "error_title": "خطأ في التوليد",
            "error_prefix": "تعذر توليد المقطع الصوتي:\n",
            "ready_suffix": "جاهز",
        },
        "en": {
            "window_title": "Voice Studio",
            "studio_title": "Voice Studio",
            "lang_label": "Language:",
            "toggle_btn": "العربية ⇄",
            "gender_label": "Category:",
            "speaker_label": "Voice:",
            "clear_btn": "Clear",
            "welcome_title": "Text-to-Speech Studio",
            "welcome_desc": "Select a voice profile from the top toolbar and enter your text below to generate audio.",
            "placeholder": "Enter your text here to generate speech...",
            "send_btn": "Generate",
            "status_analyzing": "Processing text...",
            "status_chunk_fmt": "Generating segment {idx} of {total} ({pct}%)...",
            "error_title": "Generation Error",
            "error_prefix": "Failed to generate audio:\n",
            "ready_suffix": "Ready",
        },
    }

    def __init__(self):
        super().__init__()

        self.geometry("1060x740")
        self.minsize(880, 600)

        self.engine_manager = XTTSEngineManager()

        # UI State variables
        self.current_lang_code = "ar"
        self.current_gender_key = "male"
        self.current_speaker_id = "Damien_Black"

        self.selected_lang_label = ctk.StringVar(value="العربية")
        self.selected_gender = ctk.StringVar(
            value=XTTSEngineManager.get_gender_display_label("male", "ar")
        )
        self.selected_speaker = ctk.StringVar(
            value=XTTSEngineManager.get_speaker_display_name("Damien_Black", "ar")
        )
        self.is_processing = False
        self.active_loading_bubble = None
        self.chat_bubbles = []

        # Build Main UI Components
        self._create_header_frame()
        self._create_chat_frame()
        self._create_input_frame()

        # Apply initial language across all widgets
        self._apply_ui_language("ar")

        # Start async model initialization
        self._initialize_model_async()

    def _get_assets_dir(self) -> str:
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            bundled = os.path.join(sys._MEIPASS, "assets")
            if os.path.exists(bundled):
                return bundled
        return os.path.join(BASE_APP_DIR, "assets")

    def _create_header_frame(self):
        """Top menu bar featuring language switchers and voice controls."""
        top_container = ctk.CTkFrame(self, fg_color="#181825", corner_radius=0)
        top_container.pack(side="top", fill="x", padx=0, pady=0)

        header = ctk.CTkFrame(top_container, fg_color="#1e1e2e", height=58, corner_radius=0)
        header.pack(side="top", fill="x", padx=0, pady=0)
        header.grid_columnconfigure(1, weight=1)

        # Studio Title Label
        self.title_label = ctk.CTkLabel(
            header,
            text="استوديو الصوت",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#cba6f7",
        )
        self.title_label.grid(row=0, column=0, padx=(18, 8), pady=12, sticky="w")

        # Minimal Engine Status Badge
        badges_frame = ctk.CTkFrame(header, fg_color="transparent")
        badges_frame.grid(row=0, column=1, padx=4, pady=12, sticky="w")

        badge_color = "#a6e3a1" if self.engine_manager.device == "cuda" else "#89b4fa"
        self.hardware_badge = ctk.CTkLabel(
            badges_frame,
            text=f"● {self.engine_manager.device_label}",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=badge_color,
            fg_color="#313244",
            corner_radius=6,
            padx=10,
            pady=4,
        )
        self.hardware_badge.pack(side="left")

        # Controls Container (Right Aligned Menu)
        controls_frame = ctk.CTkFrame(header, fg_color="transparent")
        controls_frame.grid(row=0, column=2, padx=16, pady=12, sticky="e")

        # Language Dropdown Label
        self.lang_label = ctk.CTkLabel(
            controls_frame,
            text="اللغة:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#cdd6f4",
        )
        self.lang_label.pack(side="left", padx=(0, 4))

        # Language Dropdown Menu (Arabic <-> English)
        self.lang_dropdown = ctk.CTkOptionMenu(
            controls_frame,
            values=XTTSEngineManager.LANGUAGE_MENU_ITEMS,
            variable=self.selected_lang_label,
            width=110,
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

        # Quick One-Click Language Switch Button (عربي ⇄ English)
        self.lang_toggle_btn = ctk.CTkButton(
            controls_frame,
            text="English ⇄",
            width=96,
            height=32,
            corner_radius=8,
            fg_color="#cba6f7",
            text_color="#11111b",
            hover_color="#b4befe",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.toggle_language,
        )
        self.lang_toggle_btn.pack(side="left", padx=(0, 12))

        # Speaker Gender Dropdown
        self.gender_label = ctk.CTkLabel(
            controls_frame,
            text="الفئة:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#cdd6f4",
        )
        self.gender_label.pack(side="left", padx=(0, 4))

        self.gender_dropdown = ctk.CTkOptionMenu(
            controls_frame,
            values=XTTSEngineManager.get_gender_options("ar"),
            variable=self.selected_gender,
            width=130,
            height=32,
            fg_color="#313244",
            button_color="#45475a",
            button_hover_color="#585b70",
            dropdown_fg_color="#1e1e2e",
            text_color="#cdd6f4",
            font=ctk.CTkFont(size=11),
            command=self._on_gender_change,
        )
        self.gender_dropdown.pack(side="left", padx=(0, 10))

        # Speaker Voice Dropdown
        self.speaker_label = ctk.CTkLabel(
            controls_frame,
            text="الصوت:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#cdd6f4",
        )
        self.speaker_label.pack(side="left", padx=(0, 4))

        self.speaker_dropdown = ctk.CTkOptionMenu(
            controls_frame,
            values=XTTSEngineManager.get_speaker_options("male", "ar"),
            variable=self.selected_speaker,
            width=195,
            height=32,
            fg_color="#313244",
            button_color="#45475a",
            button_hover_color="#585b70",
            dropdown_fg_color="#1e1e2e",
            text_color="#cdd6f4",
            font=ctk.CTkFont(size=11),
            command=self._on_speaker_change,
        )
        self.speaker_dropdown.pack(side="left", padx=(0, 8))

        # Clear Button
        self.clear_btn = ctk.CTkButton(
            controls_frame,
            text="مسح",
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
            justify="right",
        )
        self.welcome_desc.pack(fill="x", padx=16, pady=(0, 12))

    def _create_input_frame(self):
        """Bottom text entry bar and generate button."""
        input_container = ctk.CTkFrame(self, fg_color="#181825", height=85, corner_radius=0)
        input_container.pack(side="bottom", fill="x", padx=0, pady=0)
        input_container.pack_propagate(False)

        input_container.grid_columnconfigure(0, weight=1)

        self.text_entry = ctk.CTkEntry(
            input_container,
            placeholder_text=self.TRANSLATIONS["ar"]["placeholder"],
            height=46,
            corner_radius=10,
            fg_color="#313244",
            text_color="#cdd6f4",
            placeholder_text_color="#6c7086",
            border_color="#45475a",
            font=ctk.CTkFont(size=14),
            justify="right",
        )
        self.text_entry.grid(row=0, column=0, padx=(16, 10), pady=18, sticky="ew")
        self.text_entry.bind("<Return>", lambda event: self.send_message())

        self.send_button = ctk.CTkButton(
            input_container,
            text=self.TRANSLATIONS["ar"]["send_btn"],
            width=115,
            height=46,
            corner_radius=10,
            fg_color="#cba6f7",
            text_color="#11111b",
            hover_color="#b4befe",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.send_message,
        )
        self.send_button.grid(row=0, column=1, padx=(0, 16), pady=18, sticky="e")

    def _get_current_lang_code(self) -> str:
        """Returns 'ar' or 'en' cleanly based on current selection."""
        val = self.selected_lang_label.get()
        if "English" in val or val.strip().lower() == "en":
            return "en"
        return "ar"

    def toggle_language(self):
        """Switches the application language from Arabic to English and vice versa."""
        if self.is_processing:
            return
        new_lang = "en" if self.current_lang_code == "ar" else "ar"
        new_label = "English" if new_lang == "en" else "العربية"
        self.selected_lang_label.set(new_label)
        self._apply_ui_language(new_lang)

    def _on_language_change(self, choice: str):
        """Handles language selection from the menu dropdown."""
        lang_code = "en" if ("English" in choice or choice.strip().lower() == "en") else "ar"
        self._apply_ui_language(lang_code)

    def _apply_ui_language(self, lang_code: str):
        """Applies full Arabic or English localization across the entire window, menu, and cards."""
        lang = "en" if lang_code == "en" else "ar"
        self.current_lang_code = lang
        tr = self.TRANSLATIONS[lang]

        expected_dropdown_val = "English" if lang == "en" else "العربية"
        if self.selected_lang_label.get() != expected_dropdown_val:
            self.selected_lang_label.set(expected_dropdown_val)

        # 1. Window & Header Titles
        self.title(tr["window_title"])
        self.title_label.configure(text=tr["studio_title"])
        self._refresh_hardware_badge()

        # 2. Menu Controls & Toggle Button
        self.lang_label.configure(text=tr["lang_label"])
        self.lang_toggle_btn.configure(text=tr["toggle_btn"])
        self.gender_label.configure(text=tr["gender_label"])
        self.speaker_label.configure(text=tr["speaker_label"])
        self.clear_btn.configure(text=tr["clear_btn"])

        # 3. Localize Gender Options while preserving selected gender key ('male' or 'female')
        gender_options = XTTSEngineManager.get_gender_options(lang)
        self.gender_dropdown.configure(values=gender_options)
        self.selected_gender.set(
            XTTSEngineManager.get_gender_display_label(self.current_gender_key, lang)
        )

        # 4. Localize Speaker Options while preserving selected speaker ID
        speaker_options = XTTSEngineManager.get_speaker_options(self.current_gender_key, lang)
        self.speaker_dropdown.configure(values=speaker_options)
        localized_speaker = XTTSEngineManager.get_speaker_display_name(self.current_speaker_id, lang)
        if localized_speaker in speaker_options:
            self.selected_speaker.set(localized_speaker)
        elif speaker_options:
            self.selected_speaker.set(speaker_options[0])
            self.current_speaker_id = XTTSEngineManager.resolve_speaker_id(speaker_options[0])

        # 5. Welcome Card Localization & Alignment
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

        # 6. Bottom Text Input & Send Button
        self.text_entry.configure(
            placeholder_text=tr["placeholder"],
            justify="right" if is_rtl else "left",
        )
        self.send_button.configure(text=tr["send_btn"])

        # 7. Update all existing cards & audio widgets
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
        """Tracks the canonical speaker ID when the user picks a voice."""
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

    def _initialize_model_async(self):
        """Pre-loads the XTTS model on a background thread."""
        def task():
            try:
                self.engine_manager.initialize()
                self.after(0, self._on_model_loaded_ready)
            except Exception as e:
                print(f"[Main Window] Engine load exception: {e}")

        thread = threading.Thread(target=task, daemon=True)
        thread.start()

    def _refresh_hardware_badge(self):
        """Updates hardware badge text in the active UI language."""
        if not hasattr(self, "hardware_badge"):
            return
        tr = self.TRANSLATIONS[self.current_lang_code]
        if self.engine_manager.is_ready:
            self.hardware_badge.configure(
                text=f"● {self.engine_manager.device_label} • {tr['ready_suffix']}",
                text_color="#a6e3a1",
            )
        else:
            badge_color = "#a6e3a1" if self.engine_manager.device == "cuda" else "#89b4fa"
            self.hardware_badge.configure(
                text=f"● {self.engine_manager.device_label}",
                text_color=badge_color,
            )

    def _on_model_loaded_ready(self):
        """Updates badge when engine is ready."""
        self._refresh_hardware_badge()

    def send_message(self, event=None):
        """Captures long-form text input and starts async audio generation."""
        if self.is_processing:
            return

        text = self.text_entry.get().strip()
        if not text:
            return

        lang_code = self._get_current_lang_code()
        is_rtl = lang_code == "ar"
        speaker = self.selected_speaker.get()
        self.current_speaker_id = XTTSEngineManager.resolve_speaker_id(speaker)

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

        initial_status = self.TRANSLATIONS[lang_code]["status_analyzing"]
        self.active_loading_bubble = LoadingChatBubble(
            self.chat_container, initial_text=initial_status, is_rtl=is_rtl
        )
        self.active_loading_bubble.pack(fill="x", padx=20, pady=6)

        self._scroll_to_bottom()

        thread = threading.Thread(
            target=self._run_generation_thread,
            args=(text, lang_code, speaker),
            daemon=True,
        )
        thread.start()

    def _run_generation_thread(self, text: str, lang_code: str, speaker: str):
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
            result = self.engine_manager.generate_long_speech(
                text=text,
                language=lang_code,
                speaker=speaker,
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
        self.lang_dropdown.configure(state=state)
        self.lang_toggle_btn.configure(state=state)
        self.gender_dropdown.configure(state=state)
        self.speaker_dropdown.configure(state=state)
        self.clear_btn.configure(state=state)

    def _scroll_to_bottom(self):
        """Scrolls workspace to bottom."""
        self.after(100, lambda: self.chat_container._parent_canvas.yview_moveto(1.0))
