import pygame
import os
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class AudioManager:
    def __init__(self):
        self.master_volume = 0.8
        self.sounds_dir = resource_path(os.path.join("source", "audio"))
        self.sfx = {}
        self.audio_enabled = True
        
        self.step_timer = 0.0
        self.step_interval = 0.5 
        
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=128)
            print("[Audio System]: WASAPI hardware endpoint initialized successfully.")
        except pygame.error as e:
            print(f"[Audio Warning]: Sound card endpoint allocation failed ({e}). Running in SILENT mode.")
            self.audio_enabled = False

    def load_sfx(self, name, filename):
        if not self.audio_enabled: return
        path = os.path.join(self.sounds_dir, "sfx", filename)
        
        if os.path.exists(path):
            sound_obj = pygame.mixer.Sound(path)
            sound_obj.set_volume(self.master_volume)
            self.sfx[name] = sound_obj
        else:
            print(f"[Audio Warning]: SFX file not found at {path}")

    def play_sfx(self, name):
        if not self.audio_enabled or name not in self.sfx: return
        self.sfx[name].play()

    def play_ambient_music(self, filename, loops=-1):
        if not self.audio_enabled: return
        path = os.path.join(self.sounds_dir, "music", filename)
        
        if os.path.exists(path):
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self.master_volume)
            pygame.mixer.music.play(loops)
        else:
            print(f"[Audio Warning]: Ambient music track not found at {path}")

    def update_footsteps(self, dt, is_moving, is_grounded):
        """
        Calculates stride cadence intervals using delta time to play step SFX sychronously
        only when the detective entity updates its location.
        """
        if not self.audio_enabled: return
        
        if is_moving and is_grounded:
            self.step_timer += dt
            if self.step_timer >= self.step_interval:
                self.play_sfx("footstep")
                self.step_timer = 0.0  # Reset cadence loop clock
        else:
            # Reset timer if player stops moving so next stride starts instantly
            self.step_timer = self.step_interval

    def set_volume(self, volume_percentage):
        """Dynamically updates master volume tracking structures"""
        self.master_volume = max(0.0, min(1.0, volume_percentage / 100.0))
        pygame.mixer.music.set_volume(self.master_volume)
        for sound_obj in self.sfx.values():
            sound_obj.set_volume(self.master_volume)