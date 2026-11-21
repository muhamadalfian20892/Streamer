import os
import time
import datetime
import accessibility
import wx

# Try to import keyboard for global hotkeys, fail gracefully if not available
try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False

class StreamFeatures:
    def __init__(self, app_frame):
        self.frame = app_frame
        self.config = self.frame.config
        self.player = self.frame.player
        self.soundboard_player = None # Second mpv instance for overlapping audio
        
        self.is_ducked = False
        self.pre_duck_volume = 100
        
        self.init_soundboard_player()
        if KEYBOARD_AVAILABLE and self.config.get("global_hotkeys", True):
            self.register_global_hotkeys()

    def init_soundboard_player(self):
        try:
            from player import Player
            # Create a detached player for overlapping sound effects
            self.soundboard_player = Player()
            self.soundboard_player.set_volume(self.config.get("volume", 100))
        except Exception as e:
            print(f"Error initializing soundboard player: {e}")

    def register_global_hotkeys(self):
        if not KEYBOARD_AVAILABLE: return
        try:
            # Ducking
            keyboard.add_hotkey('alt+d', self.toggle_duck)
            # Stream Marker
            keyboard.add_hotkey('f9', self.log_stream_marker)
            # Example soundboard slots
            for i in range(1, 10):
                keyboard.add_hotkey(f'alt+{i}', self.play_soundboard_slot, args=[str(i)])
        except Exception as e:
            print(f"Failed to register global hotkeys: {e}")

    def unregister_global_hotkeys(self):
        if KEYBOARD_AVAILABLE:
            try:
                keyboard.unhook_all()
            except Exception:
                pass

    def export_now_playing(self, filename):
        if not self.config.get("obs_export", True):
            return
        try:
            with open("now_playing.txt", "w", encoding="utf-8") as f:
                f.write(filename)
        except Exception as e:
            print(f"Error writing to now_playing.txt: {e}")

    def log_stream_marker(self):
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open("stream_timestamps.txt", "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] Stream Marker Placed\n")
            accessibility.speak("Marker saved")
        except Exception as e:
            print(f"Error writing marker: {e}")

    def toggle_duck(self):
        if not self.player: return
        # Use wx.CallAfter to run GUI updates on the main thread
        wx.CallAfter(self._do_duck)

    def _do_duck(self):
        if not self.player: return
        
        fade_enabled = self.config.get("fade_enabled", False)
        fade_duration = self.config.get("fade_duration", 0.5)
        
        if not self.frame.fader:
            import fading
            self.frame.fader = fading.AudioFader(self.player)
            
        if self.is_ducked:
            # Unduck
            self.is_ducked = False
            target_vol = self.pre_duck_volume
            accessibility.speak("Audio Normal")
        else:
            # Duck
            self.is_ducked = True
            self.pre_duck_volume = self.frame.vol_slider.GetValue()
            target_vol = min(self.config.get("duck_volume", 15), self.pre_duck_volume)
            accessibility.speak("Audio Ducked")
            
        if fade_enabled and fade_duration > 0:
            start_vol = self.frame.vol_slider.GetValue()
            def on_step(vol):
                self.frame.vol_slider.SetValue(int(vol))
                self.frame.on_volume_change(None)
            self.frame.fader.fade_volume(fade_duration, start_vol, target_vol, on_step=on_step)
        else:
            if self.frame.fader:
                self.frame.fader.cancel()
            self.frame.vol_slider.SetValue(target_vol)
            self.frame.on_volume_change(None)

    def play_soundboard_slot(self, slot_key):
        soundboard_map = self.config.get("soundboard", {})
        file_path = soundboard_map.get(slot_key)
        if file_path and os.path.exists(file_path):
            if self.soundboard_player:
                wx.CallAfter(self.soundboard_player.load, file_path)
                accessibility.speak(f"Played sound {slot_key}")
        else:
            accessibility.speak(f"Slot {slot_key} empty")

    def pin_current_file(self):
        selected = self.frame.list_ctrl.GetFirstSelected()
        if selected == -1:
            accessibility.speak("Tidak ada yang dipilih")
            return
            
        filename, is_folder = self.frame.filtered_file_list_data[selected]
        full_path = os.path.join(self.frame.current_folder, filename)
        
        favorites = self.config.get("favorites", [])
        if full_path not in favorites:
            favorites.append(full_path)
            self.config["favorites"] = favorites
            import utils
            utils.save_config(self.config)
            accessibility.speak(f"{filename} ditambahkan ke favorit")
        else:
            accessibility.speak("Sudah ada di favorit")
