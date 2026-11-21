import ctypes
import os
import sys
import threading
import time

try:
    import winsound
    WINSOUND_AVAILABLE = True
except ImportError:
    WINSOUND_AVAILABLE = False

# Global NVDA Controller Instance
nvdaControllerClient = None

# SAPI Voice Instance (Lazy loaded for graceful fallback)
_sapi_voice = None
_sapi_init_attempted = False
_sapi_fallback_enabled = True

# Verbosity levels
VERBOSITY_VERBOSE = "verbose"
VERBOSITY_MINIMAL = "minimal"
VERBOSITY_SILENT = "silent"

_current_verbosity = VERBOSITY_VERBOSE
_sound_cues_enabled = True


def load_nvda_dll():
    """
    Attempts to load the NVDA Controller DLL.
    It checks the current directory, a 'libs' subdirectory, and system path.
    """
    global nvdaControllerClient
    if nvdaControllerClient:
        return

    try:
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        DLL_NAME = "nvdaControllerClient64.dll"
        
        possible_paths = [
            os.path.join(base_path, DLL_NAME),
            os.path.join(base_path, "libs", DLL_NAME),
            DLL_NAME
        ]

        for path in possible_paths:
            if os.path.exists(path) or path == DLL_NAME:
                try:
                    nvdaControllerClient = ctypes.cdll.LoadLibrary(path)
                    break
                except OSError:
                    continue
        
        if not nvdaControllerClient:
            print("Warning: Could not load NVDA Controller DLL.")

    except Exception as e:
        print(f"Error loading NVDA DLL: {e}")


def is_nvda_running():
    """Returns True if NVDA is actively running and responding via the Controller DLL."""
    if not nvdaControllerClient:
        return False
    try:
        # nvdaController_testIfRunning returns 0 on success
        return nvdaControllerClient.nvdaController_testIfRunning() == 0
    except Exception:
        return False


def _get_sapi_voice():
    """Lazily initializes and returns Windows SAPI SpVoice COM object for fallback."""
    global _sapi_voice, _sapi_init_attempted
    if _sapi_voice is not None:
        return _sapi_voice
    if _sapi_init_attempted:
        return None

    _sapi_init_attempted = True
    try:
        import win32com.client.dynamic
        _sapi_voice = win32com.client.dynamic.Dispatch("SAPI.SpVoice")
        return _sapi_voice
    except Exception:
        _sapi_voice = None
        return None


def set_sapi_fallback(enabled):
    """Enable or disable SAPI fallback when NVDA is not running."""
    global _sapi_fallback_enabled
    _sapi_fallback_enabled = bool(enabled)


def get_sapi_fallback():
    """Returns whether SAPI fallback is enabled."""
    return _sapi_fallback_enabled


def set_verbosity(level):
    """
    Sets speech verbosity level:
    'verbose': speaks all events and updates
    'minimal': speaks only essential events and toggles
    'silent':  suppresses all speech output
    Accepts string or boolean (True -> 'verbose', False -> 'minimal').
    """
    global _current_verbosity
    if isinstance(level, bool):
        _current_verbosity = VERBOSITY_VERBOSE if level else VERBOSITY_MINIMAL
    elif isinstance(level, str):
        lvl = level.strip().lower()
        if lvl in (VERBOSITY_VERBOSE, VERBOSITY_MINIMAL, VERBOSITY_SILENT):
            _current_verbosity = lvl
        else:
            _current_verbosity = VERBOSITY_VERBOSE


def get_verbosity():
    """Returns current speech verbosity level."""
    return _current_verbosity


def set_sound_cues(enabled):
    """Enable or disable audio cues and earcons."""
    global _sound_cues_enabled
    _sound_cues_enabled = bool(enabled)


def get_sound_cues():
    """Returns whether sound cues are enabled."""
    return _sound_cues_enabled


def speak(text, interrupt=True, level="verbose", minimal=False):
    """
    Speaks the given text using NVDA or falls back gracefully to SAPI if NVDA is not running.
    
    Args:
        text (str): The text to speak.
        interrupt (bool): If True, cancels previous speech before speaking.
        level (str): 'verbose' or 'minimal'.
        minimal (bool): If True, treats level as 'minimal'.
    """
    if not text:
        return

    # Check verbosity filter
    target_level = "minimal" if minimal else str(level).strip().lower()
    curr_verb = _current_verbosity.lower()
    
    if curr_verb == VERBOSITY_SILENT:
        return
    if curr_verb == VERBOSITY_MINIMAL and target_level not in ("minimal", "high", "critical", "essential"):
        return

    text_str = str(text)

    # 1. Try NVDA if running
    if is_nvda_running():
        try:
            if interrupt:
                nvdaControllerClient.nvdaController_cancelSpeech()
                time.sleep(0.01)
            nvdaControllerClient.nvdaController_speakText(ctypes.c_wchar_p(text_str))
            return
        except Exception as e:
            print(f"Error speaking text via NVDA: {e}")

    # 2. Fallback to SAPI if NVDA is not running and fallback is enabled
    if _sapi_fallback_enabled:
        try:
            voice = _get_sapi_voice()
            if voice:
                # SVSFlagsAsync = 1, SVSFPurgeBeforeSpeak = 2
                flags = 3 if interrupt else 1
                voice.Speak(text_str, flags)
                return
        except Exception:
            pass


def speak_minimal(text, interrupt=True):
    """Convenience helper to speak an essential or minimal announcement."""
    speak(text, interrupt=interrupt, level="minimal")


def speak_verbose(text, interrupt=True):
    """Convenience helper to speak a verbose announcement."""
    speak(text, interrupt=interrupt, level="verbose")


def beep(freq=800, duration_ms=50):
    """Generates an audible beep sound without blocking the main thread."""
    if not WINSOUND_AVAILABLE or not _sound_cues_enabled:
        return
    try:
        threading.Thread(
            target=winsound.Beep,
            args=(int(freq), int(duration_ms)),
            daemon=True
        ).start()
    except Exception:
        pass


def play_boundary_cue(boundary="top"):
    """
    Plays an earcon / sound cue when reaching a list boundary.
    'top' or True: higher pitched cue indicating start of list.
    'bottom' or False: lower pitched cue indicating end of list.
    """
    if not WINSOUND_AVAILABLE or not _sound_cues_enabled:
        return
    
    is_top = (boundary == "top" or boundary is True)
    freq = 1000 if is_top else 450
    duration = 40
    beep(freq=freq, duration_ms=duration)


def play_boundary_top():
    """Play sound cue for reaching the top boundary."""
    play_boundary_cue(boundary="top")


def play_boundary_bottom():
    """Play sound cue for reaching the bottom boundary."""
    play_boundary_cue(boundary="bottom")


# Initialize on import
load_nvda_dll()
