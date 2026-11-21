import os
import time
import datetime
import threading
import wx
import accessibility
import utils
import i18n

# Try to import keyboard for global hotkeys, fail gracefully if not available
try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False


def format_file_size(bytes_size):
    """Formats bytes into human readable file size string."""
    if not isinstance(bytes_size, (int, float)) or bytes_size < 0:
        return "Tidak diketahui"
    if bytes_size < 1024:
        return f"{bytes_size} B"
    elif bytes_size < 1024 * 1024:
        return f"{bytes_size / 1024:.1f} KB ({bytes_size:,} bytes)"
    elif bytes_size < 1024 * 1024 * 1024:
        return f"{bytes_size / (1024 * 1024):.2f} MB ({bytes_size:,} bytes)"
    else:
        return f"{bytes_size / (1024 * 1024 * 1024):.2f} GB ({bytes_size:,} bytes)"


def extract_audio_metadata(player, file_path=None):
    """
    Extracts rich audio metadata from MPV player and/or file on disk.
    Returns a dictionary of audio properties.
    """
    data = {
        "file_name": "",
        "file_path": "",
        "file_size": "Tidak diketahui",
        "format": "Tidak diketahui",
        "codec": "Tidak diketahui",
        "bitrate": "Tidak diketahui",
        "channels": "Tidak diketahui",
        "sample_rate": "Tidak diketahui",
        "duration": "Tidak diketahui",
        "title": "",
        "artist": "",
        "album": "",
    }

    resolved_path = file_path
    if not resolved_path and player and hasattr(player, 'mp'):
        resolved_path = getattr(player.mp, 'path', None)

    if resolved_path:
        data["file_path"] = str(resolved_path)
        data["file_name"] = os.path.basename(resolved_path)
        if os.path.exists(resolved_path):
            try:
                size_bytes = os.path.getsize(resolved_path)
                data["file_size"] = format_file_size(size_bytes)
            except Exception:
                pass
            _, ext = os.path.splitext(resolved_path)
            if ext:
                data["format"] = ext.lstrip('.').upper()

    if player and hasattr(player, 'mp'):
        mp = player.mp
        current_mp_path = getattr(mp, 'path', None)
        is_current_file = (not file_path) or (
            current_mp_path and resolved_path and 
            os.path.abspath(current_mp_path) == os.path.abspath(resolved_path)
        )

        if is_current_file:
            # Duration
            try:
                dur = getattr(mp, 'duration', None)
                if dur is not None and dur > 0:
                    data["duration"] = f"{utils.format_time(dur)} ({int(round(dur))} detik)"
            except Exception:
                pass

            # Format
            try:
                file_fmt = getattr(mp, 'file_format', None)
                if file_fmt:
                    data["format"] = str(file_fmt).upper()
            except Exception:
                pass

            # Codec
            try:
                codec = getattr(mp, 'audio_codec_name', getattr(mp, 'audio_codec', None))
                if codec:
                    data["codec"] = str(codec)
            except Exception:
                pass

            # Bitrate
            try:
                bitrate = getattr(mp, 'audio_bitrate', None)
                if bitrate is not None and bitrate > 0:
                    if bitrate > 1000:
                        data["bitrate"] = f"{int(round(bitrate / 1000))} kbps"
                    else:
                        data["bitrate"] = f"{int(bitrate)} bps"
            except Exception:
                pass

            # Audio params (channels, sample rate)
            try:
                params = getattr(mp, 'audio_params', None)
                if isinstance(params, dict):
                    ch_count = params.get('channel-count')
                    hr_ch = params.get('hr-channels') or params.get('channels')
                    if ch_count:
                        ch_desc = "Stereo" if ch_count == 2 else ("Mono" if ch_count == 1 else f"{ch_count} saluran")
                        if hr_ch and hr_ch != ch_desc:
                            data["channels"] = f"{ch_desc} ({hr_ch})"
                        else:
                            data["channels"] = ch_desc
                    elif hr_ch:
                        data["channels"] = str(hr_ch)

                    sr = params.get('samplerate')
                    if sr:
                        data["sample_rate"] = f"{sr} Hz"

                    if data["codec"] == "Tidak diketahui" and params.get('format'):
                        data["codec"] = str(params.get('format'))
            except Exception:
                pass

            # Metadata tags
            try:
                meta = getattr(mp, 'metadata', None)
                if isinstance(meta, dict):
                    data["title"] = meta.get("title") or meta.get("TITLE") or ""
                    data["artist"] = meta.get("artist") or meta.get("ARTIST") or ""
                    data["album"] = meta.get("album") or meta.get("ALBUM") or ""
            except Exception:
                pass

    return data


