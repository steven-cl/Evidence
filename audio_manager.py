import pygame
import os

class AudioManager:
    def __init__(self):
        """Initializes the Pygame mixer engine using a safe fallback layout to prevent hardware crashes"""
        self.master_volume = 0.8
        self.sounds_dir = os.path.join("source", "audio")
        self.sfx = {}
        self.audio_enabled = True
        
        # Step timing variables (Controls how fast steps acoustic playback occurs in seconds)
        self.step_timer = 0.0
        self.step_interval = 0.5  # Time interval between steps (e.g., 0.5 seconds per step)
        
        # Safe initialization check for sound directory structures
        if not os.path.exists(self.sounds_dir):
            os.makedirs(os.path.join(self.sounds_dir, "sfx"), exist_ok=True)
            os.makedirs(os.path.join(self.sounds_dir, "music"), exist_ok=True)

        try:
            # OPTIMIZATION: Small buffer size (256) to minimize playback latency triggers
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=256)
            print("[Audio System]: WASAPI hardware endpoint initialized successfully.")
        except pygame.error as e:
            print(f"[Audio Warning]: Sound card endpoint allocation failed ({e}). Running in SILENT mode.")
            self.audio_enabled = False

    def load_sfx(self, name, filename):
        """Preloads short audio clips into memory for instant hardware execution"""
        if not self.audio_enabled: return
        path = os.path.join(self.sounds_dir, "sfx", filename)
        if os.path.exists(path):
            sound_obj = pygame.mixer.Sound(path)
            sound_obj.set_volume(self.master_volume)
            self.sfx[name] = sound_obj
        else:
            print(f"[Audio Warning]: SFX file not found at {path}")

    def play_sfx(self, name):
        """Plays a preloaded sound effect on an available hardware channel"""
        if not self.audio_enabled or name not in self.sfx: return
        self.sfx[name].play()

    def play_ambient_music(self, filename, loops=-1):
        """Streams heavy atmospheric soundtrack layouts in background loop mode"""
        if not self.audio_enabled: return
        path = os.path.join(self.sounds_dir, "music", filename)
        if os.path.exists(path):
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self.master_volume)
            # loops=-1 instructs Pygame to repeat the track infinitely at hardware level
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