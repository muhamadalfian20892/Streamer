import wx
import os
import sys
import accessibility
import utils
from player import Player
import settings
import fading

class StreamerFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Streamer App", size=(800, 600))
        
        self.config = utils.load_config()
        self.player = None
        self.fader = None
        self.current_folder = ""
        self.file_list_data = [] # Full list of files in current folder
        self.filtered_file_list_data = []
        self.current_search_query = ""
        self.current_view_filter = "All"
        
        self.init_ui()
        self.init_shortcuts()
        self.bind_events()
        
        try:
            # Pass the video panel's window handle to the player
            wid = self.video_panel.GetHandle()
            self.player = Player(wid=wid)
        except Exception as e:
            wx.MessageBox(f"Error initializing Player: {e}", "Error", wx.ICON_ERROR)
            
        # Load initial state
        self.player_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.player_timer)
        self.player_timer.Start(500)
        
        # Populate recent folders
        self.initial_folder_load()
        
        # Audio Devices
        self.refresh_audio_devices()
        
        self.Bind(wx.EVT_CLOSE, self.on_close)

    def speak(self, text):
        """Wrapper for accessibility.speak that respects the verbose setting."""
        if self.config.get("nvda_verbose", True):
            accessibility.speak(text)

    def on_close(self, event):
        if hasattr(self, 'player_timer') and self.player_timer.IsRunning():
            self.player_timer.Stop()
        if self.player and hasattr(self.player, 'mp'):
            try:
                self.player.mp.terminate()
            except Exception:
                pass
        event.Skip()

    def init_ui(self):
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # --- Top Section: Navigation ---
        top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.open_btn = wx.Button(panel, label="Open Folder (Ctrl+O)")
        top_sizer.Add(self.open_btn, 0, wx.ALL | wx.CENTER, 5)
        
        self.settings_btn = wx.Button(panel, label="Settings (Ctrl+P)", name="Preferences and Settings")
        top_sizer.Add(self.settings_btn, 0, wx.ALL | wx.CENTER, 5)
        
        self.recent_combo = wx.Choice(panel, choices=[], name="Recent Folders")
        self.recent_combo.SetToolTip("Recent Folders")
        top_sizer.Add(self.recent_combo, 1, wx.ALL | wx.CENTER, 5)
        
        main_sizer.Add(top_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # --- Search and Filter Section ---
        search_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        search_label = wx.StaticText(panel, label="Search:")
        self.search_ctrl = wx.SearchCtrl(panel, style=wx.TE_PROCESS_ENTER, name="Search field")
        self.search_ctrl.ShowSearchButton(True)
        self.search_ctrl.ShowCancelButton(True)
        
        filter_label = wx.StaticText(panel, label="View:")
        self.view_filter = wx.Choice(panel, choices=["All", "Files Only", "Folders Only"], name="View Filter")
        self.view_filter.SetSelection(0)
        
        search_sizer.Add(search_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.LEFT, 5)
        search_sizer.Add(self.search_ctrl, 1, wx.EXPAND | wx.ALL, 5)
        search_sizer.Add(filter_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.LEFT, 5)
        search_sizer.Add(self.view_filter, 0, wx.EXPAND | wx.ALL, 5)
        
        main_sizer.Add(search_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # --- Middle Section: File List and Video ---
        self.splitter = wx.SplitterWindow(panel)
        
        self.list_ctrl = wx.ListCtrl(self.splitter, style=wx.LC_REPORT | wx.LC_SINGLE_SEL, name="File and Folder List")
        self.list_ctrl.InsertColumn(0, "Name", width=300)
        
        self.video_panel = wx.Panel(self.splitter)
        self.video_panel.SetBackgroundColour(wx.BLACK)
        
        self.splitter.SplitVertically(self.list_ctrl, self.video_panel, 300)
        self.splitter.SetMinimumPaneSize(100)
        
        main_sizer.Add(self.splitter, 1, wx.EXPAND | wx.ALL, 5)
        
        # --- Bottom Section: Controls ---
        # Time Label
        self.time_label = wx.StaticText(panel, label="00:00 / 00:00", name="Playback Time")
        main_sizer.Add(self.time_label, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        
        # Volume Slider
        vol_sizer = wx.BoxSizer(wx.HORIZONTAL)
        vol_label = wx.StaticText(panel, label="Volume:")
        self.vol_slider = wx.Slider(panel, value=100, minValue=0, maxValue=100, style=wx.SL_HORIZONTAL, name="Volume")
        vol_sizer.Add(vol_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        vol_sizer.Add(self.vol_slider, 1, wx.EXPAND)
        main_sizer.Add(vol_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # Playback Buttons
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.rewind_btn = wx.Button(panel, label="Mundur 5s", name="Mundur 5 detik")
        self.play_btn = wx.Button(panel, label="Play/Pause", name="Play or Pause")
        self.forward_btn = wx.Button(panel, label="Maju 5s", name="Maju 5 detik")
        self.loop_toggle = wx.ToggleButton(panel, label="Loop Off", name="Loop Toggle")
        
        btn_sizer.Add(self.rewind_btn, 1, wx.ALL, 2)
        btn_sizer.Add(self.play_btn, 1, wx.ALL, 2)
        btn_sizer.Add(self.forward_btn, 1, wx.ALL, 2)
        btn_sizer.Add(self.loop_toggle, 1, wx.ALL, 2)
        
        main_sizer.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # Audio Device Choice
        dev_sizer = wx.BoxSizer(wx.HORIZONTAL)
        dev_label = wx.StaticText(panel, label="Audio Device:")
        self.device_choice = wx.Choice(panel, name="Audio Device")
        dev_sizer.Add(dev_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        dev_sizer.Add(self.device_choice, 1, wx.EXPAND)
        main_sizer.Add(dev_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        panel.SetSizer(main_sizer)

    def init_shortcuts(self):
        # Global shortcuts for the frame
        # accelerator table for menu items is standard, but for general control:
        accel_tbl = wx.AcceleratorTable([
            (wx.ACCEL_CTRL, ord('O'), 101), # Open
            (wx.ACCEL_CTRL, ord('L'), 102), # Loop
            (wx.ACCEL_NORMAL, wx.WXK_F5, 103), # Refresh
            (wx.ACCEL_CTRL, ord('P'), 104), # Settings
            # Navigation is handled by key events or standard list ctrl behavior
        ])
        self.SetAcceleratorTable(accel_tbl)
        
        self.Bind(wx.EVT_MENU, self.on_open_folder, id=101)
        self.Bind(wx.EVT_MENU, self.on_toggle_loop_shortcut, id=102)
        self.Bind(wx.EVT_MENU, self.on_refresh_folder, id=103)
        self.Bind(wx.EVT_MENU, self.on_settings, id=104)

    def bind_events(self):
        self.open_btn.Bind(wx.EVT_BUTTON, self.on_open_folder)
        self.settings_btn.Bind(wx.EVT_BUTTON, self.on_settings)
        self.recent_combo.Bind(wx.EVT_CHOICE, self.on_recent_selected)
        
        self.search_ctrl.Bind(wx.EVT_TEXT, self.on_search_text)
        self.search_ctrl.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.on_search_cancel)
        self.view_filter.Bind(wx.EVT_CHOICE, self.on_view_filter_change)
        
        # List Events
        self.list_ctrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_item_activated) # Enter / Double Click
        self.list_ctrl.Bind(wx.EVT_CHAR_HOOK, self.on_list_key) # Handle play/pause on space, backspace
        
        # Controls
        self.play_btn.Bind(wx.EVT_BUTTON, self.on_play_pause)
        self.rewind_btn.Bind(wx.EVT_BUTTON, lambda e: self.on_seek(-5))
        self.forward_btn.Bind(wx.EVT_BUTTON, lambda e: self.on_seek(5))
        self.loop_toggle.Bind(wx.EVT_TOGGLEBUTTON, self.on_toggle_loop)
        
        self.vol_slider.Bind(wx.EVT_SLIDER, self.on_volume_change)
        self.device_choice.Bind(wx.EVT_CHOICE, self.on_device_change)
        
        # Global key hook for vol/seek if focus is elsewhere? 
        # Ideally, we want shortcuts to work globally.
        # wxPython EVT_CHAR_HOOK on the Frame captures all keys before they go to children.
        self.Bind(wx.EVT_CHAR_HOOK, self.on_global_key)

    def initial_folder_load(self):
        recents = self.config.get("recent_folders", [])
        self.recent_combo.Clear()
        if recents:
            self.recent_combo.AppendItems(recents)
            # self.recent_combo.SetSelection(0)
        
        # Load last folder if exists
        last_folder = self.config.get("last_folder", "")
        if self.config.get("resume_folder", True) and last_folder and os.path.exists(last_folder):
            self.load_folder(last_folder)

    def load_folder(self, path):
        if not os.path.isdir(path):
            return
            
        self.current_folder = path
        self.file_list_data = utils.get_audio_files(path)
        
        self.search_ctrl.SetValue("")
        self.current_search_query = ""
        self.apply_filters()
        
        # Update config
        self.config = utils.add_recent_folder(self.config, path)
        self.config["last_folder"] = path
        utils.save_config(self.config)
        
        # Update Recents UI
        recents = self.config.get("recent_folders", [])
        self.recent_combo.Clear()
        self.recent_combo.AppendItems(recents)
        
        # Focus list
        self.list_ctrl.SetFocus()
        if self.list_ctrl.GetItemCount() > 0:
            self.list_ctrl.Select(0)
            self.list_ctrl.Focus(0)
            
        self.speak(f"Folder loaded. {len(self.filtered_file_list_data)} items.")

    def on_open_folder(self, event):
        dlg = wx.DirDialog(self, "Choose a folder", defaultPath=self.current_folder)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.load_folder(path)
        dlg.Destroy()

    def on_recent_selected(self, event):
        path = self.recent_combo.GetStringSelection()
        if path:
            self.load_folder(path)

    def on_refresh_folder(self, event):
        if self.current_folder:
            self.load_folder(self.current_folder)
            self.speak("Folder refreshed.")

    def on_settings(self, event):
        with settings.SettingsDialog(self, self.config) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                self.config = dlg.get_settings()
                utils.save_config(self.config)
                self.speak("Settings saved.")

    def on_search_text(self, event):
        self.current_search_query = self.search_ctrl.GetValue().lower()
        self.apply_filters()

    def on_search_cancel(self, event):
        self.search_ctrl.SetValue("")
        self.current_search_query = ""
        self.apply_filters()
        
    def on_view_filter_change(self, event):
        self.current_view_filter = self.view_filter.GetStringSelection()
        self.apply_filters()

    def apply_filters(self):
        self.list_ctrl.DeleteAllItems()
        self.filtered_file_list_data = []
        
        for item in self.file_list_data:
            filename, is_folder = item
            
            # View filter
            if self.current_view_filter == "Files Only" and is_folder:
                continue
            if self.current_view_filter == "Folders Only" and not is_folder:
                continue
                
            # Search filter
            if self.current_search_query and self.current_search_query not in filename.lower():
                continue
                
            self.filtered_file_list_data.append(item)
            
        for i, item in enumerate(self.filtered_file_list_data):
            self.list_ctrl.InsertItem(i, item[0])
            
        if self.list_ctrl.GetItemCount() > 0:
            self.list_ctrl.Select(0)
            self.list_ctrl.Focus(0)

    def on_item_activated(self, event):
        """Called when pressing Enter or Double Click on a list item."""
        self.play_selected_item()

    def play_selected_item(self):
        selected = self.list_ctrl.GetFirstSelected()
        if selected == -1:
            return
            
        filename, is_folder = self.filtered_file_list_data[selected]
        full_path = os.path.join(self.current_folder, filename)
        
        if is_folder:
            # Navigate into directory
            self.load_folder(full_path)
        else:
            # Play file
            if not self.player: return
            
            fade_enabled = self.config.get("fade_enabled", False)
            fade_duration = self.config.get("fade_duration", 0.5)
            
            if not self.fader:
                self.fader = fading.AudioFader(self.player)
                
            def on_started():
                self.speak(f"Playing {filename}")
                self.update_play_button_label()
                
            if fade_enabled and self.player.is_playing() and fade_duration > 0:
                current_vol = self.vol_slider.GetValue()
                self.fader.fade_and_play(full_path, fade_duration, current_vol, on_complete=on_started)
            else:
                if self.fader:
                    self.fader.cancel()
                self.player.load(full_path)
                on_started()

    def on_global_key(self, event):
        """Global shortcuts handling."""
        keycode = event.GetKeyCode()
        modifiers = event.GetModifiers()
        
        # Ctrl Shortcuts
        if modifiers == wx.MOD_CONTROL:
            if keycode == wx.WXK_UP:
                self.change_volume(1)
                return
            elif keycode == wx.WXK_DOWN:
                self.change_volume(-1)
                return
            elif keycode == wx.WXK_LEFT:
                self.on_seek(-self.config.get("seek_step", 5))
                return
            elif keycode == wx.WXK_RIGHT:
                self.on_seek(self.config.get("seek_step", 5))
                return
        
        # Pass event to next handler if not processed
        event.Skip()

    def on_list_key(self, event):
        """Shortcuts specific to ListView focus."""
        keycode = event.GetKeyCode()
        
        if keycode == wx.WXK_SPACE:
            self.on_play_pause(None)
        elif keycode == wx.WXK_BACK:
            # Go up one level
            parent = os.path.dirname(self.current_folder)
            if parent and os.path.exists(parent) and parent != self.current_folder:
                self.load_folder(parent)
        else:
            event.Skip()

    def on_play_pause(self, event):
        if not self.player:
            return
            
        if getattr(self.player.mp, 'idle_active', getattr(self.player.mp, 'core_idle', True)):
            self.play_selected_item()
            return
            
        fade_pause = self.config.get("fade_pause", False)
        
        if self.player.is_playing():
            if fade_pause:
                fade_duration = self.config.get("fade_duration", 0.5)
                if not self.fader:
                    self.fader = fading.AudioFader(self.player)
                current_vol = self.vol_slider.GetValue()
                
                def on_paused():
                    self.speak("Paused")
                    self.update_play_button_label()
                    
                self.fader.fade_out_and_pause(fade_duration, current_vol, on_complete=on_paused)
                return
        else:
            if fade_pause:
                fade_duration = self.config.get("fade_duration", 0.5)
                if not self.fader:
                    self.fader = fading.AudioFader(self.player)
                current_vol = self.vol_slider.GetValue()
                
                if self.fader:
                    self.fader.cancel()
                
                self.player.set_volume(0)
                self.player.pause() # toggles to play
                
                def on_resumed():
                    self.speak("Playing")
                    self.update_play_button_label()
                    
                self.fader.fade_in_and_resume(fade_duration, current_vol, on_complete=on_resumed)
                return

        # Regular toggle or resuming
        if self.fader:
            self.fader.cancel()
        
        is_paused = self.player.pause()
        state = "Paused" if is_paused else "Playing"
        self.speak(state)
        self.update_play_button_label()

    def update_play_button_label(self):
        # We can poll player state or just toggle label based on assumption
        # Better to poll or trust the toggle
        pass # Optional update logic

    def on_toggle_loop_shortcut(self, event):
        # Toggle current state
        state = self.loop_toggle.GetValue()
        self.loop_toggle.SetValue(not state)
        self.on_toggle_loop(None)

    def on_toggle_loop(self, event):
        if not self.player: return
        state = self.loop_toggle.GetValue()
        self.player.set_loop(state)
        msg = "Loop Hidup" if state else "Loop Mati"
        self.loop_toggle.SetLabel(msg)
        self.speak(msg)

    def on_seek(self, seconds):
        if self.player:
            self.player.seek(seconds)
            curr = self.player.get_time_pos()
            if curr is not None:
                self.speak(f"{utils.format_time(curr)}")

    def change_volume(self, change):
        current = self.vol_slider.GetValue()
        step = self.config.get("volume_step", 1)
        new_val = max(0, min(100, current + (change * step)))
        self.vol_slider.SetValue(new_val)
        self.on_volume_change(None)
        self.speak(f"Volume {new_val}")

    def on_volume_change(self, event):
        val = self.vol_slider.GetValue()
        if self.player:
            self.player.set_volume(val)
        # Maybe don't speak every single step change if it's 1%
        
    def refresh_audio_devices(self):
        if not self.player:
            return
        
        devices = self.player.get_audio_devices()
        self.device_choice.Clear()
        for i, dev in enumerate(devices):
            self.device_choice.Append(dev['description'], dev['name'])
            
        # Select current or auto
        # We can iterate to find 'auto' or matches
        if self.device_choice.GetCount() > 0:
            self.device_choice.SetSelection(0) 

    def on_device_change(self, event):
        if not self.player: return
        idx = self.device_choice.GetSelection()
        if idx != wx.NOT_FOUND:
            dev_name = self.device_choice.GetClientData(idx)
            self.player.set_audio_device(dev_name)
            accessibility.speak(f"Device set to {self.device_choice.GetString(idx)}")
    
    def on_timer(self, event):
        if self.player:
            try:
                curr = self.player.get_time_pos()
                dur = self.player.get_duration()
                self.time_label.SetLabel(f"{utils.format_time(curr)} / {utils.format_time(dur)}")
            except:
                pass

