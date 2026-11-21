import mpv
import os
import utils

EQUALIZER_PRESETS = {
    'flat': '',
    'bass_boost': 'lavfi=[bass=g=7]',
    'treble_boost': 'lavfi=[treble=g=7]',
    'vocal': 'lavfi=[highpass=f=120,equalizer=f=1000:t=q:w=1.5:g=4,equalizer=f=3000:t=q:w=1.5:g=3]'
}

PRESET_ALIASES = {
    'flat': 'flat',
    'standard': 'flat',
    'none': 'flat',
    'off': 'flat',
    'bass boost': 'bass_boost',
    'bass_boost': 'bass_boost',
    'bass': 'bass_boost',
    'treble boost': 'treble_boost',
    'treble_boost': 'treble_boost',
    'treble': 'treble_boost',
    'vocal': 'vocal',
    'voice': 'vocal',
}

class Player:
    def __init__(self, wid=None, config=None):
        try:
            kwargs = {'input_default_bindings': True, 'input_vo_keyboard': True}
            if wid is not None:
                kwargs['wid'] = str(wid)
            self.mp = mpv.MPV(**kwargs)
        except Exception as e:
            print(f"Error initializing MPV: {e}")
            raise e

        self.mp.keep_open = True
        self._observers = []
        self.cached_devices = []
        self.current_audio_device = 'auto'
        self.equalizer_preset = 'flat'
        self.normalize_enabled = False
        self.mono_enabled = False

        # Load and restore saved configuration cleanly on launch
        if config is None:
            config = utils.load_config()

        saved_vol = config.get("volume", 100)
        saved_dev = config.get("last_audio_device", "auto")
        saved_mute = config.get("muted", False)
        saved_eq = config.get("equalizer", "flat")
        saved_mono = config.get("mono", False)
        saved_norm = config.get("normalize", False)

        self.get_audio_devices(refresh=True)
        self.set_audio_device(saved_dev, persist=False)
        self.set_volume(saved_vol, persist=False)
        self.set_mute(saved_mute, persist=False)
        self.set_equalizer(saved_eq, persist=False)
        self.set_mono(saved_mono, persist=False)
        self.set_normalize(saved_norm, persist=False)

    def load(self, path):
        """Loads and plays a file."""
        if not self.mp:
            return
        self.mp.play(path)
        self.mp.pause = False

    def pause(self):
        """Toggles pause/play."""
        if not self.mp:
            return True
        current_pause = getattr(self.mp, 'pause', True)
        self.mp.pause = not current_pause
        return not current_pause

    def stop(self):
        """Stops playback and unloads the current media."""
        if not self.mp:
            return
        try:
            self.mp.stop()
        except Exception as e:
            print(f"Error stopping playback: {e}")

    def set_loop(self, enable):
        """Sets loop file mode."""
        if not self.mp:
            return
        self.mp.loop_file = 'inf' if enable else 'no'

    def get_loop(self):
        if not self.mp:
            return False
        return self.mp.loop_file != 'no' and self.mp.loop_file is not False

    def set_volume(self, volume, persist=True):
        """Sets volume (0-100+) and optionally persists to config."""
        if not self.mp:
            return
        try:
            self.mp.volume = volume
        except Exception as e:
            print(f"Error setting volume: {e}")
        if persist:
            try:
                utils.save_volume(volume)
            except Exception as e:
                print(f"Error persisting volume: {e}")

    def get_volume(self):
        if not self.mp:
            return 100
        try:
            return self.mp.volume
        except Exception:
            return 100

    def set_mute(self, mute, persist=True):
        """Mutes or unmutes playback."""
        if not self.mp:
            return
        try:
            self.mp.mute = bool(mute)
        except Exception as e:
            print(f"Error setting mute: {e}")
        if persist:
            try:
                utils.save_muted(bool(mute))
            except Exception as e:
                print(f"Error persisting mute state: {e}")

    def get_mute(self):
        if not self.mp:
            return False
        return bool(getattr(self.mp, 'mute', False))

    def toggle_mute(self, persist=True):
        """Toggles mute state."""
        new_state = not self.get_mute()
        self.set_mute(new_state, persist=persist)
        return new_state

    def seek(self, seconds):
        """Seeks by seconds (positive or negative)."""
        if not self.mp:
            return
        self.mp.seek(seconds, reference="relative")

    def seek_absolute(self, seconds):
        """Seeks to absolute timestamp in seconds."""
        if not self.mp:
            return
        self.mp.seek(seconds, reference="absolute")

    def get_time_pos(self):
        """Returns current playback time in seconds."""
        if not self.mp:
            return 0.0
        return self.mp.time_pos

    def get_duration(self):
        """Returns total duration in seconds."""
        if not self.mp:
            return 0.0
        return self.mp.duration

    def _resolve_preset_name(self, name):
        clean = str(name).strip().lower().replace("-", "_")
        return PRESET_ALIASES.get(clean, 'flat')

    def _update_audio_filters(self):
        if not self.mp:
            return
        filters = []
        if self.mono_enabled:
            filters.append('lavfi=[pan=mono]')
        if self.normalize_enabled:
            filters.append('lavfi=[loudnorm]')
        
        eq_filter = EQUALIZER_PRESETS.get(self.equalizer_preset, '')
        if eq_filter:
            filters.append(eq_filter)
        
        filter_str = ','.join(filters)
        try:
            self.mp.af = filter_str
        except Exception as e:
            print(f"Error setting audio filters '{filter_str}': {e}")

    def set_equalizer(self, preset_name, persist=False):
        """Sets equalizer preset ('flat', 'bass_boost', 'treble_boost', 'vocal')."""
        self.equalizer_preset = self._resolve_preset_name(preset_name)
        self._update_audio_filters()
        if persist:
            try:
                utils.save_setting('equalizer', self.equalizer_preset)
            except Exception as e:
                print(f"Error persisting equalizer setting: {e}")

    def get_equalizer(self):
        return self.equalizer_preset

    def set_normalize(self, enable, persist=False):
        """Enables or disables audio normalization (loudnorm filter and replaygain)."""
        self.normalize_enabled = bool(enable)
        if self.mp:
            try:
                self.mp.replaygain = 'track' if self.normalize_enabled else 'no'
            except Exception:
                pass
        self._update_audio_filters()
        if persist:
            try:
                utils.save_setting('normalize', self.normalize_enabled)
            except Exception as e:
                print(f"Error persisting normalization setting: {e}")

    def get_normalize(self):
        return self.normalize_enabled

    def set_mono(self, enable, persist=False):
        """Enables or disables mono downmix (pan=mono filter)."""
        self.mono_enabled = bool(enable)
        self._update_audio_filters()
        if persist:
            try:
                utils.save_setting('mono', self.mono_enabled)
            except Exception as e:
                print(f"Error persisting mono setting: {e}")

    def get_mono(self):
        return self.mono_enabled

    def get_audio_devices(self, refresh=True):
        """
        Returns a list of audio devices.
        Format: [{'name': 'device_name', 'description': 'Human Readable'}, ...]
        """
        if refresh or not self.cached_devices:
            devices = []
            try:
                if self.mp:
                    dev_list = self.mp.audio_device_list
                    for dev in dev_list:
                        devices.append({
                            'name': dev.get('name', ''),
                            'description': dev.get('description', '')
                        })
            except Exception as e:
                print(f"Error retrieving audio devices: {e}")
            self.cached_devices = devices
        return self.cached_devices

    def refresh_audio_devices(self):
        """Refreshes audio devices and falls back gracefully to 'auto' if current device is missing."""
        devices = self.get_audio_devices(refresh=True)
        valid_names = {d['name'] for d in devices}
        if self.current_audio_device != 'auto' and self.current_audio_device not in valid_names:
            print(f"Audio device '{self.current_audio_device}' not found; falling back to 'auto'")
            self.set_audio_device('auto', persist=True)
        return devices

    def set_audio_device(self, device_name, persist=True):
        """Sets the audio output device with graceful fallback to 'auto' if missing."""
        if not self.mp:
            return 'auto'
        
        devices = self.get_audio_devices(refresh=False)
        valid_names = {d['name'] for d in devices}
        target_device = device_name or 'auto'
        if target_device != 'auto' and target_device not in valid_names:
            print(f"Device '{target_device}' is not in available devices. Falling back to 'auto'.")
            target_device = 'auto'
        
        try:
            self.mp.audio_device = target_device
            self.current_audio_device = target_device
        except Exception as e:
            print(f"Error setting audio device to '{target_device}': {e}, falling back to 'auto'")
            try:
                self.mp.audio_device = 'auto'
                self.current_audio_device = 'auto'
            except Exception:
                pass
        
        if persist:
            try:
                utils.save_audio_device(self.current_audio_device)
            except Exception as e:
                print(f"Error persisting audio device: {e}")
        return self.current_audio_device

    def get_current_audio_device(self):
        return self.current_audio_device

    def is_playing(self):
        if not self.mp:
            return False
        return not getattr(self.mp, 'pause', True) and not getattr(self.mp, 'idle_active', getattr(self.mp, 'core_idle', True))

    def observe_property(self, name, handler):
        """Registers and tracks a property observer for clean unregistration."""
        if self.mp:
            self._observers.append((name, handler))
            self.mp.observe_property(name, handler)

    def unobserve_property(self, name, handler):
        """Unregisters an observer."""
        if self.mp:
            try:
                self.mp.unobserve_property(name, handler)
            except Exception:
                pass
            if (name, handler) in self._observers:
                self._observers.remove((name, handler))

    def terminate(self):
        """Cleanly unregisters MPV callbacks and terminates MPV instance."""
        if hasattr(self, 'mp') and self.mp is not None:
            for name, handler in self._observers:
                try:
                    self.mp.unobserve_property(name, handler)
                except Exception:
                    pass
            self._observers.clear()
            try:
                self.mp.terminate()
            except Exception:
                pass
            self.mp = None
