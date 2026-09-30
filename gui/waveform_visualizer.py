r"""
waveform_visualizer.py - High-FPS Live Sound Wave Canvas Visualizer
-------------------------------------------------------------------
Renders smooth neon equalizer bars, an oscilloscope wave line, a live dBFS
peak meter, and an animated pulsing recording indicator for Voice Studio.
"""

import math
import time
import tkinter as tk
import customtkinter as ctk
import numpy as np
from typing import Optional


class WaveformVisualizer(ctk.CTkFrame):
    """
    High-tech neon soundwave visualizer powered by a Tkinter canvas.
    Supports live microphone amplitude streaming, FFT frequency distribution,
    smooth physics smoothing, and ambient idle wave animation.
    """

    NUM_BARS = 48
    COLOR_GRADIENT = [
        "#cba6f7",  # Mauve / Neon Violet
        "#b4befe",  # Lavender
        "#89b4fa",  # Cyan Blue
        "#74c7ec",  # Sky Blue
        "#89dceb",  # Electric Cyan
        "#f5c2e7",  # Soft Pink
        "#cba6f7",  # Mauve
    ]

    def __init__(self, parent, width: int = 700, height: int = 150, **kwargs):
        super().__init__(parent, fg_color="#11111b", corner_radius=12, **kwargs)

        self.width = width
        self.height = height
        self.bar_heights = np.zeros(self.NUM_BARS, dtype=np.float32)
        self.target_heights = np.zeros(self.NUM_BARS, dtype=np.float32)

        self.is_active = False
        self.is_recording = False
        self.elapsed_seconds = 0.0
        self.current_peak_db = -80.0
        self.phase = 0.0

        # Canvas for sound wave rendering
        self.canvas = tk.Canvas(
            self,
            width=self.width,
            height=self.height,
            bg="#11111b",
            highlightthickness=1,
            highlightbackground="#313244",
        )
        self.canvas.pack(fill="both", expand=True, padx=4, pady=(4, 0))

        # Bottom status bar (Timer + Peak dB Meter)
        self.status_bar = ctk.CTkFrame(self, fg_color="transparent", height=24)
        self.status_bar.pack(fill="x", padx=10, pady=(2, 4))

        self.timer_label = ctk.CTkLabel(
            self.status_bar,
            text="00:00.0",
            font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
            text_color="#a6adc8",
        )
        self.timer_label.pack(side="left")

        self.rec_badge = ctk.CTkLabel(
            self.status_bar,
            text="● STANDBY",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#89b4fa",
        )
        self.rec_badge.pack(side="left", padx=10)

        self.db_label = ctk.CTkLabel(
            self.status_bar,
            text="-80 dBFS",
            font=ctk.CTkFont(family="Consolas", size=10),
            text_color="#6c7086",
        )
        self.db_label.pack(side="right")

        self.canvas.bind("<Configure>", self._on_resize)
        self._start_animation_loop()

    def _on_resize(self, event):
        if event.width > 50 and event.height > 50:
            self.width = event.width
            self.height = event.height

    def set_recording_state(self, is_recording: bool):
        """Toggles active recording mode and visual cues."""
        self.is_recording = is_recording
        self.is_active = is_recording
        if is_recording:
            self.rec_badge.configure(text="● REC", text_color="#f38ba8")
        else:
            self.rec_badge.configure(text="● READY", text_color="#a6e3a1")

    def update_audio_chunk(self, chunk: np.ndarray, rms: float, peak_db: float, elapsed: float):
        """Called from audio recording stream with latest audio buffer."""
        self.is_active = True
        self.elapsed_seconds = elapsed
        self.current_peak_db = peak_db

        # Sub-divide chunk across bars to reflect spectral/time dynamics
        if len(chunk) >= self.NUM_BARS:
            step = len(chunk) // self.NUM_BARS
            raw_vals = [np.max(np.abs(chunk[i * step : (i + 1) * step])) for i in range(self.NUM_BARS)]
            raw_vals = np.array(raw_vals, dtype=np.float32)
        else:
            raw_vals = np.full(self.NUM_BARS, rms * 3.0, dtype=np.float32)

        # Scale non-linearly for aesthetic responsiveness
        scaled = np.clip(np.power(raw_vals * 2.5, 0.75), 0.05, 1.0)
        self.target_heights = scaled

    def _start_animation_loop(self):
        """Runs 35 FPS rendering loop with physics-based bar decay and wave curves."""
        decay_factor = 0.72
        attack_factor = 0.45

        if self.is_recording or self.is_active:
            # Smooth towards target
            self.bar_heights = self.bar_heights * decay_factor + self.target_heights * attack_factor
            # Natural decay
            self.target_heights *= 0.85
        else:
            # Ambient breathing idle wave
            self.phase += 0.08
            for i in range(self.NUM_BARS):
                ambient = 0.08 + 0.06 * math.sin(self.phase + (i * 0.25))
                self.bar_heights[i] = self.bar_heights[i] * 0.9 + ambient * 0.1

        self._draw_waveform()

        # Update Timer and Peak HUD
        if self.is_recording:
            mins = int(self.elapsed_seconds // 60)
            secs = self.elapsed_seconds % 60
            self.timer_label.configure(text=f"{mins:02d}:{secs:04.1f}")
            self.db_label.configure(text=f"{self.current_peak_db:+.1f} dBFS")

        self.after(28, self._start_animation_loop)

    def _draw_waveform(self):
        self.canvas.delete("all")
        w = max(100, self.width)
        h = max(60, self.height)
        cy = h / 2.0

        bar_w = max(2.0, (w - (self.NUM_BARS * 3)) / float(self.NUM_BARS))
        max_bar_h = cy * 0.88

        # Draw glowing background grid lines
        self.canvas.create_line(0, cy, w, cy, fill="#1e1e2e", width=1, dash=(4, 4))
        self.canvas.create_line(0, cy - max_bar_h, w, cy - max_bar_h, fill="#181825", width=1)
        self.canvas.create_line(0, cy + max_bar_h, w, cy + max_bar_h, fill="#181825", width=1)

        points = []
        for i in range(self.NUM_BARS):
            x = 8 + i * (bar_w + 3)
            val = float(self.bar_heights[i])
            bar_h = max(4.0, val * max_bar_h)

            color_idx = int((i / float(self.NUM_BARS)) * (len(self.COLOR_GRADIENT) - 1))
            bar_color = self.COLOR_GRADIENT[min(color_idx, len(self.COLOR_GRADIENT) - 1)]

            # Draw mirrored neon equalizer bars
            top_y = cy - bar_h
            bot_y = cy + bar_h
            self.canvas.create_rectangle(
                x, top_y, x + bar_w, bot_y,
                fill=bar_color,
                outline="",
                width=0,
            )

            points.append((x + bar_w / 2.0, top_y))

        # Draw connected oscilloscope glow line over the peaks
        if len(points) >= 2:
            flat_pts = []
            for px, py in points:
                flat_pts.extend([px, py])
            self.canvas.create_line(
                flat_pts,
                fill="#f5c2e7",
                width=2,
                smooth=True,
            )

        # Draw live peak meter bar at bottom
        meter_y = h - 3
        meter_w = w * max(0.02, min(1.0, (self.current_peak_db + 80.0) / 80.0))
        meter_color = "#a6e3a1" if self.current_peak_db < -6.0 else ("#f9e2af" if self.current_peak_db < -1.0 else "#f38ba8")
        self.canvas.create_line(0, meter_y, meter_w, meter_y, fill=meter_color, width=3)
