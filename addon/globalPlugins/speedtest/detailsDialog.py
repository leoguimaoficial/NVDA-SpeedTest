import addonHandler

addonHandler.initTranslation()

import webbrowser

import ui
import wx

from .results import format_details


class DetailsDialog(wx.Dialog):
    def __init__(self, parent, data: dict, speed_unit="Mbps"):
        super().__init__(parent, title=_("Test details"), size=(560, 500))
        self.SetEscapeId(wx.ID_CANCEL)
        panel = wx.Panel(self)

        self.lst = wx.ListBox(panel, name=_("Test result details"))
        url = data.get("result", {}).get("url", "")
        btn_copy = wx.Button(panel, label=_("Copy selected item"))
        btn_open = wx.Button(panel, label=_("Open in browser"))
        btn_back = wx.Button(panel, id=wx.ID_CANCEL, label=_("Back"))

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.lst, 1, wx.ALL | wx.EXPAND, 10)
        sizer.Add(btn_copy, 0, wx.LEFT | wx.BOTTOM, 10)
        sizer.Add(btn_open, 0, wx.LEFT | wx.BOTTOM, 10)
        sizer.Add(btn_back, 0, wx.LEFT | wx.BOTTOM, 10)
        panel.SetSizer(sizer)

        self.lst.InsertItems(format_details(data, speed_unit), 0)

        btn_open.Enable(bool(url))
        btn_copy.Enable(False)

        btn_copy.Bind(wx.EVT_BUTTON, self._copy_selected)
        btn_open.Bind(wx.EVT_BUTTON, lambda event: webbrowser.open(url))
        btn_back.Bind(wx.EVT_BUTTON, lambda event: self.EndModal(wx.ID_CANCEL))

        self.lst.Bind(wx.EVT_LISTBOX, lambda event: btn_copy.Enable(self.lst.GetSelection() != wx.NOT_FOUND))
        self.Bind(wx.EVT_CHAR_HOOK, self._on_key)

        self.btn_copy = btn_copy

    def _on_key(self, event):
        key = event.GetKeyCode()
        control_down = event.ControlDown()

        if key == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_CANCEL)
        elif control_down and key == ord("C"):
            self._copy_selected(event)
        else:
            event.Skip()

    def _copy_selected(self, event):
        selection = self.lst.GetSelection()
        if selection == wx.NOT_FOUND:
            wx.CallLater(120, lambda: ui.message(_("Please select an item to copy.")))
            return

        text = self.lst.GetString(selection)
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(text))
            wx.TheClipboard.Close()
            wx.CallLater(120, lambda: ui.message(_("Copied to clipboard.")))
        else:
            wx.CallLater(120, lambda: ui.message(_("Failed to open clipboard.")))
