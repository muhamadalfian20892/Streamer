import wx
import os
import accessibility

def show_getting_started_wizard(parent, config):
    """Shows the getting started wizard for first-time users."""
    dlg = wx.MessageDialog(
        parent, 
        "Sepertinya Anda baru pertama kali menggunakan aplikasi ini. Apakah Anda perlu bantuan untuk cara menggunakannya?", 
        "Selamat Datang!", 
        wx.YES_NO | wx.ICON_QUESTION
    )
    
    accessibility.speak("Sepertinya Anda baru pertama kali menggunakan aplikasi ini. Apakah Anda perlu bantuan untuk cara menggunakannya? Tekan Y untuk ya, atau N untuk tidak.")
    
    result = dlg.ShowModal()
    dlg.Destroy()
    
    if result == wx.ID_YES:
        show_readme_dialog(parent)
        
    # Mark first time setup as done
    config["first_time_setup"] = False
    import utils
    utils.save_config(config)

def show_readme_dialog(parent):
    """Shows the interactive readme dialog."""
    readme_path = os.path.join(os.path.dirname(__file__), "readme.txt")
    content = "File readme.txt tidak ditemukan."
    if os.path.exists(readme_path):
        try:
            with open(readme_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            content = f"Gagal membaca readme: {e}"

    dlg = ReadmeDialog(parent, content)
    dlg.ShowModal()
    dlg.Destroy()

class ReadmeDialog(wx.Dialog):
    def __init__(self, parent, content):
        super().__init__(parent, title="Panduan Penggunaan", size=(600, 500))
        self.init_ui(content)
        self.CenterOnParent()
        
    def init_ui(self, content):
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # We use a read-only multi-line text control so screen readers can read it easily
        self.text_ctrl = wx.TextCtrl(
            panel, 
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2, 
            name="Teks Panduan Penggunaan"
        )
        self.text_ctrl.SetValue(content)
        
        sizer.Add(self.text_ctrl, 1, wx.EXPAND | wx.ALL, 10)
        
        btn_sizer = wx.StdDialogButtonSizer()
        close_btn = wx.Button(panel, wx.ID_OK, label="Tutup")
        btn_sizer.AddButton(close_btn)
        btn_sizer.Realize()
        
        sizer.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        panel.SetSizer(sizer)
        
        # When opening, speak the first few lines or tell them they can read it
        accessibility.speak("Panduan penggunaan terbuka. Gunakan tombol panah untuk membaca isi panduan.")
