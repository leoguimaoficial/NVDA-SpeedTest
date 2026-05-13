import addonHandler

addonHandler.initTranslation()

import os

import ui
import wx

from .history import (
    FILTER_ALL,
    build_statistics,
    export_csv,
    export_json,
    filter_items,
)


class HistoryDialog(wx.Dialog):
    def __init__(self, parent, items: list, speed_unit="Mbps"):
        super().__init__(parent, title=_("History insights"), size=(680, 560))
        self.SetEscapeId(wx.ID_CANCEL)
        self.items = list(items)
        self.speed_unit = speed_unit
        self.filtered_items = []

        panel = wx.Panel(self)
        filter_label = wx.StaticText(panel, label=_("Date filter:"))
        self.filter_choice = wx.Choice(
            panel,
            choices=[
                _("All history"),
                _("Today"),
                _("Last 7 days"),
                _("Last 30 days"),
            ],
            name=_("Date filter"),
        )
        self.filter_choice.SetSelection(FILTER_ALL)
        self.stats = wx.ListBox(panel, name=_("History statistics"))
        self.history = wx.ListBox(panel, name=_("Filtered history"))
        self.btn_copy = wx.Button(panel, label=_("&Copy summary"))
        self.btn_export_csv = wx.Button(panel, label=_("Export &CSV..."))
        self.btn_export_json = wx.Button(panel, label=_("Export &JSON..."))
        btn_back = wx.Button(panel, id=wx.ID_CANCEL, label=_("Back"))

        filter_sizer = wx.BoxSizer(wx.HORIZONTAL)
        filter_sizer.Add(filter_label, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 8)
        filter_sizer.Add(self.filter_choice, 1)

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(self.btn_copy, 0, wx.RIGHT, 8)
        button_sizer.Add(self.btn_export_csv, 0, wx.RIGHT, 8)
        button_sizer.Add(self.btn_export_json, 0, wx.RIGHT, 8)
        button_sizer.Add(btn_back, 0)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(filter_sizer, 0, wx.ALL | wx.EXPAND, 10)
        sizer.Add(wx.StaticText(panel, label=_("Statistics:")), 0, wx.LEFT | wx.RIGHT, 10)
        sizer.Add(self.stats, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        sizer.Add(wx.StaticText(panel, label=_("Filtered history:")), 0, wx.LEFT | wx.RIGHT, 10)
        sizer.Add(self.history, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        sizer.Add(button_sizer, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        panel.SetSizer(sizer)

        self.filter_choice.Bind(wx.EVT_CHOICE, self._refresh)
        self.btn_copy.Bind(wx.EVT_BUTTON, self._copy_summary)
        self.btn_export_csv.Bind(wx.EVT_BUTTON, lambda event: self._export("csv"))
        self.btn_export_json.Bind(wx.EVT_BUTTON, lambda event: self._export("json"))
        btn_back.Bind(wx.EVT_BUTTON, lambda event: self.EndModal(wx.ID_CANCEL))
        self.Bind(wx.EVT_CHAR_HOOK, self._on_key)

        self._refresh()

    def _refresh(self, event=None):
        filter_index = self.filter_choice.GetSelection()
        self.filtered_items = filter_items(self.items, filter_index)
        stats = build_statistics(self.filtered_items, self.speed_unit)

        self.stats.Clear()
        self.stats.InsertItems(stats, 0)
        self.history.Clear()
        if self.filtered_items:
            self.history.InsertItems([item.get("summary", "") for item in self.filtered_items], 0)
        else:
            self.history.Append(_("No tests found."))

        has_items = bool(self.filtered_items)
        self.btn_export_csv.Enable(has_items)
        self.btn_export_json.Enable(has_items)
        self.btn_copy.Enable(bool(stats))

    def _copy_summary(self, event):
        lines = [self.stats.GetString(index) for index in range(self.stats.GetCount())]
        text = os.linesep.join(lines)
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(text))
            wx.TheClipboard.Close()
            wx.CallLater(120, lambda: ui.message(_("Copied to clipboard.")))
        else:
            wx.CallLater(120, lambda: ui.message(_("Failed to open clipboard.")))

    def _export(self, format_name):
        if not self.filtered_items:
            wx.CallLater(120, lambda: ui.message(_("No tests found.")))
            return

        extension = format_name
        wildcard = _("{format} files (*.{extension})|*.{extension}").format(
            format=format_name.upper(),
            extension=extension,
        )
        dialog = wx.FileDialog(
            self,
            _("Export history"),
            wildcard=wildcard,
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
        )
        try:
            if dialog.ShowModal() != wx.ID_OK:
                return
            path = _ensure_extension(dialog.GetPath(), extension)
            if format_name == "csv":
                export_csv(self.filtered_items, path)
            else:
                export_json(self.filtered_items, path)
        except Exception as error:
            wx.MessageBox(_("Could not export history: {err}").format(err=error), _("Error"))
            return
        finally:
            dialog.Destroy()

        wx.CallLater(120, lambda: ui.message(_("History exported.")))

    def _on_key(self, event):
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_CANCEL)
            return
        event.Skip()


def _ensure_extension(path, extension):
    if path.lower().endswith(f".{extension}"):
        return path
    return f"{path}.{extension}"
