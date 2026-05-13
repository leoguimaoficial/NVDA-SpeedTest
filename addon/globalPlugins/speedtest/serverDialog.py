import addonHandler

addonHandler.initTranslation()

import threading

import ui
import wx

from .runner import list_servers


def format_server(server: dict):
    return _("{location}, {country} - {name} (ID {id})").format(
        location=server.get("location", ""),
        country=server.get("country", ""),
        name=server.get("name", ""),
        id=server.get("id", ""),
    )


class ServerSelectionDialog(wx.Dialog):
    def __init__(self, parent, favorite_server_id=None):
        super().__init__(parent, title=_("Advanced speed test"), size=(620, 520))
        self.SetEscapeId(wx.ID_CANCEL)
        self.favorite_server_id = str(favorite_server_id or "")
        self.selected_server = None
        self.remember_server = False
        self.servers = []
        self.worker = None
        self.cancel_evt = threading.Event()
        self._proc_holder = []
        self._closing = False

        panel = wx.Panel(self)
        self.info = wx.StaticText(panel, label=_("Choose a server to run a fixed-server speed test."))
        self.lst = wx.ListBox(panel, name=_("Servers"))
        self.chk_remember = wx.CheckBox(panel, label=_("&Remember this server for next time"))
        self.chk_remember.SetValue(bool(self.favorite_server_id))
        self.btn_refresh = wx.Button(panel, label=_("&Refresh servers"))
        self.btn_start = wx.Button(panel, label=_("&Start selected test"))
        btn_back = wx.Button(panel, id=wx.ID_CANCEL, label=_("Back"))

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(self.btn_refresh, 0, wx.RIGHT, 8)
        button_sizer.Add(self.btn_start, 0, wx.RIGHT, 8)
        button_sizer.Add(btn_back, 0)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.info, 0, wx.ALL | wx.EXPAND, 10)
        sizer.Add(self.lst, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        sizer.Add(self.chk_remember, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        sizer.Add(button_sizer, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        panel.SetSizer(sizer)

        self.btn_refresh.Bind(wx.EVT_BUTTON, self._load_servers)
        self.btn_start.Bind(wx.EVT_BUTTON, self._start_selected)
        btn_back.Bind(wx.EVT_BUTTON, self._on_close)
        self.lst.Bind(wx.EVT_LISTBOX, lambda event: self._update_buttons())
        self.lst.Bind(wx.EVT_LISTBOX_DCLICK, self._start_selected)
        self.Bind(wx.EVT_CHAR_HOOK, self._on_key)
        self.Bind(wx.EVT_CLOSE, self._on_close)

        self._update_buttons()
        wx.CallAfter(self._load_servers)

    def _set_loading(self, loading):
        self.btn_refresh.Enable(not loading)
        self.btn_start.Enable(False)
        if loading:
            self.lst.Clear()
            self.lst.Append(_("Loading servers..."))
            self.info.SetLabel(_("Loading servers. Please wait."))
        else:
            self._update_buttons()

    def _load_servers(self, event=None):
        if self.worker and self.worker.is_alive():
            return
        self.cancel_evt.clear()
        self._proc_holder = []
        self.servers = []
        self._set_loading(True)
        self.worker = threading.Thread(target=self._load_servers_thread, daemon=True)
        self.worker.start()

    def _load_servers_thread(self):
        try:
            servers = list_servers(self.cancel_evt, self._proc_holder)
            wx.CallAfter(self._finish_loading, servers)
        except Exception as error:
            wx.CallAfter(self._show_loading_error, str(error))
        finally:
            self._proc_holder = []

    def _finish_loading(self, servers):
        if self._closing or self.cancel_evt.is_set():
            return
        self.servers = servers
        self.lst.Clear()
        if not self.servers:
            self.lst.Append(_("No servers were found."))
            self.info.SetLabel(_("No servers were found."))
            self._set_loading(False)
            return

        self.lst.InsertItems([format_server(server) for server in self.servers], 0)
        self._select_default_server()
        self.info.SetLabel(_("Server list loaded. Choose a server and press Start selected test."))
        self._set_loading(False)
        wx.CallAfter(self.lst.SetFocus)

    def _select_default_server(self):
        favorite_index = 0
        for index, server in enumerate(self.servers):
            if str(server.get("id", "")) == self.favorite_server_id:
                favorite_index = index
                break
        self.lst.SetSelection(favorite_index)

    def _show_loading_error(self, error):
        if self._closing:
            return
        self.servers = []
        self.lst.Clear()
        self.lst.Append(_("No servers were found."))
        self.info.SetLabel(_("Could not load server list: {err}").format(err=error))
        self._set_loading(False)

    def _update_buttons(self):
        has_selection = bool(self.servers) and self.lst.GetSelection() != wx.NOT_FOUND
        self.btn_start.Enable(has_selection)

    def _on_key(self, event):
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self._on_close(event)
            return
        event.Skip()

    def _start_selected(self, event):
        selection = self.lst.GetSelection()
        if selection == wx.NOT_FOUND or not self.servers:
            wx.CallLater(120, lambda: ui.message(_("Select a server before starting the test.")))
            return

        self.selected_server = self.servers[selection]
        self.remember_server = self.chk_remember.IsChecked()
        self.EndModal(wx.ID_OK)

    def _on_close(self, event=None):
        self._closing = True
        self.cancel_evt.set()
        for proc in self._proc_holder:
            try:
                proc.terminate()
            except Exception:
                pass
        if self.worker and self.worker.is_alive():
            self.worker.join(timeout=2)
        self.EndModal(wx.ID_CANCEL)
