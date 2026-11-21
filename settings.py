import wx
import utils
import i18n


class SettingsDialog(wx.Dialog):
    """
    Accessible settings and preferences dialog.
    Supports live dynamic language switching and instant persistence.
    """
    def __init__(self, parent, config):
        title = i18n.t("settings_title")
        super().__init__(
            parent,
            title=title,
            size=(540, 680),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        )
        self.SetMinSize((480, 440))
        self.parent_frame = parent
        self.config = config if config is not None else {}
        self.init_ui()
        self.CenterOnParent()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.Destroy()

    def init_ui(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        scroll_win = wx.ScrolledWindow(self, style=wx.VSCROLL | wx.TAB_TRAVERSAL)
        scroll_win.SetName("Area Pengaturan Bergulir")
        scroll_win.SetScrollRate(0, 15)
        self.scroll_win = scroll_win
        content_sizer = wx.BoxSizer(wx.VERTICAL)

        # =========================================================================
        # 1. General & Language
        # =========================================================================
        self.gen_box = wx.StaticBox(scroll_win, label=i18n.t("settings_general_box"))
        self.gen_box.SetName(i18n.t("settings_general_box"))
        gen_sizer = wx.StaticBoxSizer(self.gen_box, wx.VERTICAL)

        # Interface Language Choice
        lang_row = wx.BoxSizer(wx.HORIZONTAL)
        self.lang_label = wx.StaticText(scroll_win, label=i18n.t("settings_lang_label"))
        self.lang_label.SetName(i18n.t("settings_lang_label"))
        self.choice_language = wx.Choice(
            scroll_win,
            choices=["Bahasa Indonesia", "English"],
            name=i18n.t("settings_lang_label")
        )
        self.choice_language.SetName(i18n.t("settings_lang_label"))
        self.choice_language.SetToolTip(i18n.t("settings_lang_tip"))
        curr_lang = i18n.get_language()
        self.choice_language.SetSelection(1 if curr_lang == "en" else 0)
        lang_row.Add(self.lang_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        lang_row.Add(self.choice_language, 1, wx.EXPAND)
        gen_sizer.Add(lang_row, 0, wx.EXPAND | wx.ALL, 6)

        # Mode Choice (Standard vs Advanced)
        mode_row = wx.BoxSizer(wx.HORIZONTAL)
        self.mode_label = wx.StaticText(scroll_win, label=i18n.t("settings_mode_label"))
        self.mode_label.SetName(i18n.t("settings_mode_label"))
        self.choice_app_mode = wx.Choice(
            scroll_win,
            choices=[i18n.t("settings_mode_opt_standard"), i18n.t("settings_mode_opt_advanced")],
            name=i18n.t("settings_mode_label")
        )
        self.choice_app_mode.SetName(i18n.t("settings_mode_label"))
        self.choice_app_mode.SetToolTip(i18n.t("settings_mode_tip"))
        current_mode = str(self.config.get("app_mode", "standard")).lower()
        self.choice_app_mode.SetSelection(1 if current_mode == "advanced" else 0)
        mode_row.Add(self.mode_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        mode_row.Add(self.choice_app_mode, 1, wx.EXPAND)
        gen_sizer.Add(mode_row, 0, wx.EXPAND | wx.ALL, 6)

        # Resume last folder
        self.chk_resume = wx.CheckBox(
            scroll_win,
            label=i18n.t("settings_resume"),
            name=i18n.t("settings_resume")
        )
        self.chk_resume.SetName(i18n.t("settings_resume"))
        self.chk_resume.SetToolTip(i18n.t("settings_resume_tip"))
        self.chk_resume.SetValue(bool(self.config.get("resume_folder", True)))
        gen_sizer.Add(self.chk_resume, 0, wx.ALL, 6)

        # Remember window position
        self.chk_remember_pos = wx.CheckBox(
            scroll_win,
            label=i18n.t("settings_remember_pos"),
            name=i18n.t("settings_remember_pos")
        )
        self.chk_remember_pos.SetName(i18n.t("settings_remember_pos"))
        self.chk_remember_pos.SetToolTip(i18n.t("settings_remember_pos_tip"))
        self.chk_remember_pos.SetValue(bool(self.config.get("remember_window_pos", True)))
        gen_sizer.Add(self.chk_remember_pos, 0, wx.ALL, 6)

        # Automatic update check on startup
        self.chk_check_updates = wx.CheckBox(
            scroll_win,
            label=i18n.t("settings_check_updates_startup"),
            name=i18n.t("settings_check_updates_startup")
        )
        self.chk_check_updates.SetName(i18n.t("settings_check_updates_startup"))
        self.chk_check_updates.SetToolTip(i18n.t("settings_check_updates_startup_tip"))
        self.chk_check_updates.SetValue(bool(self.config.get("check_updates_on_startup", False)))
        gen_sizer.Add(self.chk_check_updates, 0, wx.ALL, 6)

        content_sizer.Add(gen_sizer, 0, wx.EXPAND | wx.ALL, 8)

        # =========================================================================
        # 2. Playback & Navigation
        # =========================================================================
        self.pb_box = wx.StaticBox(scroll_win, label=i18n.t("settings_playback_box"))
        self.pb_box.SetName(i18n.t("settings_playback_box"))
        pb_sizer = wx.StaticBoxSizer(self.pb_box, wx.VERTICAL)

        # Autoplay next track
        self.chk_autoplay = wx.CheckBox(
            scroll_win,
            label=i18n.t("settings_autoplay"),
            name=i18n.t("settings_autoplay")
        )
        self.chk_autoplay.SetName(i18n.t("settings_autoplay"))
        self.chk_autoplay.SetToolTip(i18n.t("settings_autoplay_tip"))
        self.chk_autoplay.SetValue(bool(self.config.get("autoplay", False)))
        pb_sizer.Add(self.chk_autoplay, 0, wx.ALL, 6)

        # Volume Step
        vol_step_row = wx.BoxSizer(wx.HORIZONTAL)
        self.vol_step_label = wx.StaticText(scroll_win, label=i18n.t("settings_vol_step"))
        self.vol_step_label.SetName(i18n.t("settings_vol_step"))
        self.spin_vol_step = wx.SpinCtrl(
            scroll_win,
            min=1,
            max=25,
            initial=int(self.config.get("volume_step", 1)),
            name=i18n.t("settings_vol_step")
        )
        self.spin_vol_step.SetName(i18n.t("settings_vol_step"))
        self.spin_vol_step.SetToolTip(i18n.t("settings_vol_step_tip"))
        vol_step_row.Add(self.vol_step_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        vol_step_row.Add(self.spin_vol_step, 1, wx.EXPAND)
        pb_sizer.Add(vol_step_row, 0, wx.EXPAND | wx.ALL, 6)

        # Seek Step
        seek_step_row = wx.BoxSizer(wx.HORIZONTAL)
        self.seek_step_label = wx.StaticText(scroll_win, label=i18n.t("settings_seek_step"))
        self.seek_step_label.SetName(i18n.t("settings_seek_step"))
        self.spin_seek_step = wx.SpinCtrl(
            scroll_win,
            min=1,
            max=60,
            initial=int(self.config.get("seek_step", 5)),
            name=i18n.t("settings_seek_step")
        )
        self.spin_seek_step.SetName(i18n.t("settings_seek_step"))
        self.spin_seek_step.SetToolTip(i18n.t("settings_seek_step_tip"))
        seek_step_row.Add(self.seek_step_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        seek_step_row.Add(self.spin_seek_step, 1, wx.EXPAND)
        pb_sizer.Add(seek_step_row, 0, wx.EXPAND | wx.ALL, 6)

        # Max Volume Limit (100% or 150%)
        max_vol_row = wx.BoxSizer(wx.HORIZONTAL)
        self.max_vol_label = wx.StaticText(scroll_win, label=i18n.t("settings_vol_max"))
        self.max_vol_label.SetName(i18n.t("settings_vol_max"))
        self.choice_max_vol = wx.Choice(
            scroll_win,
            choices=["100%", "150%"],
            name=i18n.t("settings_vol_max")
        )
        self.choice_max_vol.SetName(i18n.t("settings_vol_max"))
        self.choice_max_vol.SetToolTip(i18n.t("settings_vol_max_tip"))
        max_vol_val = int(self.config.get("volume_max", 150))
        self.choice_max_vol.SetSelection(1 if max_vol_val > 100 else 0)
        max_vol_row.Add(self.max_vol_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        max_vol_row.Add(self.choice_max_vol, 1, wx.EXPAND)
        pb_sizer.Add(max_vol_row, 0, wx.EXPAND | wx.ALL, 6)

        # Shuffle Default
        self.chk_shuffle = wx.CheckBox(
            scroll_win,
            label=i18n.t("btn_shuffle_name"),
            name=i18n.t("btn_shuffle_name")
        )
        self.chk_shuffle.SetName(i18n.t("btn_shuffle_name"))
        self.chk_shuffle.SetToolTip(i18n.t("btn_shuffle_tip"))
        self.chk_shuffle.SetValue(bool(self.config.get("shuffle", False)))
        pb_sizer.Add(self.chk_shuffle, 0, wx.ALL, 6)

        content_sizer.Add(pb_sizer, 0, wx.EXPAND | wx.ALL, 8)

        # =========================================================================
        # 3. Audio & Equalizer
        # =========================================================================
        self.audio_box = wx.StaticBox(scroll_win, label=i18n.t("settings_audio_box"))
        self.audio_box.SetName(i18n.t("settings_audio_box"))
        audio_sizer = wx.StaticBoxSizer(self.audio_box, wx.VERTICAL)

        # Equalizer Profile Choice
        eq_row = wx.BoxSizer(wx.HORIZONTAL)
        self.eq_label = wx.StaticText(scroll_win, label=i18n.t("settings_eq_label"))
        self.eq_label.SetName(i18n.t("settings_eq_label"))
        self.choice_equalizer = wx.Choice(
            scroll_win,
            choices=[
                i18n.t("menu_eq_flat"),
                i18n.t("menu_eq_bass"),
                i18n.t("menu_eq_treble"),
                i18n.t("menu_eq_vocal")
            ],
            name=i18n.t("settings_eq_label")
        )
        self.choice_equalizer.SetName(i18n.t("settings_eq_label"))
        self.choice_equalizer.SetToolTip(i18n.t("settings_eq_tip"))
        eq_map_inv = {"flat": 0, "bass_boost": 1, "treble_boost": 2, "vocal": 3}
        current_eq = str(self.config.get("equalizer", "flat")).lower()
        self.choice_equalizer.SetSelection(eq_map_inv.get(current_eq, 0))
        eq_row.Add(self.eq_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        eq_row.Add(self.choice_equalizer, 1, wx.EXPAND)
        audio_sizer.Add(eq_row, 0, wx.EXPAND | wx.ALL, 6)

        # Normalization
        self.chk_normalize = wx.CheckBox(
            scroll_win,
            label=i18n.t("settings_norm"),
            name=i18n.t("settings_norm")
        )
        self.chk_normalize.SetName(i18n.t("settings_norm"))
        self.chk_normalize.SetToolTip(i18n.t("settings_norm_tip"))
        self.chk_normalize.SetValue(bool(self.config.get("normalize", False)))
        audio_sizer.Add(self.chk_normalize, 0, wx.ALL, 6)

        # Mono Downmix
        self.chk_mono = wx.CheckBox(
            scroll_win,
            label=i18n.t("settings_mono"),
            name=i18n.t("settings_mono")
        )
        self.chk_mono.SetName(i18n.t("settings_mono"))
        self.chk_mono.SetToolTip(i18n.t("settings_mono_tip"))
        self.chk_mono.SetValue(bool(self.config.get("mono", False)))
        audio_sizer.Add(self.chk_mono, 0, wx.ALL, 6)

        # Audio Fading Checkboxes
        self.chk_fade = wx.CheckBox(
            scroll_win,
            label=i18n.t("settings_fade_next"),
            name=i18n.t("settings_fade_next")
        )
        self.chk_fade.SetName(i18n.t("settings_fade_next"))
        self.chk_fade.SetToolTip(i18n.t("settings_fade_next_tip"))
        self.chk_fade.SetValue(bool(self.config.get("fade_enabled", False)))
        audio_sizer.Add(self.chk_fade, 0, wx.ALL, 6)

        self.chk_fade_pause = wx.CheckBox(
            scroll_win,
            label=i18n.t("settings_fade_pause"),
            name=i18n.t("settings_fade_pause")
        )
        self.chk_fade_pause.SetName(i18n.t("settings_fade_pause"))
        self.chk_fade_pause.SetToolTip(i18n.t("settings_fade_pause_tip"))
        self.chk_fade_pause.SetValue(bool(self.config.get("fade_pause", False)))
        audio_sizer.Add(self.chk_fade_pause, 0, wx.ALL, 6)

        # Fade Duration
        fade_dur_row = wx.BoxSizer(wx.HORIZONTAL)
        self.fade_dur_label = wx.StaticText(scroll_win, label=i18n.t("settings_fade_dur"))
        self.fade_dur_label.SetName(i18n.t("settings_fade_dur"))
        self.spin_fade_dur = wx.SpinCtrlDouble(
            scroll_win,
            min=0.1,
            max=10.0,
            inc=0.1,
            initial=float(self.config.get("fade_duration", 0.5)),
            name=i18n.t("settings_fade_dur")
        )
        self.spin_fade_dur.SetName(i18n.t("settings_fade_dur"))
        self.spin_fade_dur.SetToolTip(i18n.t("settings_fade_dur_tip"))
        fade_dur_row.Add(self.fade_dur_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        fade_dur_row.Add(self.spin_fade_dur, 1, wx.EXPAND)
        audio_sizer.Add(fade_dur_row, 0, wx.EXPAND | wx.ALL, 6)

        content_sizer.Add(audio_sizer, 0, wx.EXPAND | wx.ALL, 8)

        # =========================================================================
        # 4. Accessibility & Feedback
        # =========================================================================
        self.acc_box = wx.StaticBox(scroll_win, label=i18n.t("settings_acc_box"))
        self.acc_box.SetName(i18n.t("settings_acc_box"))
        acc_sizer = wx.StaticBoxSizer(self.acc_box, wx.VERTICAL)

        # Verbosity Level
        verb_row = wx.BoxSizer(wx.HORIZONTAL)
        self.verb_label = wx.StaticText(scroll_win, label=i18n.t("settings_verbosity_label"))
        self.verb_label.SetName(i18n.t("settings_verbosity_label"))
        self.choice_verbosity = wx.Choice(
            scroll_win,
            choices=[
                i18n.t("settings_verb_verbose"),
                i18n.t("settings_verb_minimal"),
                i18n.t("settings_verb_silent")
            ],
            name=i18n.t("settings_verbosity_label")
        )
        self.choice_verbosity.SetName(i18n.t("settings_verbosity_label"))
        self.choice_verbosity.SetToolTip(i18n.t("settings_verbosity_tip"))
        current_verb = str(self.config.get("nvda_verbosity", self.config.get("speech_verbosity", "verbose"))).lower()
        verb_map_inv = {"verbose": 0, "minimal": 1, "silent": 2}
        self.choice_verbosity.SetSelection(verb_map_inv.get(current_verb, 0))
        verb_row.Add(self.verb_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        verb_row.Add(self.choice_verbosity, 1, wx.EXPAND)
        acc_sizer.Add(verb_row, 0, wx.EXPAND | wx.ALL, 6)

        # Audio Boundary Cues
        self.chk_audio_cues = wx.CheckBox(
            scroll_win,
            label=i18n.t("settings_cues"),
            name=i18n.t("settings_cues")
        )
        self.chk_audio_cues.SetName(i18n.t("settings_cues"))
        self.chk_audio_cues.SetToolTip(i18n.t("settings_cues_tip"))
        cues_val = self.config.get("audio_cues", self.config.get("sound_cues", True))
        self.chk_audio_cues.SetValue(bool(cues_val))
        acc_sizer.Add(self.chk_audio_cues, 0, wx.ALL, 6)

        content_sizer.Add(acc_sizer, 0, wx.EXPAND | wx.ALL, 8)

        # =========================================================================
        # 5. Tools & Sleep Timer
        # =========================================================================
        self.tools_box = wx.StaticBox(scroll_win, label=i18n.t("settings_tools_box"))
        self.tools_box.SetName(i18n.t("settings_tools_box"))
        tools_sizer = wx.StaticBoxSizer(self.tools_box, wx.VERTICAL)

        # Sleep Timer
        st_row = wx.BoxSizer(wx.HORIZONTAL)
        self.st_label = wx.StaticText(scroll_win, label=i18n.t("settings_sleep_label"))
        self.st_label.SetName(i18n.t("settings_sleep_label"))
        self.choice_sleep_timer = wx.Choice(
            scroll_win,
            choices=["Off", "15m", "30m", "45m", "60m"],
            name=i18n.t("settings_sleep_label")
        )
        self.choice_sleep_timer.SetName(i18n.t("settings_sleep_label"))
        self.choice_sleep_timer.SetToolTip(i18n.t("settings_sleep_tip"))
        curr_st = str(self.config.get("sleep_timer", "Off"))
        st_map_inv = {"Off": 0, "15m": 1, "30m": 2, "45m": 3, "60m": 4}
        self.choice_sleep_timer.SetSelection(st_map_inv.get(curr_st, 0))
        st_row.Add(self.st_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        st_row.Add(self.choice_sleep_timer, 1, wx.EXPAND)
        tools_sizer.Add(st_row, 0, wx.EXPAND | wx.ALL, 6)

        # OBS Export
        self.chk_obs_export = wx.CheckBox(
            scroll_win,
            label=i18n.t("settings_obs"),
            name=i18n.t("settings_obs")
        )
        self.chk_obs_export.SetName(i18n.t("settings_obs"))
        self.chk_obs_export.SetToolTip(i18n.t("settings_obs_tip"))
        self.chk_obs_export.SetValue(bool(self.config.get("obs_export", False)))
        tools_sizer.Add(self.chk_obs_export, 0, wx.ALL, 6)

        # Global Hotkeys (legacy option)
        self.chk_global_hotkeys = wx.CheckBox(
            scroll_win,
            label="Enable Global Hotkeys" if i18n.get_language() == "en" else "Aktifkan Tombol Pintasan Global",
            name="Global Hotkeys"
        )
        self.chk_global_hotkeys.SetName("Global Hotkeys")
        self.chk_global_hotkeys.SetToolTip("Global background hotkeys for ducking and stream markers")
        self.chk_global_hotkeys.SetValue(bool(self.config.get("global_hotkeys", True)))
        tools_sizer.Add(self.chk_global_hotkeys, 0, wx.ALL, 6)

        content_sizer.Add(tools_sizer, 0, wx.EXPAND | wx.ALL, 8)

        scroll_win.SetSizer(content_sizer)
        main_sizer.Add(scroll_win, 1, wx.EXPAND | wx.ALL, 4)

        # =========================================================================
        # Dialog Buttons (OK, Cancel)
        # =========================================================================
        btn_sizer = wx.StdDialogButtonSizer()

        self.btn_ok = wx.Button(self, wx.ID_OK, label=i18n.t("btn_save_apply"))
        self.btn_ok.SetName(i18n.t("btn_save_apply"))
        self.btn_ok.SetToolTip("Simpan semua perubahan pengaturan dan tutup dialog" if i18n.get_language() == "id" else "Save settings and close dialog")
        self.btn_ok.SetDefault()

        self.btn_cancel = wx.Button(self, wx.ID_CANCEL, label=i18n.t("btn_cancel"))
        self.btn_cancel.SetName(i18n.t("btn_cancel"))
        self.btn_cancel.SetToolTip("Batalkan perubahan dan tutup dialog" if i18n.get_language() == "id" else "Discard changes and close dialog")

        btn_sizer.AddButton(self.btn_ok)
        btn_sizer.AddButton(self.btn_cancel)
        btn_sizer.Realize()
        main_sizer.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 10)

        self.SetSizer(main_sizer)

        # Bind events for auto-persisting
        self.choice_language.Bind(wx.EVT_CHOICE, self.on_language_change)
        self.choice_app_mode.Bind(wx.EVT_CHOICE, self.on_change)
        self.chk_resume.Bind(wx.EVT_CHECKBOX, self.on_change)
        self.chk_remember_pos.Bind(wx.EVT_CHECKBOX, self.on_change)
        self.chk_check_updates.Bind(wx.EVT_CHECKBOX, self.on_change)

        self.chk_autoplay.Bind(wx.EVT_CHECKBOX, self.on_change)
        self.spin_vol_step.Bind(wx.EVT_SPINCTRL, self.on_change)
        self.spin_seek_step.Bind(wx.EVT_SPINCTRL, self.on_change)
        self.choice_max_vol.Bind(wx.EVT_CHOICE, self.on_change)
        self.chk_shuffle.Bind(wx.EVT_CHECKBOX, self.on_change)

        self.choice_equalizer.Bind(wx.EVT_CHOICE, self.on_change)
        self.chk_normalize.Bind(wx.EVT_CHECKBOX, self.on_change)
        self.chk_mono.Bind(wx.EVT_CHECKBOX, self.on_change)
        self.chk_fade.Bind(wx.EVT_CHECKBOX, self.on_change)
        self.chk_fade_pause.Bind(wx.EVT_CHECKBOX, self.on_change)
        try:
            self.spin_fade_dur.Bind(wx.EVT_SPINCTRLDOUBLE, self.on_change)
        except AttributeError:
            pass

        self.choice_verbosity.Bind(wx.EVT_CHOICE, self.on_change)
        self.chk_audio_cues.Bind(wx.EVT_CHECKBOX, self.on_change)

        self.choice_sleep_timer.Bind(wx.EVT_CHOICE, self.on_change)
        self.chk_obs_export.Bind(wx.EVT_CHECKBOX, self.on_change)
        self.chk_global_hotkeys.Bind(wx.EVT_CHECKBOX, self.on_change)

    def on_language_change(self, event):
        sel = self.choice_language.GetSelection()
        new_lang = "en" if sel == 1 else "id"
        if new_lang != i18n.get_language():
            i18n.set_language(new_lang, persist=True)
            self.config["language"] = new_lang
            utils.save_config(self.config)
            self.retranslate_ui()
            if self.parent_frame and hasattr(self.parent_frame, 'retranslate_ui'):
                self.parent_frame.retranslate_ui()
            if self.parent_frame and hasattr(self.parent_frame, 'speak'):
                self.parent_frame.speak(i18n.t("lang_switched"))
        if event:
            event.Skip()

    def retranslate_ui(self):
        """Refreshes all labels and tooltips in SettingsDialog to active language."""
        self.SetTitle(i18n.t("settings_title"))

        self.gen_box.SetLabel(i18n.t("settings_general_box"))
        self.lang_label.SetLabel(i18n.t("settings_lang_label"))
        self.choice_language.SetToolTip(i18n.t("settings_lang_tip"))

        self.mode_label.SetLabel(i18n.t("settings_mode_label"))
        curr_mode_sel = self.choice_app_mode.GetSelection()
        self.choice_app_mode.Clear()
        self.choice_app_mode.AppendItems([i18n.t("settings_mode_opt_standard"), i18n.t("settings_mode_opt_advanced")])
        self.choice_app_mode.SetSelection(curr_mode_sel if curr_mode_sel != wx.NOT_FOUND else 0)
        self.choice_app_mode.SetToolTip(i18n.t("settings_mode_tip"))

        self.chk_resume.SetLabel(i18n.t("settings_resume"))
        self.chk_resume.SetToolTip(i18n.t("settings_resume_tip"))
        self.chk_remember_pos.SetLabel(i18n.t("settings_remember_pos"))
        self.chk_remember_pos.SetToolTip(i18n.t("settings_remember_pos_tip"))
        if hasattr(self, 'chk_check_updates'):
            self.chk_check_updates.SetLabel(i18n.t("settings_check_updates_startup"))
            self.chk_check_updates.SetToolTip(i18n.t("settings_check_updates_startup_tip"))

        self.pb_box.SetLabel(i18n.t("settings_playback_box"))
        self.chk_autoplay.SetLabel(i18n.t("settings_autoplay"))
        self.chk_autoplay.SetToolTip(i18n.t("settings_autoplay_tip"))
        self.vol_step_label.SetLabel(i18n.t("settings_vol_step"))
        self.spin_vol_step.SetToolTip(i18n.t("settings_vol_step_tip"))
        self.seek_step_label.SetLabel(i18n.t("settings_seek_step"))
        self.spin_seek_step.SetToolTip(i18n.t("settings_seek_step_tip"))
        self.max_vol_label.SetLabel(i18n.t("settings_vol_max"))
        self.choice_max_vol.SetToolTip(i18n.t("settings_vol_max_tip"))
        self.chk_shuffle.SetLabel(i18n.t("btn_shuffle_name"))
        self.chk_shuffle.SetToolTip(i18n.t("btn_shuffle_tip"))

        self.audio_box.SetLabel(i18n.t("settings_audio_box"))
        self.eq_label.SetLabel(i18n.t("settings_eq_label"))
        curr_eq_sel = self.choice_equalizer.GetSelection()
        self.choice_equalizer.Clear()
        self.choice_equalizer.AppendItems([
            i18n.t("menu_eq_flat"),
            i18n.t("menu_eq_bass"),
            i18n.t("menu_eq_treble"),
            i18n.t("menu_eq_vocal")
        ])
        self.choice_equalizer.SetSelection(curr_eq_sel if curr_eq_sel != wx.NOT_FOUND else 0)
        self.choice_equalizer.SetToolTip(i18n.t("settings_eq_tip"))

        self.chk_normalize.SetLabel(i18n.t("settings_norm"))
        self.chk_normalize.SetToolTip(i18n.t("settings_norm_tip"))
        self.chk_mono.SetLabel(i18n.t("settings_mono"))
        self.chk_mono.SetToolTip(i18n.t("settings_mono_tip"))
        self.chk_fade.SetLabel(i18n.t("settings_fade_next"))
        self.chk_fade.SetToolTip(i18n.t("settings_fade_next_tip"))
        self.chk_fade_pause.SetLabel(i18n.t("settings_fade_pause"))
        self.chk_fade_pause.SetToolTip(i18n.t("settings_fade_pause_tip"))
        self.fade_dur_label.SetLabel(i18n.t("settings_fade_dur"))
        self.spin_fade_dur.SetToolTip(i18n.t("settings_fade_dur_tip"))

        self.acc_box.SetLabel(i18n.t("settings_acc_box"))
        self.verb_label.SetLabel(i18n.t("settings_verbosity_label"))
        curr_verb_sel = self.choice_verbosity.GetSelection()
        self.choice_verbosity.Clear()
        self.choice_verbosity.AppendItems([
            i18n.t("settings_verb_verbose"),
            i18n.t("settings_verb_minimal"),
            i18n.t("settings_verb_silent")
        ])
        self.choice_verbosity.SetSelection(curr_verb_sel if curr_verb_sel != wx.NOT_FOUND else 0)
        self.choice_verbosity.SetToolTip(i18n.t("settings_verbosity_tip"))
        self.chk_audio_cues.SetLabel(i18n.t("settings_cues"))
        self.chk_audio_cues.SetToolTip(i18n.t("settings_cues_tip"))

        self.tools_box.SetLabel(i18n.t("settings_tools_box"))
        self.st_label.SetLabel(i18n.t("settings_sleep_label"))
        self.choice_sleep_timer.SetToolTip(i18n.t("settings_sleep_tip"))
        self.chk_obs_export.SetLabel(i18n.t("settings_obs"))
        self.chk_obs_export.SetToolTip(i18n.t("settings_obs_tip"))

        self.btn_ok.SetLabel(i18n.t("btn_save_apply"))
        self.btn_cancel.SetLabel(i18n.t("btn_cancel"))

        self.scroll_win.Layout()
        self.Layout()

    def on_change(self, event):
        self.get_settings()
        utils.save_config(self.config)
        event.Skip()

    def get_settings(self):
        # 1. General & Mode
        self.config["language"] = "en" if self.choice_language.GetSelection() == 1 else "id"
        self.config["app_mode"] = "advanced" if self.choice_app_mode.GetSelection() == 1 else "standard"
        self.config["resume_folder"] = self.chk_resume.GetValue()
        self.config["remember_window_pos"] = self.chk_remember_pos.GetValue()
        if hasattr(self, 'chk_check_updates'):
            self.config["check_updates_on_startup"] = self.chk_check_updates.GetValue()

        # 2. Playback & Navigation
        self.config["autoplay"] = self.chk_autoplay.GetValue()
        self.config["volume_step"] = self.spin_vol_step.GetValue()
        self.config["seek_step"] = self.spin_seek_step.GetValue()
        self.config["volume_max"] = 150 if self.choice_max_vol.GetSelection() == 1 else 100
        shuffle_state = self.chk_shuffle.GetValue()
        self.config["shuffle"] = shuffle_state
        self.config["shuffle_default"] = shuffle_state

        # 3. Audio & Equalizer
        eq_map = {0: "flat", 1: "bass_boost", 2: "treble_boost", 3: "vocal"}
        self.config["equalizer"] = eq_map.get(self.choice_equalizer.GetSelection(), "flat")
        self.config["normalize"] = self.chk_normalize.GetValue()
        self.config["mono"] = self.chk_mono.GetValue()
        self.config["fade_enabled"] = self.chk_fade.GetValue()
        self.config["fade_pause"] = self.chk_fade_pause.GetValue()
        self.config["fade_duration"] = self.spin_fade_dur.GetValue()

        # 4. Accessibility & Feedback
        verb_map = {0: "verbose", 1: "minimal", 2: "silent"}
        verb = verb_map.get(self.choice_verbosity.GetSelection(), "verbose")
        self.config["nvda_verbosity"] = verb
        self.config["speech_verbosity"] = verb
        self.config["nvda_verbose"] = (verb != "silent")
        cues_state = self.chk_audio_cues.GetValue()
        self.config["audio_cues"] = cues_state
        self.config["sound_cues"] = cues_state

        # 5. Tools & Sleep Timer
        st_map = {0: "Off", 1: "15m", 2: "30m", 3: "45m", 4: "60m"}
        st_min_map = {0: 0, 1: 15, 2: 30, 3: 45, 4: 60}
        timer_sel = self.choice_sleep_timer.GetSelection()
        self.config["sleep_timer"] = st_map.get(timer_sel, "Off")
        self.config["sleep_timer_minutes"] = st_min_map.get(timer_sel, 0)
        self.config["obs_export"] = self.chk_obs_export.GetValue()
        self.config["global_hotkeys"] = self.chk_global_hotkeys.GetValue()

        return self.config