class AudioMetadataDialog(wx.Dialog):
    """Accessible Audio Metadata Inspector Dialog."""
    def __init__(self, parent, data_or_path, player=None):
        super().__init__(parent, title=i18n.t("meta_title"), size=(520, 480),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        if isinstance(data_or_path, dict):
            self.data = data_or_path
        else:
            self.data = extract_audio_metadata(player, data_or_path)
        self.report_str = self._build_report_text()
        self.init_ui()
        self.CentreOnParent()

        # Announce dialog opened to screen reader
        fname = self.data.get("file_name") or "Audio"
        accessibility.speak(i18n.t("spk_meta_opened", name=fname), level="minimal")

    def _build_report_text(self):
        lines = []
        if self.data.get("title"):
            lines.append(i18n.t("meta_title_tag", val=self.data['title']))
        if self.data.get("artist"):
            lines.append(i18n.t("meta_artist_tag", val=self.data['artist']))
        if self.data.get("album"):
            lines.append(i18n.t("meta_album_tag", val=self.data['album']))
        lines.append(i18n.t("meta_file_name", val=self.data.get('file_name', '-')))
        lines.append(i18n.t("meta_file_format", val=self.data.get('format', '-')))
        lines.append(i18n.t("meta_codec", val=self.data.get('codec', '-')))
        lines.append(f"Bitrate: {self.data.get('bitrate', '-')}")
        lines.append(i18n.t("meta_channels", val=self.data.get('channels', '-')))
        lines.append(i18n.t("meta_samplerate", val=self.data.get('sample_rate', '-')))
        lines.append(i18n.t("meta_duration", val=self.data.get('duration', '-')))
        lines.append(i18n.t("meta_file_size", val=self.data.get('file_size', '-')))
        lines.append(i18n.t("meta_file_loc", val=self.data.get('file_path', '-')))
        return "\n".join(lines)

    def init_ui(self):
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Header description
        fname = self.data.get("file_name") or "File Audio"
        header = wx.StaticText(panel, label=f"{i18n.t('meta_title')}: {fname}", name="Header Metadata")
        header.SetToolTip(i18n.t("btn_inspector_tip"))
        main_sizer.Add(header, 0, wx.ALL | wx.EXPAND, 10)

        # Multiline Read-Only TextCtrl for screen reader access
        self.text_ctrl = wx.TextCtrl(
            panel,
            value=self.report_str,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.BORDER_SUNKEN,
            name=i18n.t("meta_title")
        )
        self.text_ctrl.SetToolTip(i18n.t("btn_inspector_tip"))
        main_sizer.Add(self.text_ctrl, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        # Button row
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.copy_btn = wx.Button(panel, label=i18n.t("btn_copy_info"), name=i18n.t("btn_copy_info"))
        self.copy_btn.SetToolTip(i18n.t("btn_copy_info"))
        self.copy_btn.Bind(wx.EVT_BUTTON, self.on_copy)
        btn_sizer.Add(self.copy_btn, 0, wx.RIGHT, 10)

        self.close_btn = wx.Button(panel, wx.ID_CLOSE, label=i18n.t("btn_close"), name=i18n.t("btn_close"))
        self.close_btn.SetToolTip(i18n.t("btn_close"))
        self.close_btn.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_CLOSE))
        btn_sizer.Add(self.close_btn, 0)

        main_sizer.Add(btn_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, 10)

        panel.SetSizer(main_sizer)

        # Close on Escape
        self.Bind(wx.EVT_CHAR_HOOK, self.on_char_hook)

    def on_char_hook(self, event):
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_CLOSE)
        else:
            event.Skip()

    def on_copy(self, event):
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(self.report_str))
            wx.TheClipboard.Close()
            accessibility.speak(i18n.t("spk_meta_copied"), level="minimal")


