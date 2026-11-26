"""
Application updater module for Streamer App.
Provides background update checking and downloading.
Adheres strictly to antislop and humanizer guidelines:
No backend URLs or technical infrastructure are ever displayed in the UI.
All dialogs, labels, and speech messages use natural, humanized language.
"""

import os
import sys
import json
import urllib.request
import urllib.error
import threading
import subprocess
import wx

import i18n
import accessibility
import utils

CURRENT_VERSION = "2.2.0"

# Target repository details kept internal to backend logic
_REPO_OWNER = "muhamadalfian20892"
_REPO_NAME = "Streamer"
_RELEASES_API_URL = f"https://api.github.com/repos/{_REPO_OWNER}/{_REPO_NAME}/releases/latest"
_RAW_VERSION_URL = f"https://raw.githubusercontent.com/{_REPO_OWNER}/{_REPO_NAME}/main/version.json"
_DEFAULT_ARCHIVE_URL = f"https://github.com/{_REPO_OWNER}/{_REPO_NAME}/archive/refs/heads/main.zip"
_USER_AGENT = "StreamerApp/2.2 (Windows NT)"


def parse_version(ver_str):
    """Parses a version string like 'v2.1.0' or '2.0' into a tuple of integers."""
    if not ver_str:
        return (0,)
    clean = str(ver_str).strip().lstrip('vV')
    parts = []
    for piece in clean.split('.'):
        num_str = ""
        for ch in piece:
            if ch.isdigit():
                num_str += ch
            else:
                break
        parts.append(int(num_str) if num_str else 0)
    return tuple(parts)


def is_newer_version(remote_ver, local_ver=CURRENT_VERSION):
    """Compares remote version against local version."""
    return parse_version(remote_ver) > parse_version(local_ver)


def fetch_update_info():
    """
    Fetches the latest version metadata from repository backend silently.
    Returns a dictionary with update details or None on failure.
    Never exposes technical endpoints to callers.
    """
    req_headers = {
        "User-Agent": _USER_AGENT,
        "Accept": "application/json"
    }

    # 1. Try releases API
    try:
        req = urllib.request.Request(_RELEASES_API_URL, headers=req_headers)
        with urllib.request.urlopen(req, timeout=6) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode('utf-8'))
                tag_name = data.get("tag_name", "")
                download_url = data.get("zipball_url") or _DEFAULT_ARCHIVE_URL
                # Check for assets
                assets = data.get("assets", [])
                for asset in assets:
                    asset_url = asset.get("browser_download_url")
                    if asset_url and asset_url.endswith(".zip"):
                        download_url = asset_url
                        break
                notes = data.get("body", "").strip() or ""
                return {
                    "version": tag_name.lstrip('vV'),
                    "download_url": download_url,
                    "notes": notes,
                    "has_update": is_newer_version(tag_name, CURRENT_VERSION)
                }
    except Exception:
        pass

    # 2. Fallback to raw version.json
    try:
        req = urllib.request.Request(_RAW_VERSION_URL, headers=req_headers)
        with urllib.request.urlopen(req, timeout=6) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode('utf-8'))
                remote_ver = str(data.get("version", "0.0.0"))
                lang = i18n.get_language()
                notes_key = "release_notes_en" if lang == "en" else "release_notes_id"
                notes = data.get(notes_key) or data.get("release_notes", "")
                dl_url = data.get("download_url") or _DEFAULT_ARCHIVE_URL
                return {
                    "version": remote_ver,
                    "download_url": dl_url,
                    "notes": notes,
                    "has_update": is_newer_version(remote_ver, CURRENT_VERSION)
                }
    except Exception:
        pass

    return None


