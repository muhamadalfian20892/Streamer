import wx
import os
import accessibility
import i18n


def show_getting_started_wizard(parent, config):
    """Shows the initial wizard for first-time users in active language."""
    lang = i18n.get_language()
    if lang == "en":
        message = (
            "Welcome to Streamer Audio Player.\n\n"
            "Would you like to open the user guide now?"
        )
        title = "Welcome"
        spoken = (
            "Welcome to Streamer Audio Player. Would you like to open the user guide now? "
            "Press Y for Yes, or N for No."
        )
    else:
        message = (
            "Selamat datang di Streamer Audio Player.\n\n"
            "Apakah Anda ingin membuka panduan penggunaan aplikasi sekarang?"
        )
        title = "Selamat Datang"
        spoken = (
            "Selamat datang di Streamer Audio Player. Apakah Anda ingin membuka panduan penggunaan sekarang? "
            "Tekan tombol Y untuk Ya, atau N untuk Tidak."
        )

    dlg = wx.MessageDialog(parent, message, title, wx.YES_NO | wx.ICON_QUESTION)
    dlg.SetName(title)

    accessibility.speak(spoken)

    result = dlg.ShowModal()
    dlg.Destroy()

    if result == wx.ID_YES:
        show_readme_dialog(parent)

    config["first_time_setup"] = False
    import utils
    utils.save_config(config)


def show_readme_dialog(parent):
    """Opens interactive guide dialog in the active language."""
    import sys
    lang = i18n.get_language()
    filename = "readme_en.txt" if lang == "en" else "readme.txt"
    base_dirs = [
        getattr(sys, '_MEIPASS', ''),
        os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else '',
        os.path.dirname(os.path.abspath(__file__)),
        os.getcwd()
    ]
    target_path = None
    for b in base_dirs:
        if b:
            p = os.path.join(b, filename)
            if os.path.exists(p):
                target_path = p
                break
    if not target_path:
        for b in base_dirs:
            if b:
                p = os.path.join(b, "readme.txt")
                if os.path.exists(p):
                    target_path = p
                    break

    content = ""
    if target_path and os.path.exists(target_path):
        try:
            with open(target_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            content = f"Error reading guide file: {e}"
    else:
        content = "Guide file not found."

    with ReadmeDialog(parent, content) as dlg:
        dlg.ShowModal()


class ReadmeDialog(wx.Dialog):
    def __init__(self, parent, content):
        title = i18n.t("menu_guide").split("\t")[0].replace("&", "")
        super().__init__(
            parent,
            title=title,
            size=(700, 560),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        )
        self.SetMinSize((480, 380))
        self.content = content
        self.init_ui(content)
        self.CenterOnParent()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.Destroy()

    def init_ui(self, content):
        panel = wx.Panel(self)
        panel.SetName(i18n.t("menu_guide").split("\t")[0].replace("&", ""))
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.text_ctrl = wx.TextCtrl(
            panel,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2,
            name=i18n.t("menu_guide").split("\t")[0].replace("&", "")
        )
        self.text_ctrl.SetName(i18n.t("menu_guide").split("\t")[0].replace("&", ""))
        self.text_ctrl.SetToolTip(
            "Use up and down arrow keys to read the guide document." if i18n.get_language() == "en"
            else "Gunakan tombol panah atas dan bawah untuk membaca isi panduan."
        )
        self.text_ctrl.SetValue(content)

        sizer.Add(self.text_ctrl, 1, wx.EXPAND | wx.ALL, 10)

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

        copy_label = "Copy Guide Text" if i18n.get_language() == "en" else "Salin Teks Panduan"
        self.btn_copy = wx.Button(panel, label=copy_label, name=copy_label)
        self.btn_copy.SetName(copy_label)
        self.btn_copy.SetToolTip(
            "Copy full guide text to computer clipboard." if i18n.get_language() == "en"
            else "Menyalin seluruh isi panduan ke papan klip komputer Anda."
        )
        self.btn_copy.Bind(wx.EVT_BUTTON, self.on_copy_text)
        btn_sizer.Add(self.btn_copy, 0, wx.RIGHT, 10)

        btn_sizer.AddStretchSpacer()

        close_label = i18n.t("btn_close")
        self.btn_close = wx.Button(panel, wx.ID_OK, label=close_label, name=close_label)
        self.btn_close.SetName(close_label)
        self.btn_close.SetToolTip(
            "Close this guide window." if i18n.get_language() == "en"
            else "Menutup jendela dialog panduan ini."
        )
        self.btn_close.SetDefault()
        btn_sizer.Add(self.btn_close, 0)

        sizer.Add(btn_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        panel.SetSizer(sizer)

        self.text_ctrl.SetFocus()

        open_announcement = (
            "User guide opened. Use arrow keys to read document." if i18n.get_language() == "en"
            else "Panduan penggunaan terbuka. Gunakan tombol panah untuk membaca isi dokumen."
        )
        accessibility.speak(open_announcement)

    def on_copy_text(self, event):
        """Copies guide content to clipboard."""
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(self.content))
            wx.TheClipboard.Close()
            msg = "Guide text copied to clipboard." if i18n.get_language() == "en" else "Teks panduan berhasil disalin ke papan klip."
            accessibility.speak(msg)
        else:
            msg = "Failed to access clipboard." if i18n.get_language() == "en" else "Gagal mengakses papan klip."
            accessibility.speak(msg)