class BookmarksDialog(wx.Dialog):
    """Accessible Bookmarks Manager Dialog."""
    def __init__(self, parent, stream_features=None, file_path=None):
        super().__init__(parent, title=i18n.t("bm_title"), size=(520, 420),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        if stream_features is not None and hasattr(stream_features, 'get_bookmarks_for_file'):
            self.stream_features = stream_features
            self.file_path = file_path or self.stream_features.get_current_file_path()
        else:
            if hasattr(parent, 'stream_features'):
                self.stream_features = parent.stream_features
            else:
                self.stream_features = StreamFeatures(parent)
            self.file_path = file_path or self.stream_features.get_current_file_path()

        self.init_ui()
        self.load_bookmarks()
        self.CentreOnParent()

        # Announce dialog opened
        count = len(self.stream_features.get_bookmarks_for_file(self.file_path))
        accessibility.speak(i18n.t("spk_bm_opened", count=count), level="minimal")

    def init_ui(self):
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # File header
        fname = os.path.basename(self.file_path) if self.file_path else i18n.t("spk_no_selection")
        header = wx.StaticText(panel, label=f"{i18n.t('bm_list_label')} {fname}", name="Header Bookmark")
        header.SetToolTip(i18n.t("btn_bookmarks_tip"))
        main_sizer.Add(header, 0, wx.ALL | wx.EXPAND, 10)

        # Bookmarks ListCtrl
        self.list_ctrl = wx.ListCtrl(
            panel,
            style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.BORDER_SUNKEN,
            name=i18n.t("bm_title")
        )
        self.list_ctrl.SetToolTip(i18n.t("btn_bookmarks_tip"))
        self.list_ctrl.InsertColumn(0, i18n.t("bm_col_num"), width=50)
        self.list_ctrl.InsertColumn(1, i18n.t("bm_col_time"), width=110)
        self.list_ctrl.InsertColumn(2, i18n.t("bm_col_label"), width=300)
        main_sizer.Add(self.list_ctrl, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        # Action Buttons
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.jump_btn = wx.Button(panel, label=i18n.t("btn_bm_jump"), name=i18n.t("btn_bm_jump"))
        self.jump_btn.SetToolTip(i18n.t("btn_bm_jump_tip"))
        self.jump_btn.Bind(wx.EVT_BUTTON, self.on_jump)
        btn_sizer.Add(self.jump_btn, 0, wx.RIGHT, 6)

        self.add_btn = wx.Button(panel, label=i18n.t("btn_bm_add"), name=i18n.t("btn_bm_add"))
        self.add_btn.SetToolTip(i18n.t("btn_bm_add_tip"))
        self.add_btn.Bind(wx.EVT_BUTTON, self.on_add)
        btn_sizer.Add(self.add_btn, 0, wx.RIGHT, 6)

        self.del_btn = wx.Button(panel, label=i18n.t("btn_bm_del"), name=i18n.t("btn_bm_del"))
        self.del_btn.SetToolTip(i18n.t("btn_bm_del_tip"))
        self.del_btn.Bind(wx.EVT_BUTTON, self.on_delete)
        btn_sizer.Add(self.del_btn, 0, wx.RIGHT, 6)

        self.clear_btn = wx.Button(panel, label=i18n.t("btn_bm_clear"), name=i18n.t("btn_bm_clear"))
        self.clear_btn.SetToolTip(i18n.t("btn_bm_clear_tip"))
        self.clear_btn.Bind(wx.EVT_BUTTON, self.on_clear_all)
        btn_sizer.Add(self.clear_btn, 0, wx.RIGHT, 6)

        self.close_btn = wx.Button(panel, wx.ID_CANCEL, label=i18n.t("btn_close"), name=i18n.t("btn_close"))
        self.close_btn.SetToolTip(i18n.t("btn_close"))
        self.close_btn.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_CANCEL))
        btn_sizer.Add(self.close_btn, 0)

        main_sizer.Add(btn_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, 10)

        panel.SetSizer(main_sizer)

        # Event bindings
        self.list_ctrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_jump)
        self.list_ctrl.Bind(wx.EVT_KEY_DOWN, self.on_list_key)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_char_hook)

    def load_bookmarks(self):
        self.list_ctrl.DeleteAllItems()
        bookmarks = self.stream_features.get_bookmarks_for_file(self.file_path)
        for i, bm in enumerate(bookmarks):
            idx = self.list_ctrl.InsertItem(i, str(i + 1))
            self.list_ctrl.SetItem(idx, 1, utils.format_time(bm.get("time", 0)))
            title = bm.get("title") or bm.get("label") or ""
            self.list_ctrl.SetItem(idx, 2, str(title))

        if bookmarks:
            self.list_ctrl.Select(0)
            self.list_ctrl.Focus(0)

    def on_list_key(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_DELETE:
            self.on_delete(None)
        elif keycode == wx.WXK_RETURN:
            self.on_jump(None)
        else:
            event.Skip()

    def on_char_hook(self, event):
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_CANCEL)
        else:
            event.Skip()

    def on_jump(self, event):
        selected = self.list_ctrl.GetFirstSelected()
        if selected == -1:
            accessibility.speak(i18n.t("spk_bm_select_first"), level="minimal")
            return

        bookmarks = self.stream_features.get_bookmarks_for_file(self.file_path)
        if 0 <= selected < len(bookmarks):
            target_time = bookmarks[selected].get("time", 0)
            self.stream_features.jump_to_bookmark(target_time, self.file_path)
            self.EndModal(wx.ID_OK)

    def on_add(self, event):
        if not self.file_path:
            accessibility.speak(i18n.t("spk_bm_no_active_file"), level="minimal")
            return

        curr_time = 0.0
        if self.stream_features.player:
            curr_time = self.stream_features.player.get_time_pos() or 0.0

        time_str = utils.format_time(curr_time)
        count = len(self.stream_features.get_bookmarks_for_file(self.file_path))

        dlg = wx.TextEntryDialog(
            self,
            i18n.t("bm_prompt_desc", time=time_str),
            i18n.t("bm_prompt_title"),
            value=f"Bookmark {count + 1} ({time_str})"
        )
        dlg.SetName(i18n.t("bm_prompt_title"))
        if dlg.ShowModal() == wx.ID_OK:
            title = dlg.GetValue().strip() or f"Bookmark {count + 1}"
            self.stream_features.save_bookmark(self.file_path, curr_time, title)
            self.load_bookmarks()
            new_idx = self.list_ctrl.GetItemCount() - 1
            if new_idx >= 0:
                self.list_ctrl.Select(new_idx)
                self.list_ctrl.Focus(new_idx)
        dlg.Destroy()

    def on_delete(self, event):
        selected = self.list_ctrl.GetFirstSelected()
        if selected == -1:
            accessibility.speak(i18n.t("spk_bm_select_first"), level="minimal")
            return

        self.stream_features.delete_bookmark(self.file_path, selected)
        self.load_bookmarks()
        total = self.list_ctrl.GetItemCount()
        if total > 0:
            next_sel = min(selected, total - 1)
            self.list_ctrl.Select(next_sel)
            self.list_ctrl.Focus(next_sel)

    def on_clear_all(self, event):
        bookmarks = self.stream_features.get_bookmarks_for_file(self.file_path)
        if not bookmarks:
            accessibility.speak(i18n.t("spk_bm_none"), level="minimal")
            return

        confirm = wx.MessageBox(
            i18n.t("bm_confirm_clear_msg"),
            i18n.t("bm_confirm_clear_title"),
            wx.YES_NO | wx.ICON_QUESTION,
            self
        )
        if confirm == wx.YES:
            self.stream_features.clear_all_bookmarks(self.file_path)
            self.load_bookmarks()


