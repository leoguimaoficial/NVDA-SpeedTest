import addonHandler
import globalPluginHandler
import gui
from scriptHandler import script
import wx

addonHandler.initTranslation()

from .speedtest.constants import DEFAULT_GESTURE
from .speedtest.mainDialog import SpeedTestDialog


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    scriptCategory = _("NVDA Speedtest")

    def __init__(self):
        super().__init__()
        self._toolsMenuId = wx.NewId()
        gui.mainFrame.sysTrayIcon.toolsMenu.Append(
            self._toolsMenuId,
            "Internet Speed Test",
        )
        gui.mainFrame.sysTrayIcon.Bind(
            wx.EVT_MENU,
            self.on_tools_menu,
            id=self._toolsMenuId
        )

    @script(
        description=_("Opens the NVDA Speedtest dialog."),
        gesture=DEFAULT_GESTURE,
        category=_("NVDA Speedtest"),
    )
    def script_showUI(self, gesture):
        self._launch_dialog()

    def on_tools_menu(self, event):
        self._launch_dialog()

    def _launch_dialog(self):
        dialog = SpeedTestDialog(wx.GetApp().GetTopWindow())
        dialog.Show()
        dialog.Raise()
        wx.CallAfter(dialog.btn_start.SetFocus)
