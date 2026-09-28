"""
chat_bubble.py - RTL & LTR Adaptive Studio Cards
------------------------------------------------
Renders styled dark-mode cards with Right-to-Left (RTL) alignment for Arabic
and Left-to-Right (LTR) for English, supporting dynamic UI localization.
"""

import time
import customtkinter as ctk
from gui.audio_widget import EmbeddedAudioWidget
from xtts_engine import XTTSEngineManager


class UserChatBubble(ctk.CTkFrame):
    """User input text card with RTL / LTR layout support and dynamic UI localization."""

    def __init__(
        self,
        master,
        text: str,
        is_rtl: bool = True,
        timestamp: str = None,
        ui_lang: str = None,
        **kwargs,
    ):
        super().__init__(
            master,
            fg_color="#313244",
            corner_radius=14,
            border_width=1,
            border_color="#45475a",
            **kwargs,
        )

        self.timestamp = timestamp or time.strftime("%H:%M")
        self.is_rtl = is_rtl
        self.ui_lang = ui_lang or ("ar" if is_rtl else "en")
        self.grid_columnconfigure(0, weight=1)

        anchor_pos = "e" if is_rtl else "w"
        align_text = "right" if is_rtl else "left"

        self.header_label = ctk.CTkLabel(
            self,
            text=self._get_header_text(),
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#89b4fa",
            anchor=anchor_pos,
        )
        self.header_label.grid(row=0, column=0, padx=12, pady=(8, 2), sticky="ew")

        self.msg_label = ctk.CTkLabel(
            self,
            text=text,
            font=ctk.CTkFont(size=14 if is_rtl else 13),
            text_color="#cdd6f4",
            anchor=anchor_pos,
            justify=align_text,
            wraplength=620,
        )
        self.msg_label.grid(row=1, column=0, padx=12, pady=(0, 10), sticky="ew")

    def _get_header_text(self) -> str:
        if self.ui_lang == "ar":
            return f"النص • {self.timestamp}"
        return f"Text • {self.timestamp}"

    def update_ui_language(self, ui_lang: str):
        """Updates card header label when UI language switches."""
        self.ui_lang = "en" if ui_lang == "en" else "ar"
        self.header_label.configure(text=self._get_header_text())


class AIChatBubble(ctk.CTkFrame):
    """Generated audio card with RTL/LTR text alignment and embedded Audio Widget."""

    def __init__(
        self,
        master,
        text: str,
        audio_filepath: str,
        duration: float,
        speaker: str = "",
        language: str = "ar",
        timestamp: str = None,
        ui_lang: str = None,
        **kwargs,
    ):
        super().__init__(
            master,
            fg_color="#181825",
            corner_radius=14,
            border_width=1,
            border_color="#cba6f7",
            **kwargs,
        )

        self.timestamp = timestamp or time.strftime("%H:%M")
        self.language = language
        self.speaker = speaker
        self.speaker_id = XTTSEngineManager.resolve_speaker_id(speaker) if speaker else ""
        self.ui_lang = ui_lang or language
        self.is_rtl = language == "ar"
        anchor_pos = "e" if self.is_rtl else "w"
        align_text = "right" if self.is_rtl else "left"

        self.grid_columnconfigure(0, weight=1)

        self.header_label = ctk.CTkLabel(
            self,
            text=self._get_header_text(),
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#cba6f7",
            anchor=anchor_pos,
        )
        self.header_label.grid(row=0, column=0, padx=12, pady=(8, 2), sticky="ew")

        self.msg_label = ctk.CTkLabel(
            self,
            text=text,
            font=ctk.CTkFont(size=14 if self.is_rtl else 13),
            text_color="#cdd6f4",
            anchor=anchor_pos,
            justify=align_text,
            wraplength=620,
        )
        self.msg_label.grid(row=1, column=0, padx=12, pady=(0, 8), sticky="ew")

        self.audio_widget = EmbeddedAudioWidget(
            self,
            filepath=audio_filepath,
            duration=duration,
            speaker=speaker,
            language=language,
            ui_lang=self.ui_lang,
        )
        self.audio_widget.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="ew")

    def _get_header_text(self) -> str:
        localized_speaker = (
            XTTSEngineManager.get_speaker_display_name(
                self.speaker_id or self.speaker, self.ui_lang
            )
            if self.speaker
            else ""
        )
        if self.ui_lang == "ar":
            return f"المقطع الصوتي ({localized_speaker}) • {self.timestamp}"
        return f"Audio Output ({localized_speaker}) • {self.timestamp}"

    def update_ui_language(self, ui_lang: str):
        """Updates card header and embedded audio widget when UI language switches."""
        self.ui_lang = "en" if ui_lang == "en" else "ar"
        self.header_label.configure(text=self._get_header_text())
        if hasattr(self, "audio_widget") and self.audio_widget:
            self.audio_widget.update_ui_language(self.ui_lang)


class LoadingChatBubble(ctk.CTkFrame):
    """Loading status card with real-time chunk synthesis progress updates."""

    def __init__(
        self,
        master,
        initial_text: str = None,
        text: str = None,
        is_rtl: bool = True,
        **kwargs,
    ):
        super().__init__(
            master,
            fg_color="#181825",
            corner_radius=12,
            border_width=1,
            border_color="#fab387",
            **kwargs,
        )

        display_str = initial_text or text or ("جاري توليد الصوت..." if is_rtl else "Generating audio...")
        self.is_rtl = is_rtl
        anchor_pos = "e" if is_rtl else "w"

        self.label = ctk.CTkLabel(
            self,
            text=display_str,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#fab387",
            anchor=anchor_pos,
        )
        self.label.grid(row=0, column=0, padx=14, pady=10, sticky="ew")

    def update_status(self, text: str):
        """Updates the status label text on main thread."""
        self.after(0, lambda: self.label.configure(text=text))