class SleepTimer:
    """Thread-safe background Sleep Timer with graceful audio fade out."""
    def __init__(self, frame, player):
        self.frame = frame
        self.player = player
        self._thread = None
        self._stop_event = threading.Event()
        self.duration_seconds = 0
        self.start_time = 0
        self.target_time = 0
        self.is_running = False

    def start(self, minutes):
        """Starts the sleep timer for the given duration in minutes."""
        self.cancel(silent=True)
        if minutes <= 0:
            return

        self.duration_seconds = int(minutes * 60)
        self.start_time = time.time()
        self.target_time = self.start_time + self.duration_seconds
        self._stop_event.clear()
        self.is_running = True

        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()
        accessibility.speak(i18n.t("spk_sleep_started", mins=minutes), level="minimal")

    def cancel(self, silent=False):
        """Cancels any running sleep timer."""
        if self.is_running:
            self._stop_event.set()
            self.is_running = False
            self.duration_seconds = 0
            self.target_time = 0
            if not silent:
                accessibility.speak(i18n.t("spk_sleep_cancelled"), level="minimal")

    def get_remaining_seconds(self):
        """Returns the number of seconds remaining until the timer triggers."""
        if not self.is_running:
            return 0
        rem = self.target_time - time.time()
        return max(0, int(rem))

    def get_remaining_str(self):
        """Returns remaining time formatted as MM:SS or HH:MM:SS."""
        rem = self.get_remaining_seconds()
        return utils.format_time(rem)

    def _worker(self):
        while not self._stop_event.is_set():
            rem = self.target_time - time.time()
            if rem <= 0:
                self.is_running = False
                wx.CallAfter(self._on_timer_triggered)
                break
            time.sleep(min(1.0, max(0.1, rem)))

    def _on_timer_triggered(self):
        """Fades audio or pauses/stops player when sleep timer completes."""
        if not self.player:
            return

        fade_enabled = self.frame.config.get("fade_enabled", False)
        fade_duration = self.frame.config.get("fade_duration", 0.5)

        def stop_playback():
            if hasattr(self.player, 'stop'):
                self.player.stop()
            elif hasattr(self.player, 'pause'):
                self.player.pause()
            accessibility.speak(i18n.t("spk_sleep_done"), level="minimal")

        if fade_enabled and fade_duration > 0 and hasattr(self.frame, 'fader') and self.frame.fader:
            current_vol = self.frame.vol_slider.GetValue() if hasattr(self.frame, 'vol_slider') else 100
            self.frame.fader.fade_out_and_pause(fade_duration, current_vol, on_complete=stop_playback)
        else:
            stop_playback()


