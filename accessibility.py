import ctypes
import os
import sys
import time

# Global NVDA Controller Instance
nvdaControllerClient = None

def load_nvda_dll():
    """
    Attempts to load the NVDA Controller DLL.
    It checks the current directory and a 'libs' subdirectory.
    """
    global nvdaControllerClient
    if nvdaControllerClient:
        return

    try:
        # Determine the base path
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        DLL_NAME = "nvdaControllerClient64.dll"
        
        # Check current directory first
        possible_paths = [
            os.path.join(base_path, DLL_NAME),
            os.path.join(base_path, "libs", DLL_NAME),
            DLL_NAME # System path fallback
        ]

        dll_path = None
        for path in possible_paths:
            if os.path.exists(path) or path == DLL_NAME:
                try:
                    nvdaControllerClient = ctypes.cdll.LoadLibrary(path)
                    # print(f"NVDA Controller DLL loaded from: {path}")
                    break
                except OSError:
                    continue
        
        if not nvdaControllerClient:
            print("Warning: Could not load NVDA Controller DLL.")

    except Exception as e:
        print(f"Error loading NVDA DLL: {e}")

def speak(text, interrupt=True):
    """
    Speaks the given text using NVDA.
    
    Args:
        text (str): The text to speak.
        interrupt (bool): If True, stops previous speech before speaking.
    """
    if not nvdaControllerClient or not text:
        return

    try:
        text_str = str(text)
        if interrupt:
            nvdaControllerClient.nvdaController_cancelSpeech()
            time.sleep(0.01) # Small delay to ensure cancellation registers
        nvdaControllerClient.nvdaController_speakText(ctypes.c_wchar_p(text_str))
    except Exception as e:
        print(f"Error speaking text: {e}")

def beep():
    """Generates a beep using NVDA."""
    if nvdaControllerClient:
        try:
            nvdaControllerClient.nvdaController_beep(0)
        except Exception:
            pass

# Initialize on import
load_nvda_dll()
