import wx
import os
import accessibility

def show_getting_started_wizard(parent, config):
    """Menampilkan panduan awal bagi pengguna yang baru pertama kali menjalankan aplikasi."""
    message = (
        "Selamat datang di Streamer Audio Player.\n\n"
        "Apakah Anda ingin membuka panduan penggunaan aplikasi sekarang?"
    )
    dlg = wx.MessageDialog(
        parent,
        message,
        "Selamat Datang",
        wx.YES_NO | wx.ICON_QUESTION
    )
    dlg.SetName("Dialog Panduan Awal Selamat Datang")
    
    accessibility.speak(
        "Selamat datang di Streamer Audio Player. Apakah Anda ingin membuka panduan penggunaan sekarang? "
        "Tekan tombol Y untuk Ya, atau N untuk Tidak."
    )
    
    result = dlg.ShowModal()
    dlg.Destroy()
    
    if result == wx.ID_YES:
        show_readme_dialog(parent)
        
    config["first_time_setup"] = False
    import utils
    utils.save_config(config)

def show_readme_dialog(parent):
    """Membuka jendela dialog interaktif berisi panduan lengkap penggunaan."""
    readme_path = os.path.join(os.path.dirname(__file__), "readme.txt")
    content = "File readme.txt tidak ditemukan di direktori aplikasi."
    if os.path.exists(readme_path):
        try:
            with open(readme_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            content = f"Gagal membaca berkas panduan: {e}"

    with ReadmeDialog(parent, content) as dlg:
        dlg.ShowModal()

class ReadmeDialog(wx.Dialog):
    def __init__(self, parent, content):
        super().__init__(
            parent, 
            title="Panduan Penggunaan", 
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
        panel.SetName("Panel Utama Panduan")
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Read-only multi-line text control for optimal screen reader support
        self.text_ctrl = wx.TextCtrl(
            panel, 
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2, 
            name="Teks Dokumen Panduan Penggunaan"
        )
        self.text_ctrl.SetName("Teks Dokumen Panduan Penggunaan")
        self.text_ctrl.SetToolTip(
            "Area teks panduan penggunaan aplikasi. Gunakan tombol panah atas dan bawah untuk membaca isi panduan."
        )
        self.text_ctrl.SetValue(content)
        
        sizer.Add(self.text_ctrl, 1, wx.EXPAND | wx.ALL, 10)
        
        # Action buttons
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.btn_copy = wx.Button(
            panel, 
            label="Salin Teks Panduan", 
            name="Tombol Salin Teks Panduan"
        )
        self.btn_copy.SetName("Tombol Salin Teks Panduan")
        self.btn_copy.SetToolTip("Menyalin seluruh isi panduan ke papan klip (clipboard) komputer Anda.")
        self.btn_copy.Bind(wx.EVT_BUTTON, self.on_copy_text)
        btn_sizer.Add(self.btn_copy, 0, wx.RIGHT, 10)
        
        btn_sizer.AddStretchSpacer()
        
        self.btn_close = wx.Button(
            panel, 
            wx.ID_OK, 
            label="Tutup", 
            name="Tombol Tutup Panduan"
        )
        self.btn_close.SetName("Tombol Tutup Panduan")
        self.btn_close.SetToolTip("Menutup jendela dialog panduan ini.")
        self.btn_close.SetDefault()
        btn_sizer.Add(self.btn_close, 0)
        
        sizer.Add(btn_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        panel.SetSizer(sizer)
        
        # Focus text control initially so NVDA reads immediately
        self.text_ctrl.SetFocus()
        
        accessibility.speak(
            "Panduan penggunaan terbuka. Gunakan tombol panah untuk membaca isi dokumen."
        )

    def on_copy_text(self, event):
        """Menyalin isi panduan ke clipboard."""
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(self.content))
            wx.TheClipboard.Close()
            accessibility.speak("Teks panduan berhasil disalin ke papan klip.")
        else:
            accessibility.speak("Gagal mengakses papan klip.")