class SleepTimerDialog(wx.Dialog):
    """Accessible Sleep Timer Dialog."""
    @classmethod
    def get_presets(cls):
        return [
            (i18n.t("sleep_opt_off"), 0),
            (i18n.t("sleep_opt_15"), 15),
            (i18n.t("sleep_opt_30"), 30),
            (i18n.t("sleep_opt_45"), 45),
            (i18n.t("sleep_opt_60"), 60),
            (i18n.t("sleep_opt_custom"), -1)
        ]

    def __init__(self, parent, sleep_timer):
        super().__init__(parent, title=i18n.t("sleep_title"), size=(420, 300),
                         style=wx.DEFAULT_DIALOG_STYLE)
        self.sleep_timer = sleep_timer
        self.presets = self.get_presets()
        self.init_ui()
        self.CentreOnParent()

        # Announce to screen reader
        status = self._get_status_text()
        accessibility.speak(f"{i18n.t('sleep_title')}. {status}", level="minimal")

    def _get_status_text(self):
        if self.sleep_timer.is_running:
            return i18n.t("sleep_status_active", time=self.sleep_timer.get_remaining_str())
        return i18n.t("sleep_status_idle")

    def init_ui(self):
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.status_label = wx.StaticText(panel, label=self._get_status_text(), name="Status Sleep Timer")
        self.status_label.SetToolTip("Status aktif atau sisa waktu sleep timer saat ini")
        main_sizer.Add(self.status_label, 0, wx.ALL | wx.EXPAND, 10)

        # Choice dropdown for presets
        preset_labels = [p[0] for p in self.presets]
        choice_label = wx.StaticText(panel, label=i18n.t("sleep_desc"), name="Label Pilihan Durasi")
        main_sizer.Add(choice_label, 0, wx.LEFT | wx.RIGHT, 10)

        self.choice = wx.Choice(panel, choices=preset_labels, name="Pilihan Durasi Sleep Timer")
        self.choice.SetToolTip(i18n.t("sleep_choice_tip"))
        self.choice.SetSelection(1) # Default to 15 minutes
        self.choice.Bind(wx.EVT_CHOICE, self.on_choice_changed)
        main_sizer.Add(self.choice, 0, wx.ALL | wx.EXPAND, 10)

        # Custom minutes SpinCtrl
        custom_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.custom_label = wx.StaticText(panel, label=i18n.t("sleep_custom_label"), name="Label Durasi Kustom")
        custom_sizer.Add(self.custom_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)

        self.custom_spin = wx.SpinCtrl(panel, min=1, max=360, initial=20, name="Durasi Kustom Menit")
        self.custom_spin.SetToolTip(i18n.t("sleep_custom_tip"))
        self.custom_spin.Enable(False)
        custom_sizer.Add(self.custom_spin, 1)

        main_sizer.Add(custom_sizer, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)

        # Buttons
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.apply_btn = wx.Button(panel, label=i18n.t("btn_sleep_start"), name=i18n.t("btn_sleep_start"))
        self.apply_btn.SetToolTip(i18n.t("btn_sleep_start"))
        self.apply_btn.Bind(wx.EVT_BUTTON, self.on_apply)
        btn_sizer.Add(self.apply_btn, 0, wx.RIGHT, 10)

        self.cancel_timer_btn = wx.Button(panel, label=i18n.t("btn_sleep_cancel"), name=i18n.t("btn_sleep_cancel"))
        self.cancel_timer_btn.SetToolTip(i18n.t("btn_sleep_cancel"))
        self.cancel_timer_btn.Bind(wx.EVT_BUTTON, self.on_cancel_timer)
        btn_sizer.Add(self.cancel_timer_btn, 0, wx.RIGHT, 10)

        self.close_btn = wx.Button(panel, wx.ID_CANCEL, label=i18n.t("btn_close"), name=i18n.t("btn_close"))
        self.close_btn.SetToolTip(i18n.t("btn_close"))
        self.close_btn.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_CANCEL))
        btn_sizer.Add(self.close_btn, 0)

        main_sizer.Add(btn_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, 10)

        panel.SetSizer(main_sizer)

        self.Bind(wx.EVT_CHAR_HOOK, self.on_char_hook)

    def on_char_hook(self, event):
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_CANCEL)
        else:
            event.Skip()

    def on_choice_changed(self, event):
        sel = self.choice.GetSelection()
        is_custom = (sel == len(self.presets) - 1)
        self.custom_spin.Enable(is_custom)

    def on_apply(self, event):
        sel = self.choice.GetSelection()
        _, minutes = self.presets[sel]
        if minutes == -1:
            minutes = self.custom_spin.GetValue()

        if minutes > 0:
            self.sleep_timer.start(minutes)
        else:
            self.sleep_timer.cancel()
        self.EndModal(wx.ID_OK)

    def on_cancel_timer(self, event):
        self.sleep_timer.cancel()
        self.status_label.SetLabel(self._get_status_text())


