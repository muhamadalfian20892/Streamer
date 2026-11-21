import ctypes
import os
import sys
import time

# Local application imports
# These are imported here to access settings, but be mindful of circular dependencies.
# In this case, settings_manager does not import nvda, so it's safe.
import constants

# --- Global NVDA Controller Instance ---
nvdaControllerClient = None
# Global settings cache to avoid frequent file I/O
_settings_cache = None

def load_nvda_dll():
    """
    Attempts to load the NVDA Controller DLL from the 'libs' subfolder.
    It first checks for a local copy in 'libs', then falls back to trying
    the system path.
    """
    global nvdaControllerClient
    if nvdaControllerClient:
        return # Already loaded

    try:
        # Determine the base path (for both frozen and script execution)
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        # Look for the DLL inside the 'libs' folder
        # This constant is specific to the NVDA controller functionality.
        DLL_NAME = "nvdaControllerClient64.dll"
        local_dll_path = os.path.join(base_path, "libs", DLL_NAME)

        # Prefer the local DLL in the 'libs' folder if it exists
        if os.path.exists(local_dll_path):
            dll_path = local_dll_path
        else:
            # Fallback to the name, letting the system find it
            dll_path = DLL_NAME
            print(f"Warning: NVDA DLL not found at {local_dll_path}. Trying system path fallback: {dll_path}")

        nvdaControllerClient = ctypes.cdll.LoadLibrary(dll_path)
        print(f"NVDA Controller DLL loaded successfully from: {dll_path}")

    except OSError as e:
        print(f"Warning: Could not load the NVDA Controller DLL. NVDA speech output will be disabled. Error: {e}")
        nvdaControllerClient = None
    except Exception as e:
        print(f"An unexpected error occurred loading NVDA Controller DLL: {e}")
        nvdaControllerClient = None

def _get_verbosity_level():
    """
    Gets the current verbosity level from settings, using a cache.
    This avoids reading the settings file for every speech call.
    """
    global _settings_cache
    if _settings_cache is None:
        # This is a one-time lazy load.
        # It assumes that settings don't change without an app restart or a specific refresh call.
        import settings_manager
        _settings_cache = settings_manager.load_settings()
    
    verbosity_str = _settings_cache.get("nvda_verbosity", constants.DEFAULT_NVDA_VERBOSITY)
    return constants.NVDA_VERBOSITY_LEVELS.get(verbosity_str, constants.NVDA_VERBOSITY_LEVELS[constants.DEFAULT_NVDA_VERBOSITY])

def refresh_settings_cache():
    """Forces a reload of the settings cache. Should be called when settings change."""
    global _settings_cache
    import settings_manager
    _settings_cache = settings_manager.load_settings()
    print("NVDA module settings cache refreshed.")

def speak(text, verbosity=constants.NVDA_VERBOSITY_DEFAULT, cancel=True):
    """
    Speaks the given text using the loaded NVDA controller, respecting verbosity levels.
    
    Args:
        text (str): The text to be spoken.
        verbosity (str): The verbosity level required for this message to be spoken.
                         Can be 'quiet', 'default', or 'verbose'.
        cancel (bool): If True, cancels any previous speech before speaking.
    """
    if not nvdaControllerClient or not text:
        return

    required_level = constants.NVDA_VERBOSITY_LEVELS.get(verbosity, 1)
    current_level = _get_verbosity_level()

    if current_level >= required_level:
        try:
            text_str = str(text)  # Ensure text is a string
            if cancel:
                nvdaControllerClient.nvdaController_cancelSpeech()
                # A slight delay can help prevent issues with rapid calls, especially after a cancel.
                time.sleep(0.01)
            nvdaControllerClient.nvdaController_speakText(ctypes.c_wchar_p(text_str))
        except Exception as e:
            print(f"Error calling nvdaController_speakText: {e}")

def beep():
    """
    Generates a beep sound using the loaded NVDA controller.
    Does nothing if the controller is not available.
    """
    if nvdaControllerClient:
        try:
            # The beep function in the DLL might take arguments for pitch/duration,
            # but a simple call with 0 often works for a standard beep.
            # Adjust if the DLL documentation specifies otherwise.
            nvdaControllerClient.nvdaController_beep(0)
        except Exception as e:
            print(f"Error calling nvdaController_beep: {e}")

# --- Initial Load Attempt ---
# Load the DLL when this module is imported.
load_nvda_dll()