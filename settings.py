import wx
import utils

class SettingsDialog(wx.Dialog):
    def __init__(self, parent, config):
        super().__init__(
            parent, 
            title="Pengaturan & Preferensi", 
            size=(520, 640),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        )
        self.SetMinSize((460, 420))
        self.config = config if config is not None else {}
        self.init_ui()
        self.CenterOnParent()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.Destroy()

    def init_ui(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Scrolled container so dialog fits well on any display resolution
        scroll_win = wx.ScrolledWindow(self, style=wx.VSCROLL | wx.TAB_TRAVERSAL)
        scroll_win.SetName("Area Pengaturan Bergulir")
        scroll_win.SetScrollRate(0, 15)
        content_sizer = wx.BoxSizer(wx.VERTICAL)

        # =========================================================================
        # 1. General & Mode (Umum & Mode)
        # =========================================================================
        gen_box = wx.StaticBox(scroll_win, label="Umum & Mode Aplikasi")
        gen_box.SetName("Bagian Umum dan Mode Aplikasi")
        gen_sizer = wx.StaticBoxSizer(gen_box, wx.VERTICAL)

        # Mode Choice (Standard vs Advanced)
        mode_row = wx.BoxSizer(wx.HORIZONTAL)
        mode_label = wx.StaticText(scroll_win, label="Mode Tampilan Aplikasi:")
        mode_label.SetName("Label Mode Tampilan Aplikasi")
        self.choice_app_mode = wx.Choice(
            scroll_win,
            choices=["Standard (Pemutar Audio Sederhana)", "Advanced (Fitur Lengkap Streamer)"],
            name="Pilihan Mode Aplikasi"
        )
        self.choice_app_mode.SetName("Pilihan Mode Aplikasi")
        self.choice_app_mode.SetToolTip(
            "Pilih Mode Standard untuk pemutar musik bersih tanpa alat streamer, atau Mode Advanced untuk fitur lengkap."
        )
        current_mode = str(self.config.get("app_mode", "standard")).lower()
        self.choice_app_mode.SetSelection(1 if current_mode == "advanced" else 0)
        mode_row.Add(mode_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        mode_row.Add(self.choice_app_mode, 1, wx.EXPAND)
        gen_sizer.Add(mode_row, 0, wx.EXPAND | wx.ALL, 6)

        # Resume last folder
        self.chk_resume = wx.CheckBox(
            scroll_win,
            label="Buka kembali folder terakhir saat aplikasi dimulai",
            name="Buka kembali folder terakhir saat aplikasi dimulai"
        )
        self.chk_resume.SetName("Buka kembali folder terakhir saat aplikasi dimulai")
        self.chk_resume.SetToolTip(
            "Jika dicentang, aplikasi akan memuat daftar lagu dari folder yang terakhir dibuka saat dijalankan kembali."
        )
        self.chk_resume.SetValue(bool(self.config.get("resume_folder", True)))
        gen_sizer.Add(self.chk_resume, 0, wx.ALL, 6)

        # Remember window position
        self.chk_remember_pos = wx.CheckBox(
            scroll_win,
            label="Ingat posisi dan ukuran jendela",
            name="Ingat posisi dan ukuran jendela"
        )
        self.chk_remember_pos.SetName("Ingat posisi dan ukuran jendela")
        self.chk_remember_pos.SetToolTip(
            "Menyimpan letak dan ukuran jendela aplikasi agar selalu terbuka di posisi yang sama."
        )
        self.chk_remember_pos.SetValue(bool(self.config.get("remember_window_pos", True)))
        gen_sizer.Add(self.chk_remember_pos, 0, wx.ALL, 6)

        content_sizer.Add(gen_sizer, 0, wx.EXPAND | wx.ALL, 8)

        # =========================================================================
        # 2. Playback & Navigation (Pemutaran & Navigasi)
        # =========================================================================
        pb_box = wx.StaticBox(scroll_win, label="Pemutaran & Navigasi")
        pb_box.SetName("Bagian Pemutaran dan Navigasi")
        pb_sizer = wx.StaticBoxSizer(pb_box, wx.VERTICAL)

        # Autoplay next track
        self.chk_autoplay = wx.CheckBox(
            scroll_win,
            label="Putar lagu berikutnya secara otomatis",
            name="Putar lagu berikutnya secara otomatis"
        )
        self.chk_autoplay.SetName("Putar lagu berikutnya secara otomatis")
        self.chk_autoplay.SetToolTip(
            "Melanjutkan pemutaran ke lagu berikutnya dalam daftar saat trek yang sedang diputar selesai."
        )
        self.chk_autoplay.SetValue(bool(self.config.get("autoplay", False)))
        pb_sizer.Add(self.chk_autoplay, 0, wx.ALL, 6)

        # Volume Step
        vol_step_row = wx.BoxSizer(wx.HORIZONTAL)
        vol_step_label = wx.StaticText(scroll_win, label="Langkah Perubahan Volume (%):")
        vol_step_label.SetName("Label Langkah Perubahan Volume")
        self.spin_vol_step = wx.SpinCtrl(
            scroll_win,
            min=1,
            max=25,
            initial=int(self.config.get("volume_step", 1)),
            name="Langkah perubahan volume persen"
        )
        self.spin_vol_step.SetName("Langkah perubahan volume persen")
        self.spin_vol_step.SetToolTip(
            "Besaran perubahan volume setiap kali menekan tombol pintasan volume (1 sampai 25 persen)."
        )
        vol_step_row.Add(vol_step_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        vol_step_row.Add(self.spin_vol_step, 1, wx.EXPAND)
        pb_sizer.Add(vol_step_row, 0, wx.EXPAND | wx.ALL, 6)

        # Seek Step
        seek_step_row = wx.BoxSizer(wx.HORIZONTAL)
        seek_step_label = wx.StaticText(scroll_win, label="Langkah Lompatan Durasi (detik):")
        seek_step_label.SetName("Label Langkah Lompatan Durasi")
        self.spin_seek_step = wx.SpinCtrl(
            scroll_win,
            min=1,
            max=60,
            initial=int(self.config.get("seek_step", 5)),
            name="Langkah lompatan durasi detik"
        )
        self.spin_seek_step.SetName("Langkah lompatan durasi detik")
        self.spin_seek_step.SetToolTip(
            "Jumlah detik untuk melompat maju atau mundur saat menavigasi durasi lagu (1 sampai 60 detik)."
        )
        seek_step_row.Add(seek_step_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        seek_step_row.Add(self.spin_seek_step, 1, wx.EXPAND)
        pb_sizer.Add(seek_step_row, 0, wx.EXPAND | wx.ALL, 6)

        # Max Volume Limit (100% or 150%)
        max_vol_row = wx.BoxSizer(wx.HORIZONTAL)
        max_vol_label = wx.StaticText(scroll_win, label="Batas Maksimal Volume:")
        max_vol_label.SetName("Label Batas Maksimal Volume")
        self.choice_max_vol = wx.Choice(
            scroll_win,
            choices=["100% (Batas Standar)", "150% (Penguatan Ekstra)"],
            name="Batas volume maksimal"
        )
        self.choice_max_vol.SetName("Batas volume maksimal")
        self.choice_max_vol.SetToolTip(
            "Pilih batas atas volume: 100% untuk batas normal atau 150% untuk penguatan suara ekstra."
        )
        max_vol_val = int(self.config.get("volume_max", 150))
        self.choice_max_vol.SetSelection(1 if max_vol_val > 100 else 0)
        max_vol_row.Add(max_vol_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        max_vol_row.Add(self.choice_max_vol, 1, wx.EXPAND)
        pb_sizer.Add(max_vol_row, 0, wx.EXPAND | wx.ALL, 6)

        # Shuffle Default
        self.chk_shuffle = wx.CheckBox(
            scroll_win,
            label="Aktifkan putar acak (Shuffle) secara default",
            name="Aktifkan putar acak secara default"
        )
        self.chk_shuffle.SetName("Aktifkan putar acak secara default")
        self.chk_shuffle.SetToolTip(
            "Mengaktifkan mode putar acak trek secara otomatis setiap kali membuka daftar musik."
        )
        shuffle_val = bool(self.config.get("shuffle", self.config.get("shuffle_default", False)))
        self.chk_shuffle.SetValue(shuffle_val)
        pb_sizer.Add(self.chk_shuffle, 0, wx.ALL, 6)

        content_sizer.Add(pb_sizer, 0, wx.EXPAND | wx.ALL, 8)

        # =========================================================================
        # 3. Audio & Equalizer (Audio & Equalizer)
        # =========================================================================
        audio_box = wx.StaticBox(scroll_win, label="Audio & Equalizer")
        audio_box.SetName("Bagian Audio dan Equalizer")
        audio_sizer = wx.StaticBoxSizer(audio_box, wx.VERTICAL)

        # Equalizer Preset
        eq_row = wx.BoxSizer(wx.HORIZONTAL)
        eq_label = wx.StaticText(scroll_win, label="Preset Equalizer:")
        eq_label.SetName("Label Preset Equalizer")
        self.choice_equalizer = wx.Choice(
            scroll_win,
            choices=["Flat (Netral)", "Bass Boost (Penguat Bass)", "Treble Boost (Penguat Treble)", "Vocal (Kejelasan Vokal)"],
            name="Preset Equalizer Audio"
        )
        self.choice_equalizer.SetName("Preset Equalizer Audio")
        self.choice_equalizer.SetToolTip(
            "Pilih profil preset equalizer audio untuk menyesuaikan keluaran nada suara musik."
        )
        cur_eq = str(self.config.get("equalizer", "flat")).lower()
        if "bass" in cur_eq:
            self.choice_equalizer.SetSelection(1)
        elif "treble" in cur_eq:
            self.choice_equalizer.SetSelection(2)
        elif "vocal" in cur_eq:
            self.choice_equalizer.SetSelection(3)
        else:
            self.choice_equalizer.SetSelection(0)
        eq_row.Add(eq_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        eq_row.Add(self.choice_equalizer, 1, wx.EXPAND)
        audio_sizer.Add(eq_row, 0, wx.EXPAND | wx.ALL, 6)

        # Normalization
        self.chk_normalize = wx.CheckBox(
            scroll_win,
            label="Normalisasi audio (penyetaraan volume otomatis)",
            name="Normalisasi audio otomatis"
        )
        self.chk_normalize.SetName("Normalisasi audio otomatis")
        self.chk_normalize.SetToolTip(
            "Menyeimbangkan tingkat kenyaringan antar lagu agar suara tidak mendadak terlalu pelan atau terlalu kencang."
        )
        self.chk_normalize.SetValue(bool(self.config.get("normalize", False)))
        audio_sizer.Add(self.chk_normalize, 0, wx.ALL, 6)

        # Mono Downmix
        self.chk_mono = wx.CheckBox(
            scroll_win,
            label="Ubah ke suara mono (Mono downmix)",
            name="Ubah ke suara mono"
        )
        self.chk_mono.SetName("Ubah ke suara mono")
        self.chk_mono.SetToolTip(
            "Menggabungkan saluran kiri dan kanan menjadi satu saluran suara mono."
        )
        self.chk_mono.SetValue(bool(self.config.get("mono", False)))
        audio_sizer.Add(self.chk_mono, 0, wx.ALL, 6)

        # Fading Controls (Smooth transitions)
        self.chk_fade = wx.CheckBox(
            scroll_win,
            label="Aktifkan Fade Out saat berganti lagu",
            name="Aktifkan Fade Out saat berganti lagu"
        )
        self.chk_fade.SetName("Aktifkan Fade Out saat berganti lagu")
        self.chk_fade.SetToolTip(
            "Mengecilkan volume secara perlahan sebelum berganti ke lagu berikutnya agar terdengar halus."
        )
        self.chk_fade.SetValue(bool(self.config.get("fade_enabled", False)))
        audio_sizer.Add(self.chk_fade, 0, wx.ALL, 6)

        self.chk_fade_pause = wx.CheckBox(
            scroll_win,
            label="Aktifkan Fade saat jeda dan melanjutkan lagu",
            name="Aktifkan Fade saat jeda dan melanjutkan lagu"
        )
        self.chk_fade_pause.SetName("Aktifkan Fade saat jeda dan melanjutkan lagu")
        self.chk_fade_pause.SetToolTip(
            "Mengecilkan volume halus saat jeda (Pause) dan menaikkannya kembali saat dilanjutkan (Play)."
        )
        self.chk_fade_pause.SetValue(bool(self.config.get("fade_pause", False)))
        audio_sizer.Add(self.chk_fade_pause, 0, wx.ALL, 6)

        fade_dur_row = wx.BoxSizer(wx.HORIZONTAL)
        fade_dur_label = wx.StaticText(scroll_win, label="Durasi Transisi Fade (detik):")
        fade_dur_label.SetName("Label Durasi Transisi Fade")
        self.spin_fade_dur = wx.SpinCtrlDouble(
            scroll_win,
            min=0.1,
            max=10.0,
            inc=0.1,
            initial=float(self.config.get("fade_duration", 0.5)),
            name="Durasi transisi fade detik"
        )
        self.spin_fade_dur.SetName("Durasi transisi fade detik")
        self.spin_fade_dur.SetToolTip(
            "Durasi proses peredupan volume audio dalam hitungan detik (0.1 hingga 10.0 detik)."
        )
        fade_dur_row.Add(fade_dur_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        fade_dur_row.Add(self.spin_fade_dur, 1, wx.EXPAND)
        audio_sizer.Add(fade_dur_row, 0, wx.EXPAND | wx.ALL, 6)

        content_sizer.Add(audio_sizer, 0, wx.EXPAND | wx.ALL, 8)

        # =========================================================================
        # 4. Accessibility & Feedback (Aksesibilitas & Umpan Balik)
        # =========================================================================
        acc_box = wx.StaticBox(scroll_win, label="Aksesibilitas & Umpan Balik")
        acc_box.SetName("Bagian Aksesibilitas dan Umpan Balik")
        acc_sizer = wx.StaticBoxSizer(acc_box, wx.VERTICAL)

        # NVDA Verbosity Level (Verbose, Minimal, Silent)
        verb_row = wx.BoxSizer(wx.HORIZONTAL)
        verb_label = wx.StaticText(scroll_win, label="Tingkat Pengumuman NVDA:")
        verb_label.SetName("Label Tingkat Pengumuman NVDA")
        self.choice_verbosity = wx.Choice(
            scroll_win,
            choices=["Verbose (Lengkap)", "Minimal (Penting Saja)", "Silent (Hening)"],
            name="Tingkat kejelasan ucapan NVDA"
        )
        self.choice_verbosity.SetName("Tingkat kejelasan ucapan NVDA")
        self.choice_verbosity.SetToolTip(
            "Atur seberapa sering pembaca layar mengumumkan perubahan volume, durasi, dan status lagu."
        )
        current_verb = str(self.config.get("nvda_verbosity", self.config.get("speech_verbosity", ""))).lower()
        if not current_verb:
            current_verb = "verbose" if self.config.get("nvda_verbose", True) else "silent"
        if "minimal" in current_verb:
            self.choice_verbosity.SetSelection(1)
        elif "silent" in current_verb:
            self.choice_verbosity.SetSelection(2)
        else:
            self.choice_verbosity.SetSelection(0)
        verb_row.Add(verb_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        verb_row.Add(self.choice_verbosity, 1, wx.EXPAND)
        acc_sizer.Add(verb_row, 0, wx.EXPAND | wx.ALL, 6)

        # Audio cues on list boundaries
        self.chk_audio_cues = wx.CheckBox(
            scroll_win,
            label="Sinyal audio (bip) pada batas awal dan akhir daftar",
            name="Sinyal audio pada batas daftar"
        )
        self.chk_audio_cues.SetName("Sinyal audio pada batas daftar")
        self.chk_audio_cues.SetToolTip(
            "Membunyikan nada bip pendek saat Anda mencapai batas atas atau batas bawah daftar file."
        )
        cues_val = bool(self.config.get("audio_cues", self.config.get("sound_cues", True)))
        self.chk_audio_cues.SetValue(cues_val)
        acc_sizer.Add(self.chk_audio_cues, 0, wx.ALL, 6)

        content_sizer.Add(acc_sizer, 0, wx.EXPAND | wx.ALL, 8)

        # =========================================================================
        # 5. Tools & Sleep Timer (Alat & Pengatur Waktu Tidur)
        # =========================================================================
        tools_box = wx.StaticBox(scroll_win, label="Alat & Pengatur Waktu Tidur")
        tools_box.SetName("Bagian Alat dan Pengatur Waktu Tidur")
        tools_sizer = wx.StaticBoxSizer(tools_box, wx.VERTICAL)

        # Sleep Timer Duration (Off, 15m, 30m, 45m, 60m)
        timer_row = wx.BoxSizer(wx.HORIZONTAL)
        timer_label = wx.StaticText(scroll_win, label="Timer Tidur (Sleep Timer):")
        timer_label.SetName("Label Timer Tidur")
        self.choice_sleep_timer = wx.Choice(
            scroll_win,
            choices=["Mati (Off)", "15 Menit", "30 Menit", "45 Menit", "60 Menit"],
            name="Durasi pengatur waktu tidur"
        )
        self.choice_sleep_timer.SetName("Durasi pengatur waktu tidur")
        self.choice_sleep_timer.SetToolTip(
            "Menghentikan pemutaran musik secara otomatis setelah rentang durasi waktu yang dipilih."
        )
        st_val = str(self.config.get("sleep_timer", "Off")).lower()
        if "15" in st_val:
            self.choice_sleep_timer.SetSelection(1)
        elif "30" in st_val:
            self.choice_sleep_timer.SetSelection(2)
        elif "45" in st_val:
            self.choice_sleep_timer.SetSelection(3)
        elif "60" in st_val:
            self.choice_sleep_timer.SetSelection(4)
        else:
            self.choice_sleep_timer.SetSelection(0)
        timer_row.Add(timer_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        timer_row.Add(self.choice_sleep_timer, 1, wx.EXPAND)
        tools_sizer.Add(timer_row, 0, wx.EXPAND | wx.ALL, 6)

        # OBS text export
        self.chk_obs_export = wx.CheckBox(
            scroll_win,
            label="Ekspor judul lagu yang sedang diputar untuk OBS (now_playing.txt)",
            name="Ekspor judul lagu untuk OBS"
        )
        self.chk_obs_export.SetName("Ekspor judul lagu untuk OBS")
        self.chk_obs_export.SetToolTip(
            "Menuliskan nama lagu yang aktif ke file now_playing.txt untuk integrasi overlay OBS Studio."
        )
        self.chk_obs_export.SetValue(bool(self.config.get("obs_export", False)))
        tools_sizer.Add(self.chk_obs_export, 0, wx.ALL, 6)

        # Global hotkeys (Stream Deck features)
        self.chk_global_hotkeys = wx.CheckBox(
            scroll_win,
            label="Aktifkan Hotkey Global Streamer (Alt+D ducking, F9 marker, dll.)",
            name="Aktifkan Hotkey Global Streamer"
        )
        self.chk_global_hotkeys.SetName("Aktifkan Hotkey Global Streamer")
        self.chk_global_hotkeys.SetToolTip(
            "Memungkinkan jalan pintas keyboard global untuk audio ducking dan penanda stream."
        )
        self.chk_global_hotkeys.SetValue(bool(self.config.get("global_hotkeys", True)))
        tools_sizer.Add(self.chk_global_hotkeys, 0, wx.ALL, 6)

        content_sizer.Add(tools_sizer, 0, wx.EXPAND | wx.ALL, 8)

        # Set content sizer onto scroll window
        scroll_win.SetSizer(content_sizer)
        main_sizer.Add(scroll_win, 1, wx.EXPAND | wx.ALL, 4)

        # =========================================================================
        # Dialog Buttons (OK, Cancel)
        # =========================================================================
        btn_sizer = wx.StdDialogButtonSizer()
        
        btn_ok = wx.Button(self, wx.ID_OK, label="Simpan")
        btn_ok.SetName("Tombol Simpan Pengaturan")
        btn_ok.SetToolTip("Simpan semua perubahan pengaturan dan tutup jendela dialog.")
        btn_ok.SetDefault()
        
        btn_cancel = wx.Button(self, wx.ID_CANCEL, label="Batal")
        btn_cancel.SetName("Tombol Batal")
        btn_cancel.SetToolTip("Batalkan perubahan dan tutup jendela dialog.")
        
        btn_sizer.AddButton(btn_ok)
        btn_sizer.AddButton(btn_cancel)
        btn_sizer.Realize()
        main_sizer.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 10)

        self.SetSizer(main_sizer)

        # Bind change events for auto-persisting
        self.choice_app_mode.Bind(wx.EVT_CHOICE, self.on_change)
        self.chk_resume.Bind(wx.EVT_CHECKBOX, self.on_change)
        self.chk_remember_pos.Bind(wx.EVT_CHECKBOX, self.on_change)
        
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

    def on_change(self, event):
        self.get_settings()
        utils.save_config(self.config)
        event.Skip()

    def get_settings(self):
        # 1. General & Mode
        self.config["app_mode"] = "advanced" if self.choice_app_mode.GetSelection() == 1 else "standard"
        self.config["resume_folder"] = self.chk_resume.GetValue()
        self.config["remember_window_pos"] = self.chk_remember_pos.GetValue()

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
