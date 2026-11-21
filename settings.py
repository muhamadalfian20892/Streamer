import wx
import utils

class SettingsDialog(wx.Dialog):
    def __init__(self, parent, config):
        super().__init__(parent, title="Settings & Preferences", size=(450, 600))
        self.config = config
        self.init_ui()
        self.CenterOnParent()

    def init_ui(self):
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # --- Accessibility Options ---
        acc_box = wx.StaticBox(panel, label="Accessibility & Feedback")
        acc_sizer = wx.StaticBoxSizer(acc_box, wx.VERTICAL)
        
        self.chk_verbose = wx.CheckBox(panel, label="Enable NVDA Announcements (Verbose mode)", name="Enable NVDA Verbose Announcements")
        self.chk_verbose.SetValue(self.config.get("nvda_verbose", True))
        acc_sizer.Add(self.chk_verbose, 0, wx.ALL, 5)
        
        main_sizer.Add(acc_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        # --- Playback Options ---
        pb_box = wx.StaticBox(panel, label="Playback & Startup")
        pb_sizer = wx.StaticBoxSizer(pb_box, wx.VERTICAL)
        
        self.chk_resume = wx.CheckBox(panel, label="Resume last folder on startup", name="Resume last folder on startup")
        self.chk_resume.SetValue(self.config.get("resume_folder", True))
        pb_sizer.Add(self.chk_resume, 0, wx.ALL, 5)
        
        self.chk_autoplay = wx.CheckBox(panel, label="Autoplay next file automatically", name="Autoplay next file")
        self.chk_autoplay.SetValue(self.config.get("autoplay", False))
        pb_sizer.Add(self.chk_autoplay, 0, wx.ALL, 5)
        
        # Volume Step
        vol_sizer = wx.BoxSizer(wx.HORIZONTAL)
        vol_label = wx.StaticText(panel, label="Volume Step (%):")
        self.spin_vol_step = wx.SpinCtrl(panel, value=str(self.config.get("volume_step", 1)), min=1, max=25, name="Volume Step Percentage")
        vol_sizer.Add(vol_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        vol_sizer.Add(self.spin_vol_step, 1, wx.EXPAND)
        pb_sizer.Add(vol_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # Seek Step
        seek_sizer = wx.BoxSizer(wx.HORIZONTAL)
        seek_label = wx.StaticText(panel, label="Seek Step (seconds):")
        self.spin_seek_step = wx.SpinCtrl(panel, value=str(self.config.get("seek_step", 5)), min=1, max=60, name="Seek Step Seconds")
        seek_sizer.Add(seek_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        seek_sizer.Add(self.spin_seek_step, 1, wx.EXPAND)
        pb_sizer.Add(seek_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        main_sizer.Add(pb_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        # --- Fading Options ---
        fade_box = wx.StaticBox(panel, label="Audio Fading")
        fade_sizer = wx.StaticBoxSizer(fade_box, wx.VERTICAL)
        
        self.chk_fade = wx.CheckBox(panel, label="Enable Fade Out before playing next", name="Enable Fade Out")
        self.chk_fade.SetValue(self.config.get("fade_enabled", False))
        fade_sizer.Add(self.chk_fade, 0, wx.ALL, 5)
        
        self.chk_fade_pause = wx.CheckBox(panel, label="Enable Fade Out when pausing", name="Enable Fade Out on Pause")
        self.chk_fade_pause.SetValue(self.config.get("fade_pause", False))
        fade_sizer.Add(self.chk_fade_pause, 0, wx.ALL, 5)
        
        fade_dur_sizer = wx.BoxSizer(wx.HORIZONTAL)
        fade_dur_label = wx.StaticText(panel, label="Fade Duration (sec):")
        self.spin_fade_dur = wx.SpinCtrlDouble(panel, min=0.1, max=10.0, inc=0.1, name="Fade Duration Seconds")
        self.spin_fade_dur.SetValue(float(self.config.get("fade_duration", 0.5)))
        fade_dur_sizer.Add(fade_dur_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        fade_dur_sizer.Add(self.spin_fade_dur, 1, wx.EXPAND)
        fade_sizer.Add(fade_dur_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        main_sizer.Add(fade_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        # --- Stream Deck Features ---
        sd_box = wx.StaticBox(panel, label="Stream Deck Features")
        sd_sizer = wx.StaticBoxSizer(sd_box, wx.VERTICAL)
        
        self.chk_global_hotkeys = wx.CheckBox(panel, label="Enable Global Hotkeys (requires restart)", name="Enable Global Hotkeys")
        self.chk_global_hotkeys.SetValue(self.config.get("global_hotkeys", True))
        sd_sizer.Add(self.chk_global_hotkeys, 0, wx.ALL, 5)
        
        self.chk_obs_export = wx.CheckBox(panel, label="Enable OBS 'Now Playing' Export", name="Enable OBS Now Playing Export")
        self.chk_obs_export.SetValue(self.config.get("obs_export", False))
        sd_sizer.Add(self.chk_obs_export, 0, wx.ALL, 5)
        
        main_sizer.Add(sd_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        # Bind events for instant save
        self.chk_verbose.Bind(wx.EVT_CHECKBOX, self.on_change)
        self.chk_resume.Bind(wx.EVT_CHECKBOX, self.on_change)
        self.chk_autoplay.Bind(wx.EVT_CHECKBOX, self.on_change)
        self.spin_vol_step.Bind(wx.EVT_SPINCTRL, self.on_change)
        self.spin_seek_step.Bind(wx.EVT_SPINCTRL, self.on_change)
        self.chk_fade.Bind(wx.EVT_CHECKBOX, self.on_change)
        self.chk_fade_pause.Bind(wx.EVT_CHECKBOX, self.on_change)
        self.chk_global_hotkeys.Bind(wx.EVT_CHECKBOX, self.on_change)
        self.chk_obs_export.Bind(wx.EVT_CHECKBOX, self.on_change)
        try:
            self.spin_fade_dur.Bind(wx.EVT_SPINCTRLDOUBLE, self.on_change)
        except AttributeError:
            pass
        
        # Buttons
        btn_sizer = wx.StdDialogButtonSizer()
        btn_ok = wx.Button(panel, wx.ID_OK)
        btn_cancel = wx.Button(panel, wx.ID_CANCEL)
        btn_sizer.AddButton(btn_ok)
        btn_sizer.AddButton(btn_cancel)
        btn_sizer.Realize()
        main_sizer.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        panel.SetSizer(main_sizer)

    def on_change(self, event):
        self.get_settings()
        utils.save_config(self.config)
        event.Skip()

    def get_settings(self):
        self.config["nvda_verbose"] = self.chk_verbose.GetValue()
        self.config["resume_folder"] = self.chk_resume.GetValue()
        self.config["autoplay"] = self.chk_autoplay.GetValue()
        self.config["volume_step"] = self.spin_vol_step.GetValue()
        self.config["seek_step"] = self.spin_seek_step.GetValue()
        self.config["fade_enabled"] = self.chk_fade.GetValue()
        self.config["fade_pause"] = self.chk_fade_pause.GetValue()
        self.config["fade_duration"] = self.spin_fade_dur.GetValue()
        self.config["global_hotkeys"] = self.chk_global_hotkeys.GetValue()
        self.config["obs_export"] = self.chk_obs_export.GetValue()
        return self.config
