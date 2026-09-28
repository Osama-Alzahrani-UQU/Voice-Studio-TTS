"""
audio_player.py - Audio Playback Controller using Pygame
-------------------------------------------------------
Thread-safe audio playback controller for playing, pausing, resuming, and
stopping generated speech files.
"""

import os
import time
import threading
import pygame

class AudioPlayerController:
    """
    Singleton audio manager wrapping Pygame Mixer for responsive audio controls.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(AudioPlayerController, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.current_file = None
        self.is_paused = False
        self.active_widget = None
        self.monitor_thread = None
        self.stop_monitor_flag = False

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
                print("[Audio Player] Pygame mixer initialized successfully.")
        except Exception as e:
            print(f"[Audio Player] Error initializing pygame mixer: {e}")

    def play_audio(self, filepath: str, widget_owner=None, on_finish=None):
        """Loads and plays a WAV audio file."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Audio file not found: {filepath}")

        self.stop_audio()

        self.current_file = filepath
        self.active_widget = widget_owner
        self.is_paused = False

        try:
            pygame.mixer.music.load(filepath)
            pygame.mixer.music.play()
            print(f"[Audio Player] Playing: {os.path.basename(filepath)}")

            self.stop_monitor_flag = False
            self.monitor_thread = threading.Thread(
                target=self._monitor_playback, args=(widget_owner, on_finish), daemon=True
            )
            self.monitor_thread.start()

        except Exception as e:
            print(f"[Audio Player] Playback error: {e}")
            raise e

    def pause_audio(self):
        """Pauses current audio playback."""
        if pygame.mixer.music.get_busy() and not self.is_paused:
            pygame.mixer.music.pause()
            self.is_paused = True
            print("[Audio Player] Playback paused.")

    def resume_audio(self):
        """Resumes paused audio playback."""
        if self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
            print("[Audio Player] Playback resumed.")

    def stop_audio(self):
        """Stops current audio playback completely."""
        self.stop_monitor_flag = True
        if pygame.mixer.get_init() and (pygame.mixer.music.get_busy() or self.is_paused):
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            print("[Audio Player] Playback stopped.")
        
        self.is_paused = False
        if self.active_widget and hasattr(self.active_widget, "reset_play_button"):
            try:
                self.active_widget.reset_play_button()
            except Exception:
                pass
        self.active_widget = None

    def toggle_play_pause(self, filepath: str, widget_owner=None, on_finish=None):
        """Toggles between play, pause, and resume."""
        if self.current_file == filepath and (pygame.mixer.music.get_busy() or self.is_paused):
            if self.is_paused:
                self.resume_audio()
                return "PLAYING"
            else:
                self.pause_audio()
                return "PAUSED"
        else:
            self.play_audio(filepath, widget_owner=widget_owner, on_finish=on_finish)
            return "PLAYING"

    def _monitor_playback(self, widget_owner, on_finish):
        """Monitors playback end."""
        while not self.stop_monitor_flag:
            time.sleep(0.1)
            if not pygame.mixer.music.get_busy() and not self.is_paused:
                break

        if not self.stop_monitor_flag and self.active_widget == widget_owner:
            self.is_paused = False
            if widget_owner and hasattr(widget_owner, "reset_play_button"):
                try:
                    widget_owner.reset_play_button()
                except Exception:
                    pass
            if on_finish:
                try:
                    on_finish()
                except Exception:
                    pass
            self.current_file = None
            self.active_widget = None
