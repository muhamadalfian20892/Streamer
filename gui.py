import wx
import os
import sys
import random
import subprocess
import accessibility
import utils
from player import Player
import settings
import fading
from stream_features import StreamFeatures
import readme


class MediaDropTarget(wx.FileDropTarget):
    """Accessible drag-and-drop handler for audio/video files and folders."""
    def __init__(self, frame):
        super().__init__()
        self.frame = frame

    def OnDropFiles(self, x, y, filenames):
        if not filenames:
            return False
        first_item = filenames[0]
        if os.path.isdir(first_item):
            self.frame.load_folder(first_item)
            self.frame.speak(f"Folder dimuat dari seret dan lepas: {os.path.basename(first_item)}")
            return True
        elif os.path.isfile(first_item):
            parent = os.path.dirname(first_item)
            name = os.path.basename(first_item)
            self.frame.load_folder(parent)
            self.frame.select_file_by_name(name)
            self.frame.play_selected_item()
            self.frame.speak(f"File diputar dari seret dan lepas: {name}")
            return True
        return False


class AudioMetadataDialog(wx.Dialog):
    """Accessible technical metadata dialog."""
    def __init__(self, parent, file_path, player=None):
        super().__init__(parent, title="Rincian Informasi Audio", size=(520, 420))
        self.file_path = file_path
        self.player = player
        self.init_ui()
        self.CenterOnParent()

    def init_ui(self):
        panel = wx.Panel(self, name="Panel Rincian Metadata Audio")
        panel.SetName("Panel Rincian Metadata Audio")
        panel.SetToolTip("Panel informasi teknis dan properti file audio")
        sizer = wx.BoxSizer(wx.VERTICAL)

        info_lines = []
        filename = os.path.basename(self.file_path)
        info_lines.append(f"Nama File: {filename}")
        info_lines.append(f"Lokasi: {os.path.dirname(self.file_path)}")

        try:
            sz = os.path.getsize(self.file_path)
            if sz > 1024 * 1024:
                info_lines.append(f"Ukuran File: {sz / (1024 * 1024):.2f} MB")
            else:
                info_lines.append(f"Ukuran File: {sz / 1024:.1f} KB")
        except Exception:
            pass

        ext = os.path.splitext(self.file_path)[1].upper()
        info_lines.append(f"Format File: {ext.replace('.', '')}")

        if self.player and getattr(self.player, 'mp', None):
            try:
                dur = self.player.get_duration()
                if dur:
                    info_lines.append(f"Durasi: {utils.format_time(dur)}")
                audio_codec = getattr(self.player.mp, 'audio_codec_name', None)
                if audio_codec:
                    info_lines.append(f"Codec Audio: {audio_codec}")
                audio_params = getattr(self.player.mp, 'audio_params', None)
                if isinstance(audio_params, dict):
                    if 'samplerate' in audio_params:
                        info_lines.append(f"Sample Rate: {audio_params['samplerate']} Hz")
                    if 'channel-count' in audio_params:
                        info_lines.append(f"Kanal Suara: {audio_params['channel-count']}")
            except Exception:
                pass

        content = "\n".join(info_lines)

        self.text_ctrl = wx.TextCtrl(
            panel,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2,
            name="Informasi Teknis Audio"
        )
        self.text_ctrl.SetName("Informasi Teknis Audio")
        self.text_ctrl.SetToolTip("Gunakan tombol panah atas dan bawah untuk membaca informasi")
        self.text_ctrl.SetValue(content)
        sizer.Add(self.text_ctrl, 1, wx.EXPAND | wx.ALL, 10)

        btn_sizer = wx.StdDialogButtonSizer()
        close_btn = wx.Button(panel, wx.ID_OK, label="Tutup", name="Tutup Dialog Informasi")
        close_btn.SetName("Tutup Dialog Informasi")
        close_btn.SetToolTip("Tutup jendela rincian informasi audio")
        btn_sizer.AddButton(close_btn)
        btn_sizer.Realize()
        sizer.Add(btn_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, 10)

        panel.SetSizer(sizer)
        accessibility.speak(f"Informasi file audio {filename} terbuka.")


class BookmarksDialog(wx.Dialog):
    """Accessible bookmarks manager dialog."""
    def __init__(self, parent):
        super().__init__(parent, title="Pengelola Bookmark Waktu", size=(500, 420))
        self.parent_frame = parent
        self.config = parent.config
        self.bookmarks = self.config.get("bookmarks", {})
        self.init_ui()
        self.CenterOnParent()

    def init_ui(self):
        panel = wx.Panel(self, name="Panel Pengelola Bookmark")
        panel.SetName("Panel Pengelola Bookmark")
        panel.SetToolTip("Panel daftar bookmark penanda waktu")
        sizer = wx.BoxSizer(wx.VERTICAL)

        lbl = wx.StaticText(panel, label="Daftar Bookmark:")
        lbl.SetName("Label Daftar Bookmark")
        lbl.SetToolTip("Penanda waktu yang tersimpan untuk file saat ini")
        sizer.Add(lbl, 0, wx.LEFT | wx.TOP, 10)

        self.list_box = wx.ListBox(panel, name="Daftar Penanda Waktu", style=wx.LB_SINGLE)
        self.list_box.SetName("Daftar Penanda Waktu")
        self.list_box.SetToolTip("Daftar penanda waktu. Pilih untuk melompat atau menghapus.")
        sizer.Add(self.list_box, 1, wx.EXPAND | wx.ALL, 10)

        self.refresh_list()

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.add_btn = wx.Button(panel, label="Tambah Posisi Ini", name="Tambah Penanda")
        self.add_btn.SetName("Tambah Penanda")
        self.add_btn.SetToolTip("Simpan posisi waktu pemutaran saat ini sebagai bookmark")

        self.jump_btn = wx.Button(panel, label="Lompat ke Posisi", name="Lompat ke Bookmark")
        self.jump_btn.SetName("Lompat ke Bookmark")
        self.jump_btn.SetToolTip("Pindahkan pemutaran ke bookmark yang dipilih")

        self.del_btn = wx.Button(panel, label="Hapus", name="Hapus Bookmark")
        self.del_btn.SetName("Hapus Bookmark")
        self.del_btn.SetToolTip("Hapus bookmark yang dipilih dari daftar")

        close_btn = wx.Button(panel, wx.ID_CANCEL, label="Tutup", name="Tutup Bookmark")
        close_btn.SetName("Tutup Bookmark")
        close_btn.SetToolTip("Tutup jendela pengelola bookmark")

        btn_sizer.Add(self.add_btn, 0, wx.RIGHT, 5)
        btn_sizer.Add(self.jump_btn, 0, wx.RIGHT, 5)
        btn_sizer.Add(self.del_btn, 0, wx.RIGHT, 5)
        btn_sizer.Add(close_btn, 0)
        sizer.Add(btn_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, 10)

        self.add_btn.Bind(wx.EVT_BUTTON, self.on_add)
        self.jump_btn.Bind(wx.EVT_BUTTON, self.on_jump)
        self.del_btn.Bind(wx.EVT_BUTTON, self.on_delete)
        close_btn.Bind(wx.EVT_BUTTON, lambda e: self.Close())

        panel.SetSizer(sizer)

    def refresh_list(self):
        self.list_box.Clear()
        file_key = self.parent_frame.current_playing_file or "global"
        bm_list = self.bookmarks.get(file_key, [])
        for item in bm_list:
            pos = item.get("time", 0)
            note = item.get("label", "Bookmark")
            self.list_box.Append(f"{utils.format_time(pos)}: {note}", pos)
        if self.list_box.GetCount() > 0:
            self.list_box.SetSelection(0)

    def on_add(self, event):
        if not self.parent_frame.player:
            return
        pos = self.parent_frame.player.get_time_pos() or 0
        file_key = self.parent_frame.current_playing_file or "global"
        if file_key not in self.bookmarks:
            self.bookmarks[file_key] = []

        dlg = wx.TextEntryDialog(self, "Nama penanda:", "Tambah Bookmark", f"Penanda {len(self.bookmarks[file_key]) + 1}")
        if dlg.ShowModal() == wx.ID_OK:
            label = dlg.GetValue().strip() or "Bookmark"
            self.bookmarks[file_key].append({"time": pos, "label": label})
            self.config["bookmarks"] = self.bookmarks
            utils.save_config(self.config)
            self.refresh_list()
            accessibility.speak(f"Bookmark {label} disimpan pada waktu {utils.format_time(pos)}")
        dlg.Destroy()

    def on_jump(self, event):
        idx = self.list_box.GetSelection()
        if idx != wx.NOT_FOUND:
            pos = self.list_box.GetClientData(idx)
            if self.parent_frame.player:
                if hasattr(self.parent_frame.player, 'seek_absolute'):
                    self.parent_frame.player.seek_absolute(pos)
                else:
                    try:
                        self.parent_frame.player.mp.time_pos = pos
                    except Exception:
                        curr = self.parent_frame.player.get_time_pos() or 0
                        self.parent_frame.player.seek(pos - curr)
                accessibility.speak(f"Melompat ke posisi {utils.format_time(pos)}")

    def on_delete(self, event):
        idx = self.list_box.GetSelection()
        if idx != wx.NOT_FOUND:
            file_key = self.parent_frame.current_playing_file or "global"
            if file_key in self.bookmarks and idx < len(self.bookmarks[file_key]):
                del self.bookmarks[file_key][idx]
                self.config["bookmarks"] = self.bookmarks
                utils.save_config(self.config)
                self.refresh_list()
                accessibility.speak("Bookmark berhasil dihapus")


class StreamerFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Streamer App", size=(900, 680))

        self.config = utils.load_config()
        self.player = None
        self.fader = None
        self.current_folder = ""
        self.file_list_data = [] # Full list of files in current folder
        self.filtered_file_list_data = []
        self.current_search_query = ""
        self.current_view_filter = "All"
        self.current_playing_file = ""

        self.app_mode = self.config.get("app_mode", "standard")
        self.is_muted = self.config.get("muted", False)
        self.shuffle_enabled = self.config.get("shuffle", False)
        self.show_remaining_time = False
        self.is_user_seeking = False
        self.pre_mute_vol = self.config.get("volume", 100) or 100

        self.init_ui()
        self.init_menu_bar()
        self.init_shortcuts()
        self.bind_events()
        self.init_drag_and_drop()

        try:
            # Pass the video panel's window handle to the player
            wid = self.video_panel.GetHandle()
            self.player = Player(wid=wid)
            # Register MPV callbacks
            self.player.mp.observe_property('eof-reached', self.on_eof)
        except Exception as e:
            wx.MessageBox(f"Error initializing Player: {e}", "Error", wx.ICON_ERROR)

        self.stream_features = StreamFeatures(self)

        # Restore audio parameters from configuration
        self.restore_audio_settings()

        # Load initial timer
        self.player_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.player_timer)
        self.player_timer.Start(500)

        # Populate recent folders
        self.initial_folder_load()

        # Audio Devices
        self.refresh_audio_devices()

        # Apply initial app mode
        self.set_app_mode(self.app_mode, speak=False)

        self.Bind(wx.EVT_CLOSE, self.on_close)

        # Check for first time setup
        if self.config.get("first_time_setup", True):
            wx.CallAfter(readme.show_getting_started_wizard, self, self.config)

    def speak(self, text):
        """Wrapper for accessibility.speak that respects the verbose setting."""
        if self.config.get("nvda_verbose", True):
            accessibility.speak(text)

    def on_close(self, event):
        if hasattr(self, 'stream_features'):
            self.stream_features.unregister_global_hotkeys()
        if self.fader:
            self.fader.cancel()
        if hasattr(self, 'player_timer') and self.player_timer.IsRunning():
            self.player_timer.Stop()
        if self.player and hasattr(self.player, 'mp'):
            try:
                self.player.mp.terminate()
            except Exception:
                pass
        event.Skip()

    def init_ui(self):
        panel = wx.Panel(self, name="Panel Kontrol Utama")
        panel.SetName("Panel Kontrol Utama")
        panel.SetToolTip("Area utama pemutar media")
        self.panel = panel

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Status Bar with 4 fields
        self.status_bar = self.CreateStatusBar(4)
        self.status_bar.SetName("Bilah Status")
        self.status_bar.SetStatusWidths([-3, -2, -2, -2])

        # --- Top Section: Navigation ---
        top_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.open_btn = wx.Button(panel, label="Buka Folder (Ctrl+O)", name="Buka Folder")
        self.open_btn.SetName("Buka Folder")
        self.open_btn.SetToolTip("Buka folder berisi file media untuk diputar (Ctrl+O)")
        top_sizer.Add(self.open_btn, 0, wx.ALL | wx.CENTER, 5)

        self.open_file_btn = wx.Button(panel, label="Buka File", name="Buka File Tunggal")
        self.open_file_btn.SetName("Buka File Tunggal")
        self.open_file_btn.SetToolTip("Pilih satu file media tertentu untuk diputar (Ctrl+Shift+O)")
        top_sizer.Add(self.open_file_btn, 0, wx.ALL | wx.CENTER, 5)

        self.settings_btn = wx.Button(panel, label="Pengaturan (Ctrl+P)", name="Pengaturan Aplikasi")
        self.settings_btn.SetName("Pengaturan Aplikasi")
        self.settings_btn.SetToolTip("Buka dialog preferensi dan pengaturan aplikasi (Ctrl+P)")
        top_sizer.Add(self.settings_btn, 0, wx.ALL | wx.CENTER, 5)

        self.recent_combo = wx.Choice(panel, choices=[], name="Daftar Folder Terkini")
        self.recent_combo.SetName("Daftar Folder Terkini")
        self.recent_combo.SetToolTip("Pilih folder yang baru saja dibuka sebelumnya")
        top_sizer.Add(self.recent_combo, 1, wx.ALL | wx.CENTER, 5)

        main_sizer.Add(top_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # --- Search and Filter Section ---
        search_sizer = wx.BoxSizer(wx.HORIZONTAL)

        search_label = wx.StaticText(panel, label="Cari:", name="Label Kotak Pencarian")
        search_label.SetName("Label Kotak Pencarian")
        search_label.SetToolTip("Label untuk kotak pencarian")

        self.search_ctrl = wx.SearchCtrl(panel, style=wx.TE_PROCESS_ENTER, name="Kotak Pencarian File")
        self.search_ctrl.SetName("Kotak Pencarian File")
        self.search_ctrl.SetToolTip("Ketik kata kunci untuk menyaring nama file secara instan")
        self.search_ctrl.ShowSearchButton(True)
        self.search_ctrl.ShowCancelButton(True)

        filter_label = wx.StaticText(panel, label="Filter Tampilan:", name="Label Filter Tampilan")
        filter_label.SetName("Label Filter Tampilan")
        filter_label.SetToolTip("Label untuk filter tampilan file dan folder")

        self.view_filter = wx.Choice(panel, choices=["All", "Files Only", "Folders Only"], name="Filter Tampilan File")
        self.view_filter.SetName("Filter Tampilan File")
        self.view_filter.SetToolTip("Saring tampilan antara semua item, hanya file media, atau hanya folder")
        self.view_filter.SetSelection(0)

        search_sizer.Add(search_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.LEFT, 5)
        search_sizer.Add(self.search_ctrl, 1, wx.EXPAND | wx.ALL, 5)
        search_sizer.Add(filter_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.LEFT, 5)
        search_sizer.Add(self.view_filter, 0, wx.EXPAND | wx.ALL, 5)

        main_sizer.Add(search_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # --- Middle Section: File List and Video Splitter ---
        self.splitter = wx.SplitterWindow(panel, name="Pemisah Daftar dan Video")
        self.splitter.SetName("Pemisah Daftar dan Video")
        self.splitter.SetToolTip("Pemisah antara daftar file dan layar video")

        self.list_ctrl = wx.ListCtrl(self.splitter, style=wx.LC_REPORT | wx.LC_SINGLE_SEL, name="Daftar File dan Folder")
        self.list_ctrl.SetName("Daftar File dan Folder")
        self.list_ctrl.SetToolTip("Daftar file dan folder. Tekan Spasi untuk putar atau jeda, Enter untuk buka.")
        self.list_ctrl.InsertColumn(0, "Nama File", width=380)

        self.video_panel = wx.Panel(self.splitter, name="Panel Tampilan Video")
        self.video_panel.SetName("Panel Tampilan Video")
        self.video_panel.SetToolTip("Area visual pemutaran video")
        self.video_panel.SetBackgroundColour(wx.BLACK)

        self.splitter.SplitVertically(self.list_ctrl, self.video_panel, 340)
        self.splitter.SetMinimumPaneSize(100)

        main_sizer.Add(self.splitter, 1, wx.EXPAND | wx.ALL, 5)

        # --- Bottom Section: Controls ---

        # 1. Progress and Time Row
        progress_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.time_btn = wx.Button(panel, label="00:00 / 00:00", style=wx.BU_EXACTFIT, name="Penunjuk Waktu Pemutaran")
        self.time_btn.SetName("Penunjuk Waktu Pemutaran")
        self.time_btn.SetToolTip("Waktu pemutaran. Klik atau tekan Spasi untuk beralih antara waktu berlalu dan sisa waktu.")
        progress_sizer.Add(self.time_btn, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)

        self.seek_slider = wx.Slider(panel, value=0, minValue=0, maxValue=1000, style=wx.SL_HORIZONTAL, name="Slider Posisi Putar")
        self.seek_slider.SetName("Slider Posisi Putar")
        self.seek_slider.SetToolTip("Geser atau gunakan tombol panah untuk mengatur posisi pemutaran")
        progress_sizer.Add(self.seek_slider, 1, wx.EXPAND)

        main_sizer.Add(progress_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 5)

        # 2. Playback Buttons Row
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.prev_btn = wx.Button(panel, label="Sebelumnya", name="Lagu Sebelumnya")
        self.prev_btn.SetName("Lagu Sebelumnya")
        self.prev_btn.SetToolTip("Putar file sebelumnya dalam daftar (Ctrl+Left)")

        self.rewind_btn = wx.Button(panel, label="-5s", name="Mundur 5 Detik")
        self.rewind_btn.SetName("Mundur 5 Detik")
        self.rewind_btn.SetToolTip("Mundur pemutaran 5 detik (Left)")

        self.play_btn = wx.Button(panel, label="Putar", name="Putar atau Jeda")
        self.play_btn.SetName("Putar atau Jeda")
        self.play_btn.SetToolTip("Mulai atau jeda pemutaran file (Spasi)")

        self.stop_btn = wx.Button(panel, label="Stop", name="Hentikan Pemutaran")
        self.stop_btn.SetName("Hentikan Pemutaran")
        self.stop_btn.SetToolTip("Hentikan pemutaran lagu saat ini (Ctrl+S)")

        self.forward_btn = wx.Button(panel, label="+5s", name="Maju 5 Detik")
        self.forward_btn.SetName("Maju 5 Detik")
        self.forward_btn.SetToolTip("Maju pemutaran 5 detik (Right)")

        self.next_btn = wx.Button(panel, label="Berikutnya", name="Lagu Berikutnya")
        self.next_btn.SetName("Lagu Berikutnya")
        self.next_btn.SetToolTip("Putar file berikutnya dalam daftar (Ctrl+Right)")

        self.mute_toggle = wx.ToggleButton(panel, label="Mute", name="Tombol Bisu")
        self.mute_toggle.SetName("Tombol Bisu")
        self.mute_toggle.SetToolTip("Matikan atau nyalakan suara audio (Ctrl+M)")

        self.loop_toggle = wx.ToggleButton(panel, label="Loop Mati", name="Tombol Pengulangan")
        self.loop_toggle.SetName("Tombol Pengulangan")
        self.loop_toggle.SetToolTip("Ulangi pemutaran file secara terus menerus (Ctrl+L)")

        self.shuffle_toggle = wx.ToggleButton(panel, label="Acak: Mati", name="Tombol Putar Acak")
        self.shuffle_toggle.SetName("Tombol Putar Acak")
        self.shuffle_toggle.SetToolTip("Aktifkan atau nonaktifkan pemutaran lagu secara acak")

        btn_sizer.Add(self.prev_btn, 1, wx.ALL, 2)
        btn_sizer.Add(self.rewind_btn, 1, wx.ALL, 2)
        btn_sizer.Add(self.play_btn, 1, wx.ALL, 2)
        btn_sizer.Add(self.stop_btn, 1, wx.ALL, 2)
        btn_sizer.Add(self.forward_btn, 1, wx.ALL, 2)
        btn_sizer.Add(self.next_btn, 1, wx.ALL, 2)
        btn_sizer.Add(self.mute_toggle, 1, wx.ALL, 2)
        btn_sizer.Add(self.loop_toggle, 1, wx.ALL, 2)
        btn_sizer.Add(self.shuffle_toggle, 1, wx.ALL, 2)

        main_sizer.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # 3. Volume and Audio Device Row
        vol_dev_sizer = wx.BoxSizer(wx.HORIZONTAL)

        vol_label = wx.StaticText(panel, label="Volume:", name="Label Volume Suara")
        vol_label.SetName("Label Volume Suara")
        vol_label.SetToolTip("Label volume suara pemutar")

        max_vol = self.config.get("volume_max", 150)
        self.vol_slider = wx.Slider(panel, value=100, minValue=0, maxValue=max_vol, style=wx.SL_HORIZONTAL, name="Slider Volume Suara")
        self.vol_slider.SetName("Slider Volume Suara")
        self.vol_slider.SetToolTip("Atur tingkat volume suara (0 sampai 150%)")

        dev_label = wx.StaticText(panel, label="Perangkat Audio:", name="Label Perangkat Audio")
        dev_label.SetName("Label Perangkat Audio")
        dev_label.SetToolTip("Label perangkat output suara")

        self.device_choice = wx.Choice(panel, name="Pilihan Perangkat Audio")
        self.device_choice.SetName("Pilihan Perangkat Audio")
        self.device_choice.SetToolTip("Pilih perangkat output suara yang digunakan")

        vol_dev_sizer.Add(vol_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        vol_dev_sizer.Add(self.vol_slider, 1, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 15)
        vol_dev_sizer.Add(dev_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        vol_dev_sizer.Add(self.device_choice, 1, wx.ALIGN_CENTER_VERTICAL)

        main_sizer.Add(vol_dev_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # 4. Advanced Streamer Features Section (Hidden in Standard Mode)
        self.advanced_panel = wx.Panel(panel, name="Panel Fitur Lanjutan Streamer")
        self.advanced_panel.SetName("Panel Fitur Lanjutan Streamer")
        self.advanced_panel.SetToolTip("Panel fitur khusus streamer: penanda streaming, bookmark, dan efek audio")

        adv_box = wx.StaticBox(self.advanced_panel, label="Fitur Lanjutan Streamer")
        adv_box.SetName("Kotak Fitur Lanjutan Streamer")
        adv_sizer = wx.StaticBoxSizer(adv_box, wx.VERTICAL)

        adv_row1 = wx.BoxSizer(wx.HORIZONTAL)

        self.marker_btn = wx.Button(self.advanced_panel, label="Penanda Stream (F9)", name="Tambah Penanda Streaming")
        self.marker_btn.SetName("Tambah Penanda Streaming")
        self.marker_btn.SetToolTip("Catat stempel waktu streaming saat ini ke file stream_timestamps.txt (F9)")
        adv_row1.Add(self.marker_btn, 1, wx.ALL, 3)

        self.bookmark_btn = wx.Button(self.advanced_panel, label="Bookmarks", name="Pengelola Bookmark")
        self.bookmark_btn.SetName("Pengelola Bookmark")
        self.bookmark_btn.SetToolTip("Kelola dan lompat ke penanda waktu yang disimpan")
        adv_row1.Add(self.bookmark_btn, 1, wx.ALL, 3)

        self.inspector_btn = wx.Button(self.advanced_panel, label="Info Metadata", name="Inspektur Metadata Audio")
        self.inspector_btn.SetName("Inspektur Metadata Audio")
        self.inspector_btn.SetToolTip("Buka rincian informasi teknis dan metadata file audio")
        adv_row1.Add(self.inspector_btn, 1, wx.ALL, 3)

        self.obs_chk = wx.CheckBox(self.advanced_panel, label="Ekspor Teks OBS", name="Ekspor Teks OBS")
        self.obs_chk.SetName("Ekspor Teks OBS")
        self.obs_chk.SetToolTip("Tulis judul lagu yang sedang diputar ke file now_playing.txt untuk OBS Studio")
        self.obs_chk.SetValue(self.config.get("obs_export", False))
        adv_row1.Add(self.obs_chk, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        adv_sizer.Add(adv_row1, 0, wx.EXPAND | wx.ALL, 2)

        adv_row2 = wx.BoxSizer(wx.HORIZONTAL)

        eq_label = wx.StaticText(self.advanced_panel, label="Equalizer:", name="Label Preset Equalizer")
        eq_label.SetName("Label Preset Equalizer")
        eq_label.SetToolTip("Label pilihan equalizer")
        adv_row2.Add(eq_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)

        self.eq_choice = wx.Choice(self.advanced_panel, choices=["Flat", "Bass Boost", "Treble Boost", "Vocal"], name="Preset Equalizer")
        self.eq_choice.SetName("Preset Equalizer")
        self.eq_choice.SetToolTip("Pilih profil equalizer audio")
        adv_row2.Add(self.eq_choice, 1, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)

        self.chk_normalize = wx.CheckBox(self.advanced_panel, label="Normalisasi Audio", name="Normalisasi Audio")
        self.chk_normalize.SetName("Normalisasi Audio")
        self.chk_normalize.SetToolTip("Ratakan volume audio secara otomatis")
        self.chk_normalize.SetValue(self.config.get("normalize", False))
        adv_row2.Add(self.chk_normalize, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)

        self.chk_mono = wx.CheckBox(self.advanced_panel, label="Audio Mono", name="Konversi Audio Mono")
        self.chk_mono.SetName("Konversi Audio Mono")
        self.chk_mono.SetToolTip("Gabungkan kanal audio kiri dan kanan menjadi mono")
        self.chk_mono.SetValue(self.config.get("mono", False))
        adv_row2.Add(self.chk_mono, 0, wx.ALIGN_CENTER_VERTICAL, 5)

        adv_sizer.Add(adv_row2, 0, wx.EXPAND | wx.ALL, 2)

        self.advanced_panel.SetSizer(adv_sizer)
        main_sizer.Add(self.advanced_panel, 0, wx.EXPAND | wx.ALL, 5)

        panel.SetSizer(main_sizer)
        self.update_status_bar("Siap")

    def init_menu_bar(self):
        """Creates the comprehensive menu bar with accessible labels and shortcuts."""
        menu_bar = wx.MenuBar()

        # --- File Menu ---
        file_menu = wx.Menu()
        item_open_folder = file_menu.Append(wx.ID_OPEN, "Buka &Folder...\tCtrl+O", "Pilih folder media untuk dimuat")
        item_open_file = file_menu.Append(wx.ID_ANY, "Buka F&ile...\tCtrl+Shift+O", "Pilih file media tertentu")
        item_refresh = file_menu.Append(wx.ID_REFRESH, "&Segarkan Daftar\tF5", "Perbarui isi folder saat ini")
        file_menu.AppendSeparator()
        item_settings = file_menu.Append(wx.ID_PREFERENCES, "&Pengaturan...\tCtrl+P", "Buka jendela pengaturan dan preferensi")
        file_menu.AppendSeparator()
        item_exit = file_menu.Append(wx.ID_EXIT, "&Keluar\tAlt+F4", "Tutup aplikasi")
        menu_bar.Append(file_menu, "&File")

        # --- Playback Menu ---
        play_menu = wx.Menu()
        item_play_pause = play_menu.Append(wx.ID_ANY, "&Putar / Jeda\tSpace", "Mulai atau jeda pemutaran")
        item_stop = play_menu.Append(wx.ID_ANY, "&Berhenti\tCtrl+S", "Hentikan pemutaran lagu saat ini")
        item_prev = play_menu.Append(wx.ID_ANY, "Lagu Se&belumnya\tCtrl+Left", "Putar lagu sebelumnya dalam daftar")
        item_next = play_menu.Append(wx.ID_ANY, "Lagu &Berikutnya\tCtrl+Right", "Putar lagu berikutnya dalam daftar")
        play_menu.AppendSeparator()
        item_rewind = play_menu.Append(wx.ID_ANY, "&Mundur 5 Detik", "Mundur pemutaran 5 detik")
        item_forward = play_menu.Append(wx.ID_ANY, "Ma&ju 5 Detik", "Maju pemutaran 5 detik")
        play_menu.AppendSeparator()
        self.menu_toggle_loop = play_menu.AppendCheckItem(wx.ID_ANY, "&Ulangi Lagu (Loop)\tCtrl+L", "Aktifkan pengulangan lagu")
        self.menu_toggle_shuffle = play_menu.AppendCheckItem(wx.ID_ANY, "Putar &Acak (Shuffle)", "Aktifkan pemutaran lagu acak")
        self.menu_toggle_mute = play_menu.AppendCheckItem(wx.ID_ANY, "&Bisu (Mute)\tCtrl+M", "Matikan atau hidupkan suara")
        menu_bar.Append(play_menu, "&Pemutaran")

        # --- Audio Menu ---
        audio_menu = wx.Menu()
        item_vol_up = audio_menu.Append(wx.ID_ANY, "&Naikkan Volume\tCtrl+Up", "Naikkan volume suara")
        item_vol_down = audio_menu.Append(wx.ID_ANY, "&Turunkan Volume\tCtrl+Down", "Turunkan volume suara")
        audio_menu.AppendSeparator()

        eq_menu = wx.Menu()
        self.menu_eq_flat = eq_menu.AppendRadioItem(wx.ID_ANY, "Datar (Flat)", "Profil equalizer standar")
        self.menu_eq_bass = eq_menu.AppendRadioItem(wx.ID_ANY, "Penguat Bass (Bass Boost)", "Tingkatkan nada rendah")
        self.menu_eq_treble = eq_menu.AppendRadioItem(wx.ID_ANY, "Penguat Treble (Treble Boost)", "Tingkatkan nada tinggi")
        self.menu_eq_vocal = eq_menu.AppendRadioItem(wx.ID_ANY, "Fokus Vokal (Vocal)", "Tingkatkan kejelasan vokal")
        audio_menu.AppendSubMenu(eq_menu, "Preset &Equalizer")

        self.menu_audio_norm = audio_menu.AppendCheckItem(wx.ID_ANY, "&Normalisasi Audio", "Ratakan kenyaringan audio otomatis")
        self.menu_audio_mono = audio_menu.AppendCheckItem(wx.ID_ANY, "Konversi &Mono", "Gabungkan suara stereo ke mono")
        menu_bar.Append(audio_menu, "&Audio")

        # --- View Menu ---
        view_menu = wx.Menu()
        self.menu_mode_standard = view_menu.AppendRadioItem(wx.ID_ANY, "Mode &Standar", "Tampilan kontrol pemutar media bersih")
        self.menu_mode_advanced = view_menu.AppendRadioItem(wx.ID_ANY, "Mode &Lanjutan", "Tampilkan fitur lanjutan streamer")
        view_menu.AppendSeparator()
        self.menu_view_all = view_menu.AppendRadioItem(wx.ID_ANY, "Tampilkan &Semua", "Tampilkan semua file dan folder")
        self.menu_view_files = view_menu.AppendRadioItem(wx.ID_ANY, "Hanya &File", "Sembunyikan folder dari daftar")
        self.menu_view_folders = view_menu.AppendRadioItem(wx.ID_ANY, "Hanya F&older", "Sembunyikan file dari daftar")
        view_menu.AppendSeparator()
        item_toggle_time = view_menu.Append(wx.ID_ANY, "Alihkan Tampilan &Waktu Sisa", "Beralih antara waktu berlalu dan sisa waktu")
        menu_bar.Append(view_menu, "&Tampilan")

        # --- Tools Menu ---
        tools_menu = wx.Menu()
        item_marker = tools_menu.Append(wx.ID_ANY, "&Tambah Penanda Streaming\tF9", "Catat stempel waktu streaming")
        item_bookmarks = tools_menu.Append(wx.ID_ANY, "Pengelola &Bookmark...", "Kelola dan lompat ke penanda waktu")
        item_inspector = tools_menu.Append(wx.ID_ANY, "&Inspektur Metadata Audio...", "Lihat rincian metadata teknis file audio")
        item_sleep = tools_menu.Append(wx.ID_ANY, "Pengatur Waktu &Tidur (Sleep Timer)...", "Buka dialog pengatur waktu tidur")
        tools_menu.AppendSeparator()
        item_open_folder_exp = tools_menu.Append(wx.ID_ANY, "Buka Folder di File &Explorer", "Buka lokasi folder saat ini di Windows Explorer")
        item_open_obs_txt = tools_menu.Append(wx.ID_ANY, "Buka now_playing.&txt", "Buka file output judul lagu OBS")
        menu_bar.Append(tools_menu, "&Alat")

        # --- Help Menu ---
        help_menu = wx.Menu()
        item_guide = help_menu.Append(wx.ID_HELP, "&Panduan Penggunaan\tF1", "Buka panduan lengkap aplikasi")
        item_wizard = help_menu.Append(wx.ID_ANY, "&Wizard Mulai Cepat...", "Tampilkan panduan untuk pengguna baru")
        help_menu.AppendSeparator()
        item_about = help_menu.Append(wx.ID_ABOUT, "&Tentang Streamer App", "Informasi versi dan pembuat aplikasi")
        menu_bar.Append(help_menu, "&Bantuan")

        self.SetMenuBar(menu_bar)

        # Menu Event Bindings
        self.Bind(wx.EVT_MENU, self.on_open_folder, item_open_folder)
        self.Bind(wx.EVT_MENU, self.on_open_file, item_open_file)
        self.Bind(wx.EVT_MENU, self.on_refresh_folder, item_refresh)
        self.Bind(wx.EVT_MENU, self.on_settings, item_settings)
        self.Bind(wx.EVT_MENU, lambda e: self.Close(), item_exit)

        self.Bind(wx.EVT_MENU, self.on_play_pause, item_play_pause)
        self.Bind(wx.EVT_MENU, self.on_stop, item_stop)
        self.Bind(wx.EVT_MENU, lambda e: self.play_previous_file(), item_prev)
        self.Bind(wx.EVT_MENU, lambda e: self.play_next_file(), item_next)
        self.Bind(wx.EVT_MENU, lambda e: self.on_seek(-5), item_rewind)
        self.Bind(wx.EVT_MENU, lambda e: self.on_seek(5), item_forward)
        self.Bind(wx.EVT_MENU, self.on_toggle_loop_menu, self.menu_toggle_loop)
        self.Bind(wx.EVT_MENU, self.on_toggle_shuffle_menu, self.menu_toggle_shuffle)
        self.Bind(wx.EVT_MENU, self.on_toggle_mute_menu, self.menu_toggle_mute)

        self.Bind(wx.EVT_MENU, lambda e: self.change_volume(1), item_vol_up)
        self.Bind(wx.EVT_MENU, lambda e: self.change_volume(-1), item_vol_down)
        self.Bind(wx.EVT_MENU, lambda e: self.apply_equalizer("Flat"), self.menu_eq_flat)
        self.Bind(wx.EVT_MENU, lambda e: self.apply_equalizer("Bass Boost"), self.menu_eq_bass)
        self.Bind(wx.EVT_MENU, lambda e: self.apply_equalizer("Treble Boost"), self.menu_eq_treble)
        self.Bind(wx.EVT_MENU, lambda e: self.apply_equalizer("Vocal"), self.menu_eq_vocal)
        self.Bind(wx.EVT_MENU, self.on_toggle_normalize_menu, self.menu_audio_norm)
        self.Bind(wx.EVT_MENU, self.on_toggle_mono_menu, self.menu_audio_mono)

        self.Bind(wx.EVT_MENU, lambda e: self.set_app_mode("standard"), self.menu_mode_standard)
        self.Bind(wx.EVT_MENU, lambda e: self.set_app_mode("advanced"), self.menu_mode_advanced)
        self.Bind(wx.EVT_MENU, lambda e: self.set_view_filter_selection("All"), self.menu_view_all)
        self.Bind(wx.EVT_MENU, lambda e: self.set_view_filter_selection("Files Only"), self.menu_view_files)
        self.Bind(wx.EVT_MENU, lambda e: self.set_view_filter_selection("Folders Only"), self.menu_view_folders)
        self.Bind(wx.EVT_MENU, self.on_toggle_time_display, item_toggle_time)

        self.Bind(wx.EVT_MENU, self.on_add_stream_marker, item_marker)
        self.Bind(wx.EVT_MENU, lambda e: self.show_bookmarks_dialog(), item_bookmarks)
        self.Bind(wx.EVT_MENU, lambda e: self.show_metadata_dialog(), item_inspector)
        self.Bind(wx.EVT_MENU, lambda e: self.stream_features.show_sleep_timer_dialog(), item_sleep)
        self.Bind(wx.EVT_MENU, lambda e: self.open_in_explorer(self.current_folder), item_open_folder_exp)
        self.Bind(wx.EVT_MENU, self.open_now_playing_file, item_open_obs_txt)

        self.Bind(wx.EVT_MENU, lambda e: readme.show_readme_dialog(self), item_guide)
        self.Bind(wx.EVT_MENU, lambda e: readme.show_getting_started_wizard(self, self.config), item_wizard)
        self.Bind(wx.EVT_MENU, self.on_about, item_about)

    def init_drag_and_drop(self):
        """Sets up drag-and-drop support for files and folders."""
        self.SetDropTarget(MediaDropTarget(self))
        self.panel.SetDropTarget(MediaDropTarget(self))
        self.list_ctrl.SetDropTarget(MediaDropTarget(self))

    def init_shortcuts(self):
        # Global shortcuts for the frame
        accel_tbl = wx.AcceleratorTable([
            (wx.ACCEL_CTRL, ord('O'), 101), # Open Folder
            (wx.ACCEL_CTRL | wx.ACCEL_SHIFT, ord('O'), 102), # Open File
            (wx.ACCEL_CTRL, ord('L'), 103), # Loop
            (wx.ACCEL_NORMAL, wx.WXK_F5, 104), # Refresh
            (wx.ACCEL_CTRL, ord('P'), 105), # Settings
            (wx.ACCEL_CTRL, ord('D'), 106), # Pin favorite
            (wx.ACCEL_CTRL, ord('S'), 107), # Stop
            (wx.ACCEL_CTRL, ord('M'), 108), # Mute
            (wx.ACCEL_NORMAL, wx.WXK_F1, 109), # Help Guide
            (wx.ACCEL_NORMAL, wx.WXK_F9, 110), # Stream marker
            (wx.ACCEL_CTRL | wx.ACCEL_SHIFT, wx.WXK_UP, 111), # Pitch up
            (wx.ACCEL_CTRL | wx.ACCEL_SHIFT, wx.WXK_DOWN, 112), # Pitch down
            (wx.ACCEL_CTRL | wx.ACCEL_SHIFT, wx.WXK_RIGHT, 113), # Speed up
            (wx.ACCEL_CTRL | wx.ACCEL_SHIFT, wx.WXK_LEFT, 114), # Speed down
        ])
        self.SetAcceleratorTable(accel_tbl)

        self.Bind(wx.EVT_MENU, self.on_open_folder, id=101)
        self.Bind(wx.EVT_MENU, self.on_open_file, id=102)
        self.Bind(wx.EVT_MENU, self.on_toggle_loop_shortcut, id=103)
        self.Bind(wx.EVT_MENU, self.on_refresh_folder, id=104)
        self.Bind(wx.EVT_MENU, self.on_settings, id=105)
        self.Bind(wx.EVT_MENU, lambda e: self.stream_features.pin_current_file(), id=106)
        self.Bind(wx.EVT_MENU, self.on_stop, id=107)
        self.Bind(wx.EVT_MENU, self.on_toggle_mute, id=108)
        self.Bind(wx.EVT_MENU, lambda e: readme.show_readme_dialog(self), id=109)
        self.Bind(wx.EVT_MENU, self.on_add_stream_marker, id=110)
        self.Bind(wx.EVT_MENU, lambda e: self.adjust_pitch(1), id=111)
        self.Bind(wx.EVT_MENU, lambda e: self.adjust_pitch(-1), id=112)
        self.Bind(wx.EVT_MENU, lambda e: self.adjust_speed(0.1), id=113)
        self.Bind(wx.EVT_MENU, lambda e: self.adjust_speed(-0.1), id=114)

    def bind_events(self):
        self.open_btn.Bind(wx.EVT_BUTTON, self.on_open_folder)
        self.open_file_btn.Bind(wx.EVT_BUTTON, self.on_open_file)
        self.settings_btn.Bind(wx.EVT_BUTTON, self.on_settings)
        self.recent_combo.Bind(wx.EVT_CHOICE, self.on_recent_selected)

        self.search_ctrl.Bind(wx.EVT_TEXT, self.on_search_text)
        self.search_ctrl.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.on_search_cancel)
        self.view_filter.Bind(wx.EVT_CHOICE, self.on_view_filter_change)

        # List Events
        self.list_ctrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_item_activated)
        self.list_ctrl.Bind(wx.EVT_CHAR_HOOK, self.on_list_key)
        self.list_ctrl.Bind(wx.EVT_CONTEXT_MENU, self.on_list_context_menu)
        self.list_ctrl.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.on_list_context_menu)

        # Playback Controls
        self.prev_btn.Bind(wx.EVT_BUTTON, lambda e: self.play_previous_file())
        self.rewind_btn.Bind(wx.EVT_BUTTON, lambda e: self.on_seek(-5))
        self.play_btn.Bind(wx.EVT_BUTTON, self.on_play_pause)
        self.stop_btn.Bind(wx.EVT_BUTTON, self.on_stop)
        self.forward_btn.Bind(wx.EVT_BUTTON, lambda e: self.on_seek(5))
        self.next_btn.Bind(wx.EVT_BUTTON, lambda e: self.play_next_file())
        self.mute_toggle.Bind(wx.EVT_TOGGLEBUTTON, self.on_toggle_mute)
        self.loop_toggle.Bind(wx.EVT_TOGGLEBUTTON, self.on_toggle_loop)
        self.shuffle_toggle.Bind(wx.EVT_TOGGLEBUTTON, self.on_toggle_shuffle)

        # Time and Seek Slider
        self.time_btn.Bind(wx.EVT_BUTTON, self.on_toggle_time_display)
        self.seek_slider.Bind(wx.EVT_SCROLL_THUMBTRACK, self.on_seek_thumbtrack)
        self.seek_slider.Bind(wx.EVT_SCROLL_THUMBRELEASE, self.on_seek_thumbrelease)
        self.seek_slider.Bind(wx.EVT_SCROLL_CHANGED, self.on_seek_changed)
        self.seek_slider.Bind(wx.EVT_SLIDER, self.on_seek_slider)

        # Volume and Device
        self.vol_slider.Bind(wx.EVT_SLIDER, self.on_volume_change)
        self.device_choice.Bind(wx.EVT_CHOICE, self.on_device_change)

        # Advanced Streamer Controls
        self.marker_btn.Bind(wx.EVT_BUTTON, self.on_add_stream_marker)
        self.bookmark_btn.Bind(wx.EVT_BUTTON, lambda e: self.show_bookmarks_dialog())
        self.inspector_btn.Bind(wx.EVT_BUTTON, lambda e: self.show_metadata_dialog())
        self.obs_chk.Bind(wx.EVT_CHECKBOX, self.on_toggle_obs_export)
        self.eq_choice.Bind(wx.EVT_CHOICE, self.on_eq_choice_changed)
        self.chk_normalize.Bind(wx.EVT_CHECKBOX, self.on_toggle_normalize_chk)
        self.chk_mono.Bind(wx.EVT_CHECKBOX, self.on_toggle_mono_chk)

        # Global key hook for frame
        self.Bind(wx.EVT_CHAR_HOOK, self.on_global_key)

    def restore_audio_settings(self):
        """Restores saved volume, audio device, loop, shuffle, and equalizer settings."""
        saved_vol = self.config.get("volume", 100)
        try:
            saved_vol = int(saved_vol)
        except (ValueError, TypeError):
            saved_vol = 100
        max_vol = self.config.get("volume_max", 150)
        saved_vol = max(0, min(max_vol, saved_vol))

        self.vol_slider.SetValue(saved_vol)
        self.pre_mute_vol = saved_vol if saved_vol > 0 else 100

        if self.is_muted:
            self.mute_toggle.SetValue(True)
            self.mute_toggle.SetLabel("Bisu")
            if hasattr(self, 'menu_toggle_mute'):
                self.menu_toggle_mute.Check(True)
            if self.player:
                self.player.set_volume(0, persist=False)
        else:
            self.mute_toggle.SetValue(False)
            self.mute_toggle.SetLabel("Mute")
            if hasattr(self, 'menu_toggle_mute'):
                self.menu_toggle_mute.Check(False)
            if self.player:
                self.player.set_volume(saved_vol, persist=False)

        saved_loop = self.config.get("loop", False)
        self.loop_toggle.SetValue(saved_loop)
        self.loop_toggle.SetLabel("Loop Hidup" if saved_loop else "Loop Mati")
        if hasattr(self, 'menu_toggle_loop'):
            self.menu_toggle_loop.Check(saved_loop)
        if self.player:
            self.player.set_loop(saved_loop)

        self.shuffle_toggle.SetValue(self.shuffle_enabled)
        self.shuffle_toggle.SetLabel("Acak: Hidup" if self.shuffle_enabled else "Acak: Mati")
        if hasattr(self, 'menu_toggle_shuffle'):
            self.menu_toggle_shuffle.Check(self.shuffle_enabled)

        # Equalizer
        saved_eq = self.config.get("equalizer", "flat")
        self.apply_equalizer(saved_eq, speak=False)

        # Normalization
        saved_norm = self.config.get("normalize", False)
        self.apply_normalization(saved_norm, speak=False)

        # Mono
        saved_mono = self.config.get("mono", False)
        self.apply_mono(saved_mono, speak=False)

    def set_app_mode(self, mode, speak=True):
        """Switches between 'standard' and 'advanced' modes."""
        self.app_mode = mode
        self.config["app_mode"] = mode
        utils.save_setting("app_mode", mode)

        is_adv = (mode == "advanced")
        self.advanced_panel.Show(is_adv)
        self.panel.Layout()

        if hasattr(self, 'menu_mode_standard'):
            self.menu_mode_standard.Check(mode == "standard")
        if hasattr(self, 'menu_mode_advanced'):
            self.menu_mode_advanced.Check(mode == "advanced")

        self.update_status_bar()
        mode_text = "Lanjutan" if is_adv else "Standar"
        if speak:
            self.speak(f"Mode aplikasi diubah ke {mode_text}")

    def update_status_bar(self, state=None):
        """Updates all 4 fields of the status bar cleanly."""
        if not hasattr(self, 'status_bar') or not self.status_bar:
            return

        if state is None:
            if self.player and self.player.is_playing():
                track = self.current_playing_file or "Lagu"
                state = f"Memutar: {track}"
            elif self.player and not getattr(self.player.mp, 'idle_active', getattr(self.player.mp, 'core_idle', True)):
                state = "Jeda"
            else:
                state = "Berhenti"

        count = len(self.filtered_file_list_data)
        vol = self.vol_slider.GetValue()
        vol_str = f"Vol: {vol}%"
        if self.is_muted:
            vol_str += " [Bisu]"

        mode_str = f"Mode: {'Lanjutan' if self.app_mode == 'advanced' else 'Standar'}"

        self.status_bar.SetStatusText(state, 0)
        self.status_bar.SetStatusText(f"Total: {count} item", 1)
        self.status_bar.SetStatusText(vol_str, 2)
        self.status_bar.SetStatusText(mode_str, 3)

    def initial_folder_load(self):
        recents = self.config.get("recent_folders", [])
        self.recent_combo.Clear()
        if recents:
            self.recent_combo.AppendItems(recents)

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

        self.config = utils.add_recent_folder(self.config, path)
        self.config["last_folder"] = path
        utils.save_config(self.config)

        recents = self.config.get("recent_folders", [])
        self.recent_combo.Clear()
        self.recent_combo.AppendItems(recents)

        self.list_ctrl.SetFocus()
        if self.list_ctrl.GetItemCount() > 0:
            self.list_ctrl.Select(0)
            self.list_ctrl.Focus(0)

        self.update_status_bar()
        self.speak(f"Folder dimuat. {len(self.filtered_file_list_data)} item.")

    def select_file_by_name(self, filename):
        for i, item in enumerate(self.filtered_file_list_data):
            if item[0].lower() == filename.lower():
                self.list_ctrl.Select(i)
                self.list_ctrl.Focus(i)
                self.list_ctrl.EnsureVisible(i)
                break

    def on_open_folder(self, event):
        dlg = wx.DirDialog(self, "Pilih sebuah folder media", defaultPath=self.current_folder)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.load_folder(path)
        dlg.Destroy()

    def on_open_file(self, event):
        wildcard = "File Media (*.mp3;*.wav;*.ogg;*.flac;*.m4a;*.mp4;*.mkv)|*.mp3;*.wav;*.ogg;*.flac;*.m4a;*.aac;*.wma;*.opus;*.mp4;*.mkv;*.avi;*.mov;*.wmv;*.webm|Semua File (*.*)|*.*"
        dlg = wx.FileDialog(self, "Pilih file media untuk diputar", defaultDir=self.current_folder, wildcard=wildcard, style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            parent = os.path.dirname(path)
            self.load_folder(parent)
            self.select_file_by_name(os.path.basename(path))
            self.play_selected_item()
        dlg.Destroy()

    def on_recent_selected(self, event):
        path = self.recent_combo.GetStringSelection()
        if path:
            self.load_folder(path)

    def on_refresh_folder(self, event):
        if self.current_folder:
            self.load_folder(self.current_folder)
            self.speak("Daftar folder disegarkan.")

    def on_settings(self, event):
        with settings.SettingsDialog(self, self.config) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                self.config = dlg.get_settings()
                utils.save_config(self.config)
                new_mode = self.config.get("app_mode", self.app_mode)
                if new_mode != self.app_mode:
                    self.set_app_mode(new_mode)
                self.speak("Pengaturan berhasil disimpan.")

    def on_search_text(self, event):
        self.current_search_query = self.search_ctrl.GetValue().lower()
        self.apply_filters()

    def on_search_cancel(self, event):
        self.search_ctrl.SetValue("")
        self.current_search_query = ""
        self.apply_filters()

    def set_view_filter_selection(self, filter_text):
        idx = self.view_filter.FindString(filter_text)
        if idx != wx.NOT_FOUND:
            self.view_filter.SetSelection(idx)
        self.current_view_filter = filter_text
        self.apply_filters()

    def on_view_filter_change(self, event):
        self.current_view_filter = self.view_filter.GetStringSelection()
        if hasattr(self, 'menu_view_all') and self.current_view_filter in ("All", "Semua"):
            self.menu_view_all.Check(True)
        elif hasattr(self, 'menu_view_files') and self.current_view_filter in ("Files Only", "Hanya File"):
            self.menu_view_files.Check(True)
        elif hasattr(self, 'menu_view_folders') and self.current_view_filter in ("Folders Only", "Hanya Folder"):
            self.menu_view_folders.Check(True)
        self.apply_filters()

    def apply_filters(self):
        self.list_ctrl.DeleteAllItems()
        self.filtered_file_list_data = []

        for item in self.file_list_data:
            filename, is_folder = item

            # View filter
            if self.current_view_filter in ("Files Only", "Hanya File") and is_folder:
                continue
            if self.current_view_filter in ("Folders Only", "Hanya Folder") and not is_folder:
                continue

            # Search filter
            if self.current_search_query and self.current_search_query not in filename.lower():
                continue

            self.filtered_file_list_data.append(item)

        for i, item in enumerate(self.filtered_file_list_data):
            self.list_ctrl.InsertItem(i, item[0])

        count = self.list_ctrl.GetItemCount()
        if count > 0:
            self.list_ctrl.Select(0)
            self.list_ctrl.Focus(0)
        self.update_status_bar()
        self.speak(f"Ketemu {count} file")

    def on_item_activated(self, event):
        """Called when pressing Enter or Double Click on a list item."""
        self.play_selected_item()

    def play_selected_item(self):
        selected = self.list_ctrl.GetFirstSelected()
        if selected == -1:
            self.speak("Tidak ada yang dipilih")
            return

        filename, is_folder = self.filtered_file_list_data[selected]
        full_path = os.path.join(self.current_folder, filename)

        if is_folder:
            # Navigate into directory
            self.load_folder(full_path)
        else:
            # Play file
            if not self.player:
                return

            fade_enabled = self.config.get("fade_enabled", False)
            fade_duration = self.config.get("fade_duration", 0.5)

            if not self.fader:
                self.fader = fading.AudioFader(self.player)

            self.current_playing_file = filename

            def on_started():
                self.speak(f"Memutar {filename}")
                self.update_play_button_label()
                self.SetTitle(f"Streamer App - {filename}")
                self.update_status_bar(state=f"Memutar: {filename}")
                if self.config.get("obs_export", False):
                    self.stream_features.export_now_playing(filename)

            if fade_enabled and self.player.is_playing() and fade_duration > 0:
                current_vol = self.vol_slider.GetValue()
                self.fader.fade_and_play(full_path, fade_duration, current_vol, on_complete=on_started)
            else:
                if self.fader:
                    self.fader.cancel()
                self.player.load(full_path)
                on_started()

    def on_eof(self, name, value):
        if value is True:
            if self.config.get("autoplay", False):
                wx.CallAfter(self.play_next_file)
            else:
                wx.CallAfter(self.update_status_bar, "Selesai")

    def play_previous_file(self):
        """Plays the previous audio track in the list."""
        if not self.filtered_file_list_data:
            self.speak("Daftar file kosong")
            return

        file_indices = [i for i, item in enumerate(self.filtered_file_list_data) if not item[1]]
        if not file_indices:
            self.speak("Tidak ada file audio dalam daftar")
            return

        selected = self.list_ctrl.GetFirstSelected()
        if selected in file_indices:
            curr_pos = file_indices.index(selected)
            if curr_pos > 0:
                target_idx = file_indices[curr_pos - 1]
            else:
                if self.config.get("loop", False):
                    target_idx = file_indices[-1]
                else:
                    if hasattr(accessibility, 'play_boundary_top'):
                        accessibility.play_boundary_top()
                    self.speak("Awal daftar lagu tercapai")
                    return
        else:
            target_idx = file_indices[0]

        self.list_ctrl.Select(selected, False) if selected != -1 else None
        self.list_ctrl.Select(target_idx)
        self.list_ctrl.Focus(target_idx)
        self.list_ctrl.EnsureVisible(target_idx)
        self.play_selected_item()

    def play_next_file(self):
        """Plays the next audio track in the list or a random one if shuffle is on."""
        if not self.filtered_file_list_data:
            self.speak("Daftar file kosong")
            return

        file_indices = [i for i, item in enumerate(self.filtered_file_list_data) if not item[1]]
        if not file_indices:
            self.speak("Tidak ada file audio dalam daftar")
            return

        selected = self.list_ctrl.GetFirstSelected()

        if self.shuffle_enabled and len(file_indices) > 1:
            choices = [i for i in file_indices if i != selected]
            target_idx = random.choice(choices)
        else:
            if selected in file_indices:
                curr_pos = file_indices.index(selected)
                if curr_pos + 1 < len(file_indices):
                    target_idx = file_indices[curr_pos + 1]
                else:
                    if self.config.get("loop", False):
                        target_idx = file_indices[0]
                    else:
                        if hasattr(accessibility, 'play_boundary_bottom'):
                            accessibility.play_boundary_bottom()
                        self.speak("Akhir daftar lagu tercapai")
                        return
            else:
                target_idx = file_indices[0]

        self.list_ctrl.Select(selected, False) if selected != -1 else None
        self.list_ctrl.Select(target_idx)
        self.list_ctrl.Focus(target_idx)
        self.list_ctrl.EnsureVisible(target_idx)
        self.play_selected_item()

    def on_stop(self, event=None):
        """Stops playback and resets state."""
        if not self.player:
            return
        if self.fader:
            self.fader.cancel()
        try:
            self.player.stop()
        except Exception:
            pass
        self.seek_slider.SetValue(0)
        self.time_btn.SetLabel("00:00 / 00:00")
        self.update_play_button_label()
        self.SetTitle("Streamer App")
        self.update_status_bar(state="Berhenti")
        self.speak("Pemutaran dihentikan")

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
                    self.speak("Jeda")
                    self.update_play_button_label()
                    self.update_status_bar(state="Jeda")

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

                self.player.set_volume(0, persist=False)
                self.player.pause()

                def on_resumed():
                    self.speak("Memutar")
                    self.update_play_button_label()
                    track = self.current_playing_file or "Lagu"
                    self.update_status_bar(state=f"Memutar: {track}")

                self.fader.fade_in_and_resume(fade_duration, current_vol, on_complete=on_resumed)
                return

        # Regular toggle
        if self.fader:
            self.fader.cancel()

        is_paused = self.player.pause()
        state_text = "Jeda" if is_paused else "Memutar"
        self.speak(state_text)
        self.update_play_button_label()
        self.update_status_bar(state=state_text)

    def update_play_button_label(self):
        if not hasattr(self, 'play_btn'):
            return
        if self.player and self.player.is_playing():
            self.play_btn.SetLabel("Jeda")
        else:
            self.play_btn.SetLabel("Putar")

    def on_toggle_loop_shortcut(self, event):
        state = self.loop_toggle.GetValue()
        self.loop_toggle.SetValue(not state)
        self.on_toggle_loop(None)

    def on_toggle_loop_menu(self, event):
        state = self.menu_toggle_loop.IsChecked()
        self.loop_toggle.SetValue(state)
        self.on_toggle_loop(None)

    def on_toggle_loop(self, event):
        if not self.player:
            return
        state = self.loop_toggle.GetValue()
        self.player.set_loop(state)
        self.config["loop"] = state
        utils.save_setting("loop", state)
        msg = "Loop Hidup" if state else "Loop Mati"
        self.loop_toggle.SetLabel(msg)
        if hasattr(self, 'menu_toggle_loop'):
            self.menu_toggle_loop.Check(state)
        spoken_msg = "Pengulangan diaktifkan" if state else "Pengulangan dinonaktifkan"
        self.speak(spoken_msg)

    def on_toggle_shuffle_menu(self, event):
        state = self.menu_toggle_shuffle.IsChecked()
        self.shuffle_toggle.SetValue(state)
        self.on_toggle_shuffle(None)

    def on_toggle_shuffle(self, event):
        self.shuffle_enabled = self.shuffle_toggle.GetValue()
        self.config["shuffle"] = self.shuffle_enabled
        utils.save_setting("shuffle", self.shuffle_enabled)
        label = "Acak: Hidup" if self.shuffle_enabled else "Acak: Mati"
        self.shuffle_toggle.SetLabel(label)
        if hasattr(self, 'menu_toggle_shuffle'):
            self.menu_toggle_shuffle.Check(self.shuffle_enabled)
        msg = "Putar acak diaktifkan" if self.shuffle_enabled else "Putar acak dinonaktifkan"
        self.speak(msg)

    def on_toggle_mute_menu(self, event):
        self.on_toggle_mute(None)

    def on_toggle_mute(self, event=None):
        """Toggles audio mute state."""
        if self.player:
            self.is_muted = self.player.toggle_mute(persist=True)
        else:
            self.is_muted = not self.is_muted
            utils.save_muted(self.is_muted)
        self.config["muted"] = self.is_muted

        if self.is_muted:
            self.mute_toggle.SetValue(True)
            self.mute_toggle.SetLabel("Bisu")
            if hasattr(self, 'menu_toggle_mute'):
                self.menu_toggle_mute.Check(True)
            self.speak("Audio dibisukan")
        else:
            self.mute_toggle.SetValue(False)
            self.mute_toggle.SetLabel("Mute")
            if hasattr(self, 'menu_toggle_mute'):
                self.menu_toggle_mute.Check(False)
            cur_vol = self.player.get_volume() if self.player else self.vol_slider.GetValue()
            self.speak(f"Audio aktif, volume {int(cur_vol)}%")

        self.update_status_bar()

    def on_toggle_time_display(self, event=None):
        """Toggles between elapsed time and remaining time display."""
        self.show_remaining_time = not self.show_remaining_time
        curr = self.player.get_time_pos() if self.player else 0
        dur = self.player.get_duration() if self.player else 0
        self.update_time_display(curr, dur)
        mode_text = "Menampilkan sisa waktu" if self.show_remaining_time else "Menampilkan waktu berlalu"
        self.speak(mode_text)

    def on_seek_thumbtrack(self, event):
        self.is_user_seeking = True
        if self.player:
            dur = self.player.get_duration() or 0
            if dur > 0:
                val = self.seek_slider.GetValue()
                preview_sec = (val / 1000.0) * dur
                self.update_time_display(preview_sec, dur)
        event.Skip()

    def on_seek_thumbrelease(self, event):
        self.is_user_seeking = False
        self.apply_seek_from_slider()
        event.Skip()

    def on_seek_changed(self, event):
        self.is_user_seeking = False
        self.apply_seek_from_slider()
        event.Skip()

    def on_seek_slider(self, event):
        # When user navigates slider with keyboard arrows
        if not wx.GetMouseState().LeftIsDown():
            self.apply_seek_from_slider()
        event.Skip()

    def apply_seek_from_slider(self):
        if not self.player:
            return
        dur = self.player.get_duration()
        if dur and dur > 0:
            val = self.seek_slider.GetValue()
            target_pos = (val / 1000.0) * dur
            if hasattr(self.player, 'seek_absolute'):
                self.player.seek_absolute(target_pos)
            else:
                try:
                    self.player.mp.time_pos = target_pos
                except Exception:
                    curr = self.player.get_time_pos() or 0
                    self.player.seek(target_pos - curr)
            self.update_time_display(target_pos, dur)
            self.speak(f"Posisi {utils.format_time(target_pos)}")

    def on_seek(self, seconds):
        if self.player:
            try:
                self.player.seek(seconds)
                curr = self.player.get_time_pos()
                if curr is not None:
                    self.speak(f"{utils.format_time(curr)}")
            except Exception:
                pass

    def change_volume(self, change):
        current = self.vol_slider.GetValue()
        step = self.config.get("volume_step", 1)
        max_vol = self.config.get("volume_max", 150)
        new_val = max(0, min(max_vol, current + (change * step)))
        self.vol_slider.SetValue(new_val)
        self.on_volume_change(None)
        self.speak(f"Volume {new_val}%")

    def on_volume_change(self, event):
        val = self.vol_slider.GetValue()
        if self.is_muted and val > 0:
            self.is_muted = False
            self.config["muted"] = False
            utils.save_muted(False)
            self.mute_toggle.SetValue(False)
            self.mute_toggle.SetLabel("Mute")
            if hasattr(self, 'menu_toggle_mute'):
                self.menu_toggle_mute.Check(False)

        if self.player:
            self.player.set_volume(val, persist=True)
        else:
            utils.save_volume(val)
        self.config["volume"] = val
        self.update_status_bar()

    def refresh_audio_devices(self):
        if not self.player:
            return

        devices = self.player.get_audio_devices(refresh=True)
        self.device_choice.Clear()
        saved_dev = self.config.get("last_audio_device", "auto")

        selected_idx = 0
        for i, dev in enumerate(devices):
            dev_id = dev.get('name', '')
            dev_label = dev.get('description', dev_id)
            self.device_choice.Append(dev_label, dev_id)
            if dev_id == saved_dev:
                selected_idx = i

        if self.device_choice.GetCount() > 0:
            self.device_choice.SetSelection(selected_idx)
            active_dev = self.device_choice.GetClientData(selected_idx)
            self.player.set_audio_device(active_dev, persist=False)

    def on_device_change(self, event):
        if not self.player:
            return
        idx = self.device_choice.GetSelection()
        if idx != wx.NOT_FOUND:
            dev_name = self.device_choice.GetClientData(idx)
            dev_desc = self.device_choice.GetString(idx)
            self.player.set_audio_device(dev_name, persist=True)
            self.config["last_audio_device"] = dev_name
            self.speak(f"Perangkat audio diatur ke {dev_desc}")

    def on_timer(self, event):
        if not self.player:
            return
        try:
            curr = self.player.get_time_pos()
            dur = self.player.get_duration()

            if curr is not None and dur is not None and dur > 0:
                if not self.is_user_seeking:
                    pct = int((curr / dur) * 1000)
                    self.seek_slider.SetValue(min(1000, max(0, pct)))
                self.update_time_display(curr, dur)
            elif curr is not None:
                self.update_time_display(curr, 0)
        except Exception:
            pass

    def update_time_display(self, curr, dur):
        curr_sec = curr if curr is not None else 0
        dur_sec = dur if dur is not None else 0

        if self.show_remaining_time and dur_sec > 0:
            rem = max(0, dur_sec - curr_sec)
            label = f"-{utils.format_time(rem)} / {utils.format_time(dur_sec)}"
        else:
            label = f"{utils.format_time(curr_sec)} / {utils.format_time(dur_sec)}"

        self.time_btn.SetLabel(label)

    def on_global_key(self, event):
        """Global shortcuts handling."""
        keycode = event.GetKeyCode()
        modifiers = event.GetModifiers()

        if wx.Window.FindFocus() == self.search_ctrl:
            event.Skip()
            return

        if modifiers == wx.MOD_CONTROL:
            if keycode == wx.WXK_UP:
                self.change_volume(1)
                return
            elif keycode == wx.WXK_DOWN:
                self.change_volume(-1)
                return
            elif keycode == wx.WXK_LEFT:
                self.play_previous_file()
                return
            elif keycode == wx.WXK_RIGHT:
                self.play_next_file()
                return

        event.Skip()

    def on_list_key(self, event):
        """Shortcuts specific to ListView focus."""
        keycode = event.GetKeyCode()

        if keycode == wx.WXK_SPACE:
            self.on_play_pause(None)
        elif keycode == wx.WXK_BACK:
            # Go up one level
            parent = os.path.dirname(self.current_folder)
            if parent and os.path.exists(parent):
                if parent != self.current_folder:
                    self.load_folder(parent)
                else:
                    if hasattr(accessibility, 'play_boundary_top'):
                        accessibility.play_boundary_top()
                    self.speak("Batas direktori teratas")
        elif keycode == wx.WXK_LEFT:
            step = self.config.get("seek_step", 5)
            self.on_seek(-step)
        elif keycode == wx.WXK_RIGHT:
            step = self.config.get("seek_step", 5)
            self.on_seek(step)
        else:
            event.Skip()

    def on_list_context_menu(self, event):
        """Presents context menu for selected item in ListCtrl."""
        selected = self.list_ctrl.GetFirstSelected()
        if selected == -1:
            return

        filename, is_folder = self.filtered_file_list_data[selected]
        full_path = os.path.join(self.current_folder, filename)

        menu = wx.Menu()
        item_play = menu.Append(wx.ID_ANY, "Buka / Putar\tEnter", "Buka folder atau putar file ini")
        item_pin = menu.Append(wx.ID_ANY, "Tambah ke Favorit\tCtrl+D", "Sematkan file ke daftar favorit")
        item_props = None
        if not is_folder:
            item_props = menu.Append(wx.ID_ANY, "Rincian Informasi Audio...", "Lihat metadata dan spesifikasi audio")
        item_explorer = menu.Append(wx.ID_ANY, "Buka di File Explorer", "Tampilkan lokasi file di Windows Explorer")
        item_copy = menu.Append(wx.ID_ANY, "Salin Jalur File", "Salin path lengkap ke papan klip")

        self.Bind(wx.EVT_MENU, lambda e: self.play_selected_item(), item_play)
        self.Bind(wx.EVT_MENU, lambda e: self.stream_features.pin_current_file(), item_pin)
        if item_props:
            self.Bind(wx.EVT_MENU, lambda e: self.show_metadata_dialog(full_path), item_props)
        self.Bind(wx.EVT_MENU, lambda e: self.open_in_explorer(full_path), item_explorer)
        self.Bind(wx.EVT_MENU, lambda e: self.copy_file_path(full_path), item_copy)

        self.PopupMenu(menu)
        menu.Destroy()

    def open_in_explorer(self, target_path):
        """Opens file location in Windows Explorer."""
        if not target_path or not os.path.exists(target_path):
            self.speak("Jalur tidak ditemukan")
            return
        norm_path = os.path.normpath(target_path)
        try:
            if os.path.isdir(norm_path):
                subprocess.Popen(f'explorer "{norm_path}"')
            else:
                subprocess.Popen(f'explorer /select,"{norm_path}"')
            self.speak("Membuka File Explorer")
        except Exception as e:
            self.speak(f"Gagal membuka explorer: {e}")

    def copy_file_path(self, target_path):
        """Copies file path to clipboard."""
        if not target_path:
            self.speak("Tidak ada jalur yang dipilih")
            return
        norm_path = os.path.normpath(target_path)
        try:
            if wx.TheClipboard.Open():
                wx.TheClipboard.SetData(wx.TextDataObject(norm_path))
                wx.TheClipboard.Close()
                self.speak("Jalur file berhasil disalin")
            else:
                self.speak("Gagal mengakses papan klip")
        except Exception:
            self.speak("Gagal menyalin jalur file")

    def show_metadata_dialog(self, file_path=None):
        """Shows technical metadata inspector dialog."""
        if not file_path:
            selected = self.list_ctrl.GetFirstSelected()
            if selected != -1:
                name, is_folder = self.filtered_file_list_data[selected]
                file_path = os.path.join(self.current_folder, name)
            elif self.current_playing_file and self.current_folder:
                file_path = os.path.join(self.current_folder, self.current_playing_file)

        if not file_path or not os.path.exists(file_path):
            self.speak("Pilih file terlebih dahulu")
            return

        if hasattr(self, 'stream_features'):
            if hasattr(self.stream_features, 'show_metadata_inspector'):
                self.stream_features.show_metadata_inspector(file_path)
                return
            elif hasattr(self.stream_features, 'show_metadata_dialog'):
                self.stream_features.show_metadata_dialog(file_path)
                return
            elif hasattr(self.stream_features, 'inspect_metadata'):
                self.stream_features.inspect_metadata(file_path)
                return

        dlg = AudioMetadataDialog(self, file_path, self.player)
        dlg.ShowModal()
        dlg.Destroy()

    def show_bookmarks_dialog(self, file_path=None):
        """Shows bookmarks manager dialog."""
        if not file_path:
            file_path = self.current_playing_file
            if file_path and self.current_folder:
                file_path = os.path.join(self.current_folder, file_path)

        if hasattr(self, 'stream_features'):
            if hasattr(self.stream_features, 'show_bookmarks_manager'):
                self.stream_features.show_bookmarks_manager(file_path)
                return
            elif hasattr(self.stream_features, 'show_bookmarks_dialog'):
                self.stream_features.show_bookmarks_dialog()
                return
            elif hasattr(self.stream_features, 'manage_bookmarks'):
                self.stream_features.manage_bookmarks()
                return

        dlg = BookmarksDialog(self)
        dlg.ShowModal()
        dlg.Destroy()

    def on_add_stream_marker(self, event=None):
        if hasattr(self, 'stream_features') and hasattr(self.stream_features, 'log_stream_marker'):
            self.stream_features.log_stream_marker()

    def on_toggle_obs_export(self, event):
        val = self.obs_chk.GetValue()
        self.config["obs_export"] = val
        utils.save_setting("obs_export", val)
        if val and self.current_playing_file:
            self.stream_features.export_now_playing(self.current_playing_file)
        self.speak("Ekspor OBS diaktifkan" if val else "Ekspor OBS dinonaktifkan")

    def on_eq_choice_changed(self, event):
        preset = self.eq_choice.GetStringSelection()
        self.apply_equalizer(preset)

    def apply_equalizer(self, preset, speak=True):
        preset_clean = preset.strip().lower().replace(" ", "_")
        self.config["equalizer"] = preset_clean
        utils.save_setting("equalizer", preset_clean)

        if hasattr(self, 'eq_choice'):
            for i in range(self.eq_choice.GetCount()):
                item_str = self.eq_choice.GetString(i).strip().lower().replace(" ", "_")
                if item_str == preset_clean:
                    self.eq_choice.SetSelection(i)
                    break

        if hasattr(self, 'menu_eq_flat') and preset_clean == "flat":
            self.menu_eq_flat.Check(True)
        elif hasattr(self, 'menu_eq_bass') and preset_clean == "bass_boost":
            self.menu_eq_bass.Check(True)
        elif hasattr(self, 'menu_eq_treble') and preset_clean == "treble_boost":
            self.menu_eq_treble.Check(True)
        elif hasattr(self, 'menu_eq_vocal') and preset_clean == "vocal":
            self.menu_eq_vocal.Check(True)

        if self.player:
            if hasattr(self.player, 'set_equalizer'):
                self.player.set_equalizer(preset_clean, persist=True)
            elif hasattr(self.player, 'mp'):
                try:
                    if preset_clean == "flat":
                        self.player.mp.af = ""
                    elif preset_clean == "bass_boost":
                        self.player.mp.af = "lavfi=[bass=g=7]"
                    elif preset_clean == "treble_boost":
                        self.player.mp.af = "lavfi=[treble=g=7]"
                    elif preset_clean == "vocal":
                        self.player.mp.af = "lavfi=[highpass=f=120,equalizer=f=1000:t=q:w=1.5:g=4,equalizer=f=3000:t=q:w=1.5:g=3]"
                except Exception:
                    pass
        if speak:
            self.speak(f"Equalizer diatur ke {preset}")

    def on_toggle_normalize_chk(self, event):
        val = self.chk_normalize.GetValue()
        self.apply_normalization(val)

    def on_toggle_normalize_menu(self, event):
        val = self.menu_audio_norm.IsChecked()
        self.apply_normalization(val)

    def apply_normalization(self, enabled, speak=True):
        self.config["normalize"] = enabled
        utils.save_setting("normalize", enabled)

        if hasattr(self, 'chk_normalize'):
            self.chk_normalize.SetValue(enabled)
        if hasattr(self, 'menu_audio_norm'):
            self.menu_audio_norm.Check(enabled)

        if self.player:
            if hasattr(self.player, 'set_normalize'):
                self.player.set_normalize(enabled, persist=True)
            elif hasattr(self.player, 'mp'):
                try:
                    self.player.mp.replaygain = 'track' if enabled else 'no'
                except Exception:
                    pass
        if speak:
            self.speak("Normalisasi audio diaktifkan" if enabled else "Normalisasi audio dinonaktifkan")

    def on_toggle_mono_chk(self, event):
        val = self.chk_mono.GetValue()
        self.apply_mono(val)

    def on_toggle_mono_menu(self, event):
        val = self.menu_audio_mono.IsChecked()
        self.apply_mono(val)

    def apply_mono(self, enabled, speak=True):
        self.config["mono"] = enabled
        utils.save_setting("mono", enabled)

        if hasattr(self, 'chk_mono'):
            self.chk_mono.SetValue(enabled)
        if hasattr(self, 'menu_audio_mono'):
            self.menu_audio_mono.Check(enabled)

        if self.player:
            if hasattr(self.player, 'set_mono'):
                self.player.set_mono(enabled, persist=True)
            elif hasattr(self.player, 'mp'):
                try:
                    self.player.mp.af = "lavfi=[pan=mono]" if enabled else ""
                except Exception:
                    pass
        if speak:
            self.speak("Audio mono diaktifkan" if enabled else "Audio stereo diaktifkan")

    def open_now_playing_file(self, event):
        path = os.path.abspath("now_playing.txt")
        if not os.path.exists(path):
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write("")
            except Exception:
                pass
        if os.path.exists(path):
            subprocess.Popen(f'notepad.exe "{path}"')
            self.speak("Membuka now_playing.txt")
        else:
            self.speak("File now_playing.txt belum dibuat")

    def on_about(self, event):
        msg = "Streamer App\nMedia player bersih dan aksesibel untuk streaming dan penggunaan harian.\nDirancang dengan dukungan pembaca layar penuh."
        dlg = wx.MessageDialog(self, msg, "Tentang Streamer App", wx.OK | wx.ICON_INFORMATION)
        self.speak("Tentang Streamer App. Media player bersih dan aksesibel.")
        dlg.ShowModal()
        dlg.Destroy()

    def adjust_pitch(self, change):
        if not self.player:
            return
        self.speak("Kontrol pitch memerlukan filter audio tambahan")

    def adjust_speed(self, change):
        if not self.player:
            return
        current_speed = getattr(self.player.mp, 'speed', 1.0)
        new_speed = max(0.25, min(4.0, current_speed + change))
        try:
            self.player.mp.speed = new_speed
            self.speak(f"Kecepatan {new_speed:.1f}x")
        except Exception:
            pass