class StreamFeatures:
    """Manages streamer and enhanced audio playback features."""
    def __init__(self, app_frame):
        self.frame = app_frame
        self.config = self.frame.config
        self.player = self.frame.player
        self.soundboard_player = None
        
        self.is_ducked = False
        self.pre_duck_volume = 100
        
        # Background sleep timer
        self.sleep_timer = SleepTimer(self.frame, self.player)

        self.init_soundboard_player()
        if KEYBOARD_AVAILABLE and self.config.get("global_hotkeys", True):
            self.register_global_hotkeys()

    def init_soundboard_player(self):
        try:
            from player import Player
            self.soundboard_player = Player()
            self.soundboard_player.set_volume(self.config.get("volume", 100))
        except Exception as e:
            print(f"Error initializing soundboard player: {e}")

    def register_global_hotkeys(self):
        if not KEYBOARD_AVAILABLE:
            return
        try:
            # Ducking
            keyboard.add_hotkey('alt+d', self.toggle_duck)
            # Stream Marker
            keyboard.add_hotkey('f9', self.log_stream_marker)
            # Example soundboard slots
            for i in range(1, 10):
                keyboard.add_hotkey(f'alt+{i}', self.play_soundboard_slot, args=[str(i)])
        except Exception as e:
            print(f"Failed to register global hotkeys: {e}")

    def unregister_global_hotkeys(self):
        if KEYBOARD_AVAILABLE:
            try:
                keyboard.unhook_all()
            except Exception:
                pass
        # Cancel sleep timer background thread cleanly on exit
        if hasattr(self, 'sleep_timer') and self.sleep_timer:
            self.sleep_timer.cancel(silent=True)

    def export_now_playing(self, filename):
        if not self.config.get("obs_export", True):
            return
        try:
            with open("now_playing.txt", "w", encoding="utf-8") as f:
                f.write(filename)
        except Exception as e:
            print(f"Error writing to now_playing.txt: {e}")

    def log_stream_marker(self):
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open("stream_timestamps.txt", "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] Stream Marker Placed\n")
            accessibility.speak(i18n.t("spk_marker_saved"), level="minimal")
        except Exception as e:
            print(f"Error writing marker: {e}")

    def toggle_duck(self):
        if not self.player:
            return
        wx.CallAfter(self._do_duck)

    def _do_duck(self):
        if not self.player:
            return
        
        fade_enabled = self.config.get("fade_enabled", False)
        fade_duration = self.config.get("fade_duration", 0.5)
        
        if not self.frame.fader:
            import fading
            self.frame.fader = fading.AudioFader(self.player)
            
        if self.is_ducked:
            self.is_ducked = False
            target_vol = self.pre_duck_volume
            accessibility.speak(i18n.t("spk_audio_normal"), level="minimal")
        else:
            self.is_ducked = True
            self.pre_duck_volume = self.frame.vol_slider.GetValue()
            target_vol = min(self.config.get("duck_volume", 15), self.pre_duck_volume)
            accessibility.speak(i18n.t("spk_audio_ducked"), level="minimal")
            
        if fade_enabled and fade_duration > 0:
            start_vol = self.frame.vol_slider.GetValue()
            def on_step(vol):
                self.frame.vol_slider.SetValue(int(vol))
                self.frame.on_volume_change(None)
            self.frame.fader.fade_volume(fade_duration, start_vol, target_vol, on_step=on_step)
        else:
            if self.frame.fader:
                self.frame.fader.cancel()
            self.frame.vol_slider.SetValue(target_vol)
            self.frame.on_volume_change(None)

    def play_soundboard_slot(self, slot_key):
        soundboard_map = self.config.get("soundboard", {})
        file_path = soundboard_map.get(slot_key)
        if file_path and os.path.exists(file_path):
            if self.soundboard_player:
                wx.CallAfter(self.soundboard_player.load, file_path)
                accessibility.speak(f"Played sound {slot_key}", level="minimal")
        else:
            accessibility.speak(f"Slot {slot_key} empty", level="minimal")

    def pin_current_file(self):
        selected = self.frame.list_ctrl.GetFirstSelected()
        if selected == -1:
            accessibility.speak(i18n.t("spk_no_selection"), level="minimal")
            return
            
        filename, is_folder = self.frame.filtered_file_list_data[selected]
        full_path = os.path.join(self.frame.current_folder, filename)
        
        favorites = self.config.get("favorites", [])
        if full_path not in favorites:
            favorites.append(full_path)
            self.config["favorites"] = favorites
            utils.save_config(self.config)
            accessibility.speak(i18n.t("spk_fav_added", name=filename), level="minimal")
        else:
            accessibility.speak(i18n.t("spk_fav_exists", name=filename), level="minimal")

    # --- Metadata Inspector ---
    def get_current_file_path(self):
        """Resolves the currently playing or currently selected file path."""
        # 1. Check player current track
        if self.player and hasattr(self.player, 'mp'):
            path = getattr(self.player.mp, 'path', None)
            if path and os.path.exists(path):
                return path

        # 2. Check frame current_playing_file attribute if present
        if hasattr(self.frame, 'current_playing_file') and self.frame.current_playing_file:
            if os.path.exists(self.frame.current_playing_file):
                return self.frame.current_playing_file

        # 3. Check selected item in file list
        if hasattr(self.frame, 'list_ctrl') and hasattr(self.frame, 'filtered_file_list_data'):
            sel = self.frame.list_ctrl.GetFirstSelected()
            if sel != -1 and sel < len(self.frame.filtered_file_list_data):
                item = self.frame.filtered_file_list_data[sel]
                filename = item[0] if isinstance(item, (tuple, list)) else item
                full_path = os.path.join(self.frame.current_folder, filename)
                if os.path.exists(full_path):
                    return full_path

        return None

    def show_metadata_inspector(self, file_path=None):
        """Opens the Audio Metadata Inspector dialog."""
        target_path = file_path or self.get_current_file_path()
        data = extract_audio_metadata(self.player, target_path)
        dlg = AudioMetadataDialog(self.frame, data)
        dlg.ShowModal()
        dlg.Destroy()

    def show_metadata_dialog(self, file_path=None):
        """Alias for show_metadata_inspector."""
        self.show_metadata_inspector(file_path)

    def inspect_metadata(self, file_path=None):
        """Alias for show_metadata_inspector."""
        self.show_metadata_inspector(file_path)

    # --- Bookmarks Manager ---
    def get_bookmarks_for_file(self, file_path):
        """Retrieves list of bookmarks for a specific file, matching full or base path."""
        if not file_path:
            return []
        all_bookmarks = self.config.get("bookmarks", {})
        norm_path = os.path.normpath(file_path)
        base_name = os.path.basename(file_path)

        bm_list = all_bookmarks.get(norm_path) or all_bookmarks.get(base_name) or all_bookmarks.get(file_path) or []

        normalized = []
        for bm in bm_list:
            item = dict(bm)
            if "title" not in item and "label" in item:
                item["title"] = item["label"]
            elif "label" not in item and "title" in item:
                item["label"] = item["title"]
            normalized.append(item)
        return normalized

    def save_bookmark(self, file_path, timestamp, title):
        """Saves a bookmark timestamp and title for a file into config."""
        if not file_path:
            return
        all_bookmarks = self.config.setdefault("bookmarks", {})
        norm_path = os.path.normpath(file_path)
        bm_list = all_bookmarks.setdefault(norm_path, [])

        bm_entry = {
            "time": float(timestamp),
            "title": str(title),
            "label": str(title),
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        bm_list.append(bm_entry)
        bm_list.sort(key=lambda x: x["time"])
        self.config["bookmarks"] = all_bookmarks
        utils.save_config(self.config)

        accessibility.speak(i18n.t("spk_bookmark_added", time=utils.format_time(timestamp)), level="minimal")

    def delete_bookmark(self, file_path, index):
        """Deletes a bookmark by index for a file."""
        if not file_path:
            return
        all_bookmarks = self.config.get("bookmarks", {})
        norm_path = os.path.normpath(file_path)
        base_name = os.path.basename(file_path)

        target_key = norm_path if norm_path in all_bookmarks else (base_name if base_name in all_bookmarks else file_path)
        bm_list = all_bookmarks.get(target_key, [])

        if 0 <= index < len(bm_list):
            removed = bm_list.pop(index)
            self.config["bookmarks"] = all_bookmarks
            utils.save_config(self.config)
            accessibility.speak(i18n.t("spk_bookmark_deleted"), level="minimal")

    def clear_all_bookmarks(self, file_path):
        """Removes all bookmarks for a specific file."""
        if not file_path:
            return
        all_bookmarks = self.config.get("bookmarks", {})
        norm_path = os.path.normpath(file_path)
        base_name = os.path.basename(file_path)

        changed = False
        for key in (norm_path, base_name, file_path):
            if key in all_bookmarks:
                del all_bookmarks[key]
                changed = True

        if changed:
            self.config["bookmarks"] = all_bookmarks
            utils.save_config(self.config)
            accessibility.speak(i18n.t("spk_bm_cleared"), level="minimal")

    def jump_to_bookmark(self, seconds, file_path=None):
        """Seeks player to the bookmark timestamp."""
        if not self.player:
            return

        target_file = file_path or self.get_current_file_path()
        current_mp_path = getattr(self.player.mp, 'path', None) if hasattr(self.player, 'mp') else None

        if target_file and current_mp_path and os.path.abspath(target_file) != os.path.abspath(current_mp_path):
            self.player.load(target_file)
            time.sleep(0.05)

        self.player.mp.time_pos = float(seconds)
        accessibility.speak(i18n.t("spk_jump_to", time=utils.format_time(seconds)), level="minimal")

    def show_bookmarks_manager(self, file_path=None):
        """Opens the Bookmarks Manager dialog."""
        target_path = file_path or self.get_current_file_path()
        dlg = BookmarksDialog(self.frame, self, target_path)
        dlg.ShowModal()
        dlg.Destroy()

    def show_bookmarks_dialog(self, file_path=None):
        """Alias for show_bookmarks_manager."""
        self.show_bookmarks_manager(file_path)

    def manage_bookmarks(self, file_path=None):
        """Alias for show_bookmarks_manager."""
        self.show_bookmarks_manager(file_path)

    # --- Sleep Timer ---
    def set_sleep_timer(self, minutes):
        """Starts background sleep timer for given minutes."""
        self.sleep_timer.start(minutes)

    def cancel_sleep_timer(self):
        """Cancels background sleep timer."""
        self.sleep_timer.cancel()

    def get_sleep_timer_remaining(self):
        """Returns remaining seconds for sleep timer."""
        return self.sleep_timer.get_remaining_seconds()

    def show_sleep_timer_dialog(self):
        """Opens the Sleep Timer configuration dialog."""
        dlg = SleepTimerDialog(self.frame, self.sleep_timer)
        dlg.ShowModal()
        dlg.Destroy()
