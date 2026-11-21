import wx
import utils
import i18n
from gui import StreamerFrame


def main():
    config = utils.load_config()
    i18n.init_language(config)
    app = wx.App(False)
    frame = StreamerFrame()
    frame.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()
