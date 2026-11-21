import mpv
import os

class Player:
    def __init__(self, wid=None):
        # Initialize MPV
        # input_default_bindings=True allows some default keys if window was visible, 
        # but we are mostly controlling via API.
        try:
            kwargs = {'input_default_bindings': True, 'input_vo_keyboard': True}
            if wid is not None:
                kwargs['wid'] = str(wid)
            self.mp = mpv.MPV(**kwargs)
        except Exception as e:
            print(f"Error initializing MPV: {e}")
            raise e

        # Set default properties
        self.mp.keep_open = True # Don't terminate on file end, allows pausing at end
        
    def load(self, path):
        """Loads and plays a file."""
        # 'replace' mode replaces the current track
        self.mp.play(path)
        self.mp.pause = False


    def pause(self):
        """Toggles pause/play."""
        current_pause = getattr(self.mp, 'pause', True)
        self.mp.pause = not current_pause
        return not current_pause

    def stop(self):
        """Stops playback."""
        self.mp.stop()

    def set_loop(self, enable):
        """Sets loop file mode."""
        if enable:
            self.mp.loop_file = 'inf'
        else:
            self.mp.loop_file = 'no'

    def get_loop(self):
        return self.mp.loop_file != 'no' and self.mp.loop_file is not False

    def set_volume(self, volume):
        """Sets volume (0-100+)."""
        self.mp.volume = volume

    def get_volume(self):
        return self.mp.volume

    def seek(self, seconds):
        """Seeks by seconds (positive or negative)."""
        self.mp.seek(seconds, reference="relative")

    def get_time_pos(self):
        """Returns current playback time in seconds."""
        return self.mp.time_pos

    def get_duration(self):
        """Returns total duration in seconds."""
        return self.mp.duration

    def get_audio_devices(self):
        """
        Returns a list of audio devices.
        Format: [{'name': 'device_name', 'description': 'Human Readable'}, ...]
        """
        devices = []
        try:
            dev_list = self.mp.audio_device_list
            for dev in dev_list:
                devices.append({
                    'name': dev['name'],
                    'description': dev['description']
                })
        except Exception:
            pass
        return devices

    def set_audio_device(self, device_name):
        """Sets the audio output device."""
        try:
            self.mp.audio_device = device_name
        except Exception as e:
            print(f"Error setting audio device: {e}")

    def is_playing(self):
        return not getattr(self.mp, 'pause', True) and not getattr(self.mp, 'idle_active', getattr(self.mp, 'core_idle', True))