class DownloadProgressDialog(wx.Dialog):
    """Accessible download progress dialog."""
    def __init__(self, parent, download_url, target_path, on_finished):
        super().__init__(parent, title=i18n.t("updater_title"), size=(440, 200),
                         style=wx.DEFAULT_DIALOG_STYLE)
        self.download_url = download_url
        self.target_path = target_path
        self.on_finished = on_finished
        self.cancelled = False

        self.init_ui()
        self.CenterOnParent()
        self.start_download()

    def init_ui(self):
        panel = wx.Panel(self, name=i18n.t("updater_title"))
        panel.SetName(i18n.t("updater_title"))
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.status_lbl = wx.StaticText(panel, label=i18n.t("updater_downloading"), name=i18n.t("updater_downloading"))
        self.status_lbl.SetName(i18n.t("updater_downloading"))
        sizer.Add(self.status_lbl, 0, wx.ALL | wx.EXPAND, 15)

        self.gauge = wx.Gauge(panel, range=100, size=(-1, 24), style=wx.GA_HORIZONTAL, name=i18n.t("updater_downloading"))
        self.gauge.SetName(i18n.t("updater_downloading"))
        self.gauge.SetToolTip(i18n.t("updater_downloading"))
        sizer.Add(self.gauge, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 15)

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.cancel_btn = wx.Button(panel, wx.ID_CANCEL, label=i18n.t("btn_cancel"), name=i18n.t("btn_cancel"))
        self.cancel_btn.SetName(i18n.t("btn_cancel"))
        self.cancel_btn.SetToolTip(i18n.t("btn_cancel"))
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.on_cancel)
        btn_sizer.Add(self.cancel_btn, 0)

        sizer.Add(btn_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, 15)
        panel.SetSizer(sizer)

        accessibility.speak(i18n.t("updater_downloading"))

    def start_download(self):
        thread = threading.Thread(target=self._download_worker, daemon=True)
        thread.start()

    def _download_worker(self):
        req_headers = {"User-Agent": _USER_AGENT}
        req = urllib.request.Request(self.download_url, headers=req_headers)

        try:
            with urllib.request.urlopen(req, timeout=30) as response, open(self.target_path, 'wb') as out_file:
                total_length = response.headers.get('content-length')
                total_bytes = int(total_length) if total_length and total_length.isdigit() else 0
                downloaded_bytes = 0
                chunk_size = 32768
                last_reported_pct = -1

                while not self.cancelled:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    out_file.write(chunk)
                    downloaded_bytes += len(chunk)

                    if total_bytes > 0:
                        pct = int((downloaded_bytes / total_bytes) * 100)
                        if pct != last_reported_pct:
                            last_reported_pct = pct
                            dl_mb = downloaded_bytes / (1024 * 1024)
                            tot_mb = total_bytes / (1024 * 1024)
                            msg = i18n.t("updater_downloading_progress", pct=pct, dl_mb=dl_mb, total_mb=tot_mb)
                            wx.CallAfter(self._update_progress, pct, msg)
                    else:
                        dl_mb = downloaded_bytes / (1024 * 1024)
                        msg = i18n.t("updater_downloading_unknown", dl_mb=dl_mb)
                        wx.CallAfter(self._update_progress, 0, msg)

            if not self.cancelled:
                wx.CallAfter(self._on_complete, True, None)
            else:
                if os.path.exists(self.target_path):
                    try:
                        os.remove(self.target_path)
                    except Exception:
                        pass
                wx.CallAfter(self._on_complete, False, "CANCELLED")
        except Exception as e:
            if os.path.exists(self.target_path):
                try:
                    os.remove(self.target_path)
                except Exception:
                    pass
            wx.CallAfter(self._on_complete, False, str(e))

    def _update_progress(self, pct, label_text):
        if not self.cancelled:
            self.gauge.SetValue(pct)
            self.status_lbl.SetLabel(label_text)

    def _on_complete(self, success, err):
        self.Destroy()
        if self.on_finished:
            self.on_finished(success, self.target_path, err)

    def on_cancel(self, event):
        self.cancelled = True
        self.Destroy()


