import threading
import time
import wx

class AudioFader:
    def __init__(self, player):
        self.player = player
        self.fade_thread = None
        self.cancel_event = threading.Event()

    def fade_and_play(self, new_file_path, duration, original_volume, on_complete=None):
        self.cancel_event.set()
        if self.fade_thread and self.fade_thread.is_alive():
            self.fade_thread.join(timeout=0.5)
            
        self.cancel_event.clear()
        
        self.fade_thread = threading.Thread(
            target=self._fade_task,
            args=(new_file_path, duration, original_volume, on_complete),
            daemon=True
        )
        self.fade_thread.start()

    def _fade_task(self, new_file_path, duration, original_volume, on_complete):
        steps = int(duration * 20) # 20 steps per second
        if steps < 1: steps = 1
        sleep_time = duration / steps
        vol_step = original_volume / steps
        
        curr_vol = float(original_volume)
        for _ in range(steps):
            if self.cancel_event.is_set():
                return
            curr_vol -= vol_step
            if curr_vol < 0: curr_vol = 0
            self.player.set_volume(curr_vol)
            time.sleep(sleep_time)
            
        if self.cancel_event.is_set():
            return
            
        # Ensure it reaches 0
        self.player.set_volume(0)
        
        # Load new file
        self.player.load(new_file_path)
        
        # Restore volume
        self.player.set_volume(original_volume)
        
        if on_complete:
            wx.CallAfter(on_complete)

    def fade_out_and_pause(self, duration, original_volume, on_complete=None):
        self.cancel_event.set()
        if self.fade_thread and self.fade_thread.is_alive():
            self.fade_thread.join(timeout=0.5)
            
        self.cancel_event.clear()
        
        self.fade_thread = threading.Thread(
            target=self._fade_pause_task,
            args=(duration, original_volume, on_complete),
            daemon=True
        )
        self.fade_thread.start()

    def _fade_pause_task(self, duration, original_volume, on_complete):
        steps = int(duration * 20)
        if steps < 1: steps = 1
        sleep_time = duration / steps
        vol_step = original_volume / steps
        
        curr_vol = float(original_volume)
        for _ in range(steps):
            if self.cancel_event.is_set():
                return
            curr_vol -= vol_step
            if curr_vol < 0: curr_vol = 0
            self.player.set_volume(curr_vol)
            time.sleep(sleep_time)
            
        if self.cancel_event.is_set():
            return
            
        self.player.set_volume(0)
        self.player.mp.pause = True
        self.player.set_volume(original_volume)
        
        if on_complete:
            wx.CallAfter(on_complete)

    def fade_in_and_resume(self, duration, target_volume, on_complete=None):
        self.cancel_event.set()
        if self.fade_thread and self.fade_thread.is_alive():
            self.fade_thread.join(timeout=0.5)
            
        self.cancel_event.clear()
        
        self.fade_thread = threading.Thread(
            target=self._fade_in_task,
            args=(duration, target_volume, on_complete),
            daemon=True
        )
        self.fade_thread.start()

    def _fade_in_task(self, duration, target_volume, on_complete):
        steps = int(duration * 20)
        if steps < 1: steps = 1
        sleep_time = duration / steps
        vol_step = target_volume / steps
        
        curr_vol = 0.0
        self.player.set_volume(curr_vol)
        
        for _ in range(steps):
            if self.cancel_event.is_set():
                return
            curr_vol += vol_step
            if curr_vol > target_volume: curr_vol = target_volume
            self.player.set_volume(curr_vol)
            time.sleep(sleep_time)
            
        if self.cancel_event.is_set():
            return
            
        self.player.set_volume(target_volume)
        
        if on_complete:
            wx.CallAfter(on_complete)

    def cancel(self):
        self.cancel_event.set()
