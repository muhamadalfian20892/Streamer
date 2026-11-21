import wx
from gui import StreamerFrame

def main():
    app = wx.App(False)
    frame = StreamerFrame()
    frame.Show()
    app.MainLoop()

if __name__ == '__main__':
    main()
