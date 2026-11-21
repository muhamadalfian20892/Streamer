import os
import json
import copy

CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "recent_folders": [],
    "last_folder": "",
    "volume": 100,
    "muted": False,
    "loop": False,
    "last_audio_device": "auto",
    "app_mode": "standard",
    "equalizer": "flat",
    "mono": False,
    "normalize": False,
    "nvda_verbose": True,
    "volume_step": 1,
    "seek_step": 5,
    "autoplay": False,
    "resume_folder": True,
    "fade_enabled": False,
    "fade_pause": False,
    "fade_duration": 0.5,
    "volume_max": 150,
    "global_hotkeys": True,
    "duck_volume": 15,
    "obs_export": False,
    "favorites": [],
    "soundboard": {},
    "language": "id",
    "check_updates_on_startup": False,
    "first_time_setup": True
}

def load_config():
    """Loads configuration from JSON file, merging with default settings."""
    if not os.path.exists(CONFIG_FILE):
        return copy.deepcopy(DEFAULT_CONFIG)
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            # Merge with defaults to ensure all keys exist
            for key, value in DEFAULT_CONFIG.items():
                if key not in config:
                    config[key] = copy.deepcopy(value)
            return config
    except Exception:
        return copy.deepcopy(DEFAULT_CONFIG)

def save_config(config):
    """Saves configuration atomically to JSON file using a temp file and os.replace."""
    temp_file = f"{CONFIG_FILE}.tmp"
    try:
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_file, CONFIG_FILE)
    except Exception as e:
        print(f"Error saving config: {e}")
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except OSError:
                pass

def save_setting(key, value):
    """Persists a single setting atomically into config.json."""
    config = load_config()
    config[key] = value
    save_config(config)
    return config

def save_volume(volume):
    """Saves output volume into config.json."""
    return save_setting("volume", volume)

def save_audio_device(device_name):
    """Saves output audio device into config.json."""
    return save_setting("last_audio_device", device_name)

def save_muted(muted):
    """Saves muted state into config.json."""
    return save_setting("muted", bool(muted))

def save_language(lang):
    """Saves interface language choice into config.json."""
    return save_setting("language", str(lang).lower())

def add_recent_folder(config, path):
    """Adds a path to recent folders list, keeping it unique and limited to 10."""
    recents = config.get("recent_folders", [])
    if path in recents:
        recents.remove(path)
    recents.insert(0, path)
    config["recent_folders"] = recents[:10]
    return config

def format_time(seconds):
    """Formats seconds into MM:SS or HH:MM:SS string."""
    if not seconds:
        return "00:00"
    try:
        seconds = int(float(seconds))
    except (ValueError, TypeError):
        return "00:00"
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"

MEDIA_EXTENSIONS = {
    # Audio
    '.mp3', '.wav', '.ogg', '.flac', '.m4a', '.aac', '.wma', '.opus',
    # Video / Other Media
    '.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mpeg', '.mpg', '.m4v', '.3gp'
}

def get_audio_files(folder_path):
    """
    Returns a list of media files and directories in the folder.
    """
    if not os.path.isdir(folder_path):
        return []
    
    files = []
    try:
        with os.scandir(folder_path) as entries:
            for entry in entries:
                if entry.is_file():
                    ext = os.path.splitext(entry.name)[1].lower()
                    if ext in MEDIA_EXTENSIONS:
                        files.append((entry.name, False))
                elif entry.is_dir():
                    files.append((entry.name, True))
    except (PermissionError, OSError):
        pass
    
    # Sort: Directories first, then files
    files.sort(key=lambda x: (not x[1], x[0].lower()))
    return files
