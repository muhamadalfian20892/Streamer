import threading
import time
import wx

def _safe_call_after(callback, *args, **kwargs):
    """Safely dispatches callback to wx main thread if the event loop is running."""
    if not callback:
        return
    try:
        app = wx.GetApp()
        if app and app.IsMainLoopRunning():
            wx.CallAfter(callback, *args, **kwargs)
        elif not app:
            callback(*args, **kwargs)
    except Exception:
        pass

class AudioFader:
    def __init__(self, player):
        self.player = player
        self.fade_thread = None
        self.cancel_event = threading.Event()
        self._lock = threading.Lock()

    def _start_thread(self, target, args):
        """Terminates any running fade thread cleanly and starts a new one with a fresh cancel token."""
        with self._lock:
            self.cancel_event.set()
            if self.fade_thread and self.fade_thread.is_alive():
                if threading.current_thread() != self.fade_thread:
                    self.fade_thread.join(timeout=0.3)
            
            self.cancel_event = threading.Event()
            self.fade_thread = threading.Thread(
                target=target,
                args=(self.cancel_event, *args),
                daemon=True
            )
            self.fade_thread.start()

    def fade_and_play(self, new_file_path, duration, original_volume, on_complete=None):
        """Fades out current playback, loads new track, and restores original volume."""
        self._start_thread(self._fade_task, (new_file_path, duration, original_volume, on_complete))

    def _fade_task(self, cancel_token, new_file_path, duration, original_volume, on_complete):
        steps = int(duration * 20)
        if steps < 1:
            steps = 1
        sleep_time = max(0.005, duration / steps)
        vol_step = float(original_volume) / steps
        
        curr_vol = float(original_volume)
        for _ in range(steps):
            if cancel_token.is_set():
                return
            curr_vol -= vol_step
            if curr_vol < 0:
                curr_vol = 0
            try:
                self.player.set_volume(curr_vol, persist=False)
            except Exception:
                pass
            if cancel_token.wait(timeout=sleep_time):
                return
            
        if cancel_token.is_set():
            return
            
        try:
            self.player.set_volume(0, persist=False)
            self.player.load(new_file_path)
            self.player.set_volume(original_volume, persist=False)
        except Exception:
            pass
        
        if not cancel_token.is_set() and on_complete:
            _safe_call_after(on_complete)

    def fade_out_and_pause(self, duration, original_volume, on_complete=None):
        """Fades out current playback to 0 and pauses."""
        self._start_thread(self._fade_pause_task, (duration, original_volume, on_complete))

    def _fade_pause_task(self, cancel_token, duration, original_volume, on_complete):
        steps = int(duration * 20)
        if steps < 1:
            steps = 1
        sleep_time = max(0.005, duration / steps)
        vol_step = float(original_volume) / steps
        
        curr_vol = float(original_volume)
        for _ in range(steps):
            if cancel_token.is_set():
                return
            curr_vol -= vol_step
            if curr_vol < 0:
                curr_vol = 0
            try:
                self.player.set_volume(curr_vol, persist=False)
            except Exception:
                pass
            if cancel_token.wait(timeout=sleep_time):
                return
            
        if cancel_token.is_set():
            return
            
        try:
            self.player.set_volume(0, persist=False)
            if hasattr(self.player, 'mp') and self.player.mp:
                self.player.mp.pause = True
            self.player.set_volume(original_volume, persist=False)
        except Exception:
            pass
        
        if not cancel_token.is_set() and on_complete:
            _safe_call_after(on_complete)

    def fade_in_and_resume(self, duration, target_volume, on_complete=None):
        """Resumes playback at volume 0 and fades in to target volume."""
        self._start_thread(self._fade_in_task, (duration, target_volume, on_complete))

    def _fade_in_task(self, cancel_token, duration, target_volume, on_complete):
        steps = int(duration * 20)
        if steps < 1:
            steps = 1
        sleep_time = max(0.005, duration / steps)
        vol_step = float(target_volume) / steps
        
        curr_vol = 0.0
        try:
            self.player.set_volume(curr_vol, persist=False)
            if hasattr(self.player, 'mp') and self.player.mp:
                self.player.mp.pause = False
        except Exception:
            pass
        
        for _ in range(steps):
            if cancel_token.is_set():
                return
            curr_vol += vol_step
            if curr_vol > target_volume:
                curr_vol = target_volume
            try:
                self.player.set_volume(curr_vol, persist=False)
            except Exception:
                pass
            if cancel_token.wait(timeout=sleep_time):
                return
            
        if cancel_token.is_set():
            return
            
        try:
            self.player.set_volume(target_volume, persist=False)
        except Exception:
            pass
        
        if not cancel_token.is_set() and on_complete:
            _safe_call_after(on_complete)

    def fade_volume(self, duration, start_volume, target_volume, on_step=None, on_complete=None):
        """Transitions volume smoothly between start_volume and target_volume."""
        self._start_thread(self._fade_volume_task, (duration, start_volume, target_volume, on_step, on_complete))

    def _fade_volume_task(self, cancel_token, duration, start_volume, target_volume, on_step, on_complete):
        duration = float(duration)
        start_volume = float(start_volume)
        target_volume = float(target_volume)

        if duration <= 0 or start_volume == target_volume:
            if not cancel_token.is_set():
                if on_step:
                    _safe_call_after(on_step, target_volume)
                else:
                    try:
                        self.player.set_volume(target_volume, persist=False)
                    except Exception:
                        pass
                if on_complete:
                    _safe_call_after(on_complete)
            return

        step_interval = min(0.05, max(0.01, duration / 20.0))
        start_time = time.monotonic()

        while not cancel_token.is_set():
            elapsed = time.monotonic() - start_time
            remaining = duration - elapsed
            if remaining <= 0:
                break

            wait_time = min(step_interval, remaining)
            if cancel_token.wait(timeout=wait_time):
                return

            elapsed = time.monotonic() - start_time
            progress = min(1.0, elapsed / duration)
            if progress >= 1.0:
                break

            curr_vol = start_volume + (target_volume - start_volume) * progress
            if on_step:
                _safe_call_after(on_step, curr_vol)
            else:
                try:
                    self.player.set_volume(curr_vol, persist=False)
                except Exception:
                    pass

        if cancel_token.is_set():
            return

        if on_step:
            _safe_call_after(on_step, target_volume)
        else:
            try:
                self.player.set_volume(target_volume, persist=False)
            except Exception:
                pass

        if not cancel_token.is_set() and on_complete:
            _safe_call_after(on_complete)

    def cancel(self):
        """Signals active fade thread to terminate immediately."""
        self.cancel_event.set()
        if self.fade_thread and self.fade_thread.is_alive():
            if threading.current_thread() != self.fade_thread:
                self.fade_thread.join(timeout=0.3)

    def terminate(self):
        """Cleanly stops background thread and releases references without leaks."""
        self.cancel()
        self.fade_thread = None