def check_for_updates_interactive(parent_frame):
    """
    Checks for updates and displays user-friendly accessible dialogs.
    Never exposes backend hostnames or endpoints in the UI.
    """
    if hasattr(parent_frame, 'speak'):
        parent_frame.speak(i18n.t("updater_checking"))

    def worker():
        info = fetch_update_info()
        wx.CallAfter(_handle_interactive_result, parent_frame, info)

    threading.Thread(target=worker, daemon=True).start()


def check_for_updates_silent(parent_frame):
    """
    Checks for updates silently on startup. Only notifies if a new update is found.
    """
    def worker():
        info = fetch_update_info()
        if info and info.get("has_update"):
            wx.CallAfter(_handle_interactive_result, parent_frame, info)

    threading.Thread(target=worker, daemon=True).start()


def _handle_interactive_result(parent_frame, info):
    if not parent_frame:
        return

    if info is None:
        if hasattr(parent_frame, 'speak'):
            parent_frame.speak(i18n.t("updater_error"))
        dlg = wx.MessageDialog(
            parent_frame,
            i18n.t("updater_error"),
            i18n.t("updater_title"),
            wx.OK | wx.ICON_WARNING
        )
        dlg.ShowModal()
        dlg.Destroy()
        return

    if not info.get("has_update"):
        msg = i18n.t("updater_up_to_date", ver=CURRENT_VERSION)
        if hasattr(parent_frame, 'speak'):
            parent_frame.speak(msg)
        dlg = wx.MessageDialog(
            parent_frame,
            msg,
            i18n.t("updater_title"),
            wx.OK | wx.ICON_INFORMATION
        )
        dlg.ShowModal()
        dlg.Destroy()
        return

    # Update is available
    new_ver = info.get("version", "2.0")
    notes = info.get("notes") or ""
    prompt_msg = i18n.t("updater_available_msg", new_ver=new_ver, notes=notes)

    if hasattr(parent_frame, 'speak'):
        parent_frame.speak(f"{i18n.t('updater_available_title')} v{new_ver}")

    dlg = wx.MessageDialog(
        parent_frame,
        prompt_msg,
        i18n.t("updater_available_title"),
        wx.YES_NO | wx.ICON_QUESTION
    )
    res = dlg.ShowModal()
    dlg.Destroy()

    if res == wx.ID_YES:
        _start_update_download(parent_frame, info)


def _start_update_download(parent_frame, info):
    download_url = info.get("download_url")
    if not download_url:
        return

    # Determine destination folder (user's Downloads folder)
    downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
    if not os.path.exists(downloads_dir):
        downloads_dir = os.getcwd()

    new_ver = info.get("version", "update")
    target_filename = f"Streamer-v{new_ver}.zip"
    target_path = os.path.join(downloads_dir, target_filename)

    def on_download_finished(success, saved_path, err):
        if success:
            msg = i18n.t("updater_complete_msg", path=saved_path)
            if hasattr(parent_frame, 'speak'):
                parent_frame.speak(i18n.t("updater_complete_title"))

            confirm = wx.MessageDialog(
                parent_frame,
                msg,
                i18n.t("updater_complete_title"),
                wx.YES_NO | wx.ICON_INFORMATION
            )
            ans = confirm.ShowModal()
            confirm.Destroy()

            if ans == wx.ID_YES:
                try:
                    norm_path = os.path.normpath(saved_path)
                    subprocess.Popen(f'explorer /select,"{norm_path}"')
                except Exception:
                    pass
        else:
            if err and err != "CANCELLED":
                fail_msg = i18n.t("updater_failed")
                if hasattr(parent_frame, 'speak'):
                    parent_frame.speak(fail_msg)
                err_dlg = wx.MessageDialog(
                    parent_frame,
                    fail_msg,
                    i18n.t("updater_title"),
                    wx.OK | wx.ICON_ERROR
                )
                err_dlg.ShowModal()
                err_dlg.Destroy()

    dlg = DownloadProgressDialog(parent_frame, download_url, target_path, on_download_finished)
    dlg.ShowModal()
