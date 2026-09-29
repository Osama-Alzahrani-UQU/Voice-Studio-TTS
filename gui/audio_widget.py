"""
audio_widget.py - Embedded Audio Player Widget
----------------------------------------------
Interactive widget embedded inside audio response cards with Play/Pause
controls, dynamic Arabic/English UI localization, and WAV export.
"""

import os
import shutil
import customtkinter as ctk
from tkinter import filedialog, messagebox
from audio_player import AudioPlayerController
from xtts_engine import EXPORTS_DIR, XTTSEngineManager


class EmbeddedAudioWidget(ctk.CTkFrame):
    """
    Audio player widget embedded inside generated audio cards.
    """

    def __init__(
        self,
        master,
        filepath: str,
        duration: float,
        speaker: str = "",
        language: str = "ar",
        ui_lang: str = None,
        engine: str = "xtts",
        **kwargs,
    ):
        super().__init__(
            master,
            fg_color="#1e1e2e",
            corner_radius=10,
            border_width=1,
            border_color="#313244",
            **kwargs,
        )

        self.filepath = filepath
        self.duration = duration
        self.speaker = speaker
        self.engine = engine or "xtts"
        self.speaker_id = XTTSEngineManager.resolve_speaker_id(speaker) if speaker and self.engine != "omnivoice" else ""
        self.language = language
        self.ui_lang = ui_lang or language
        self.is_playing = False
        self.audio_player = AudioPlayerController()

        self.grid_columnconfigure(1, weight=1)

        self.play_btn = ctk.CTkButton(
            self,
            text=self._get_play_text(),
            width=95,
            height=32,
            corner_radius=8,
            fg_color="#89b4fa",
            text_color="#11111b",
            hover_color="#b4befe",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.toggle_playback,
        )
        self.play_btn.grid(row=0, column=0, padx=(10, 5), pady=8, sticky="w")

        self.info_label = ctk.CTkLabel(
            self,
            text=self._get_info_text(),
            font=ctk.CTkFont(size=12),
            text_color="#cdd6f4",
            anchor="e" if self.ui_lang == "ar" else "w",
        )
        self.info_label.grid(row=0, column=1, padx=5, pady=8, sticky="ew")

        self.save_btn = ctk.CTkButton(
            self,
            text="Save WAV" if self.ui_lang == "en" else "حفظ WAV",
            width=100,
            height=32,
            corner_radius=8,
            fg_color="#313244",
            text_color="#cdd6f4",
            hover_color="#45475a",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.export_wav,
        )
        self.save_btn.grid(row=0, column=2, padx=(5, 10), pady=8, sticky="e")

    def _get_play_text(self) -> str:
        if self.is_playing:
            return "⏸ Pause" if self.ui_lang == "en" else "⏸ إيقاف"
        return "▶ Play" if self.ui_lang == "en" else "▶ تشغيل"

    def _get_info_text(self) -> str:
        unit = "s" if self.ui_lang == "en" else " ث"
        engine_badge = "[OmniVoice]" if self.engine == "omnivoice" else "[XTTS v2]"
        info_text = f"{engine_badge}  {self.duration:.1f}{unit}"
        if self.speaker:
            if self.engine == "omnivoice" or "," in self.speaker:
                info_text += f"  •  {self.speaker}"
            else:
                localized_speaker = XTTSEngineManager.get_speaker_display_name(
                    self.speaker_id or self.speaker, self.ui_lang
                )
                info_text += f"  •  {localized_speaker}"
        return info_text

    def update_ui_language(self, ui_lang: str):
        """Updates button and info labels when the user switches the app UI language."""
        self.ui_lang = "en" if ui_lang == "en" else "ar"
        self.play_btn.configure(text=self._get_play_text())
        self.info_label.configure(
            text=self._get_info_text(),
            anchor="e" if self.ui_lang == "ar" else "w",
        )
        self.save_btn.configure(
            text="Save WAV" if self.ui_lang == "en" else "حفظ WAV"
        )

    def toggle_playback(self):
        """Toggles audio playback."""
        try:
            state = self.audio_player.toggle_play_pause(
                self.filepath, widget_owner=self, on_finish=self.reset_play_button
            )
            self.is_playing = state == "PLAYING"
            if self.is_playing:
                self.play_btn.configure(text=self._get_play_text(), fg_color="#f38ba8")
            else:
                self.play_btn.configure(text=self._get_play_text(), fg_color="#89b4fa")
        except Exception as e:
            err_title = "Error" if self.ui_lang == "en" else "خطأ في التشغيل"
            err_msg = (
                f"Could not play audio:\n{e}"
                if self.ui_lang == "en"
                else f"تعذر تشغيل الملف الصوتي:\n{e}"
            )
            messagebox.showerror(err_title, err_msg)
            self.reset_play_button()

    def reset_play_button(self):
        """Resets the play button when audio finishes."""
        self.is_playing = False
        self.after(
            0,
            lambda: self.play_btn.configure(
                text=self._get_play_text(), fg_color="#89b4fa"
            ),
        )

    def export_wav(self):
        """Opens file dialog to export the generated WAV file."""
        if not os.path.exists(self.filepath):
            err_title = "Error" if self.ui_lang == "en" else "خطأ"
            err_msg = (
                "The original audio file is missing."
                if self.ui_lang == "en"
                else "الملف الصوتي الأصلي غير موجود."
            )
            messagebox.showerror(err_title, err_msg)
            return

        os.makedirs(EXPORTS_DIR, exist_ok=True)
        default_name = os.path.basename(self.filepath)
        dlg_title = (
            "Save Audio WAV File"
            if self.ui_lang == "en"
            else "حفظ الملف الصوتي بصيغة WAV"
        )

        target_path = filedialog.asksaveasfilename(
            title=dlg_title,
            initialdir=EXPORTS_DIR,
            initialfile=default_name,
            defaultextension=".wav",
            filetypes=[("WAVE Audio", "*.wav"), ("All Files", "*.*")],
        )

        if target_path:
            try:
                shutil.copy2(self.filepath, target_path)
                ok_title = "Saved" if self.ui_lang == "en" else "تم الحفظ"
                ok_msg = (
                    f"Audio exported successfully:\n{target_path}"
                    if self.ui_lang == "en"
                    else f"تم حفظ الملف الصوتي بنجاح:\n{target_path}"
                )
                messagebox.showinfo(ok_title, ok_msg)
            except Exception as e:
                err_title = "Save Error" if self.ui_lang == "en" else "خطأ أثناء الحفظ"
                err_msg = (
                    f"Failed to save audio file:\n{e}"
                    if self.ui_lang == "en"
                    else f"فشل حفظ الملف الصوتي:\n{e}"
                )
                messagebox.showerror(err_title, err_msg)
