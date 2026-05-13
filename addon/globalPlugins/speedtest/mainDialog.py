import addonHandler

addonHandler.initTranslation()

from datetime import datetime
import threading

import ui
import wx

from .alerts import evaluate_alerts
from .constants import CONF_FILE, HISTORY_FILE, get_empty_history_msg
from .detailsDialog import DetailsDialog
from .diagnostics import build_diagnostics
from .features import (
    FEATURE_ADVANCED_TEST,
    FEATURE_CUSTOM_SPEED_UNIT,
    FEATURE_DIAGNOSIS,
    FEATURE_HISTORY_INSIGHTS,
    is_feature_enabled,
)
from .historyDialog import HistoryDialog
from .runner import run_speedtest
from .serverDialog import ServerSelectionDialog, format_server
from .settingsDialog import SettingsDialog
from .storage import load_json, save_json
from .units import DEFAULT_SPEED_UNIT, format_speed, get_speed_unit


def _get_summary_server(data: dict):
    server = data.get("server", {})
    name = server.get("name", "")
    location = server.get("location", "")
    if name and location:
        return f"{name} - {location}"
    return name or location


class SpeedTestDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title=_("NVDA Speedtest"), size=(520, 570))
        self.cancel_evt = threading.Event()
        self.worker = None
        self.items = []
        self.conf = load_json(CONF_FILE, {"accepted": False})
        self.empty_history_msg = get_empty_history_msg()
        self.current_server = None
        self._speedtest_proc = None
        self._canceling = False

        panel = wx.Panel(self)
        self.panel = panel
        self.info = wx.StaticText(panel, label=_("Click Start to measure your connection."))
        self.btn_start = wx.Button(panel, label=_("&Start quick test"))
        self.btn_advanced = wx.Button(panel, label=_("&Advanced test..."))
        self.lst = wx.ListBox(panel, name=_("History"))
        self.btn_view = wx.Button(panel, label=_("&View details"))
        self.btn_del = wx.Button(panel, label=_("&Delete"))
        self.btn_history = wx.Button(panel, label=_("&History insights"))
        self.btn_clear = wx.Button(panel, label=_("&Clear history"))
        self.btn_settings = wx.Button(panel, label=_("&Settings..."))
        btn_close = wx.Button(panel, id=wx.ID_CLOSE, label=_("&Close"))
        self.progress = wx.Gauge(panel, range=100, style=wx.GA_HORIZONTAL)
        self.progress.Hide()

        start_sizer = wx.BoxSizer(wx.HORIZONTAL)
        start_sizer.Add(self.btn_start, 1, wx.RIGHT, 8)
        start_sizer.Add(self.btn_advanced, 1)

        history_action_sizer = wx.BoxSizer(wx.HORIZONTAL)
        history_action_sizer.Add(self.btn_view, 1, wx.RIGHT, 8)
        history_action_sizer.Add(self.btn_del, 1)

        history_manage_sizer = wx.BoxSizer(wx.HORIZONTAL)
        history_manage_sizer.Add(self.btn_history, 1, wx.RIGHT, 8)
        history_manage_sizer.Add(self.btn_clear, 1)

        footer_sizer = wx.BoxSizer(wx.HORIZONTAL)
        footer_sizer.Add(self.btn_settings, 0)
        footer_sizer.AddStretchSpacer(1)
        footer_sizer.Add(btn_close, 0)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.info, 0, wx.ALL | wx.EXPAND, 10)
        sizer.Add(start_sizer, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        sizer.Add(self.progress, 0, wx.ALL | wx.EXPAND, 10)
        sizer.Add(wx.StaticText(panel, label=_("History:")), 0, wx.LEFT, 10)
        sizer.Add(self.lst, 1, wx.ALL | wx.EXPAND, 10)
        sizer.Add(history_action_sizer, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        sizer.Add(history_manage_sizer, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        sizer.Add(wx.StaticLine(panel), 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        sizer.Add(footer_sizer, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        panel.SetSizer(sizer)

        self.btn_start.Bind(wx.EVT_BUTTON, self._start_or_cancel)
        self.btn_advanced.Bind(wx.EVT_BUTTON, self._show_advanced_test)
        self.btn_view.Bind(wx.EVT_BUTTON, self._show_details)
        self.btn_history.Bind(wx.EVT_BUTTON, self._show_history_insights)
        self.btn_settings.Bind(wx.EVT_BUTTON, self._show_settings)
        self.btn_del.Bind(wx.EVT_BUTTON, self._delete_item)
        self.btn_clear.Bind(wx.EVT_BUTTON, self._clear_all)
        btn_close.Bind(wx.EVT_BUTTON, self._on_close)
        self.lst.Bind(wx.EVT_LISTBOX, lambda event: self._update_buttons())
        self.Bind(wx.EVT_CHAR_HOOK, self._on_key)
        self.Bind(wx.EVT_CLOSE, self._on_close)

        raw = load_json(HISTORY_FILE, [])
        self.items = raw if raw and isinstance(raw[0], dict) else []
        if not self.items:
            self.lst.Append(self.empty_history_msg)
        else:
            for item in self.items:
                self.lst.Append(item["summary"])
        self._apply_feature_visibility()
        self._update_buttons()

        self._progress_timer = None
        self._progress_pos = 0

    def _start_progress(self):
        self.progress.SetValue(0)
        self.progress.Show()
        self._progress_pos = 0
        if self._progress_timer is None:
            self._progress_timer = wx.Timer(self)
            self.Bind(wx.EVT_TIMER, self._on_progress_timer, self._progress_timer)
        self._progress_timer.Start(250)

    def _on_progress_timer(self, event):
        self._progress_pos += 1
        self.progress.SetValue(self._progress_pos)
        if self._progress_pos >= 100:
            self._progress_pos = 0
            self.progress.SetValue(0)

    def _stop_progress(self):
        if self._progress_timer:
            self._progress_timer.Stop()
        self.progress.SetValue(0)
        self.progress.Hide()
        self._progress_pos = 0

    def _get_display_speed_unit(self):
        if is_feature_enabled(self.conf, FEATURE_CUSTOM_SPEED_UNIT):
            return get_speed_unit(self.conf)
        return DEFAULT_SPEED_UNIT

    def _apply_feature_visibility(self):
        advanced_enabled = is_feature_enabled(self.conf, FEATURE_ADVANCED_TEST)
        history_enabled = is_feature_enabled(self.conf, FEATURE_HISTORY_INSIGHTS)
        self.btn_advanced.Show(advanced_enabled)
        self.btn_history.Show(history_enabled)
        self.btn_advanced.Enable(advanced_enabled and not (self.worker and self.worker.is_alive()))
        if not history_enabled:
            self.btn_history.Disable()
        self.panel.Layout()

    def _update_buttons(self):
        if self.lst.GetCount() == 1 and self.lst.GetString(0) == self.empty_history_msg:
            self.btn_view.Enable(False)
            self.btn_history.Enable(False)
            self.btn_del.Enable(False)
            self.btn_clear.Enable(False)
            return

        has_selection = self.lst.GetSelection() != wx.NOT_FOUND
        self.btn_view.Enable(has_selection)
        self.btn_history.Enable(is_feature_enabled(self.conf, FEATURE_HISTORY_INSIGHTS) and bool(self.items))
        self.btn_del.Enable(has_selection)
        self.btn_clear.Enable(bool(self.items))

    def _on_key(self, event):
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self._on_close(event)
            return
        event.Skip()

    def _prompt_terms(self):
        dialog = wx.MessageDialog(
            self,
            _("This test uses Ookla's Speedtest CLI. By proceeding, you agree to the Terms. Continue?"),
            _("Accept terms"),
            style=wx.YES_NO | wx.ICON_QUESTION,
        )
        result = dialog.ShowModal()
        dialog.Destroy()
        if result == wx.ID_YES:
            self.conf["accepted"] = True
            save_json(CONF_FILE, self.conf)
            return True
        return False

    def _ensure_terms_accepted(self):
        return self.conf.get("accepted") or self._prompt_terms()

    def _start_or_cancel(self, event):
        if self.worker and self.worker.is_alive():
            self.cancel_evt.set()
            self._canceling = True
            self.btn_start.Disable()
            self.btn_advanced.Disable()
            self.info.SetLabel(_("Test canceled or failed."))
            if self._speedtest_proc:
                try:
                    self._speedtest_proc.terminate()
                except Exception:
                    pass
            wx.CallLater(200, self._wait_for_thread_finish)
            return

        if not self._ensure_terms_accepted():
            return
        self._start_test()

    def _show_advanced_test(self, event):
        if not is_feature_enabled(self.conf, FEATURE_ADVANCED_TEST):
            return
        if self.worker and self.worker.is_alive():
            return
        if not self._ensure_terms_accepted():
            return

        dialog = ServerSelectionDialog(self, self.conf.get("favoriteServerId"))
        result = dialog.ShowModal()
        selected_server = dialog.selected_server
        remember_server = dialog.remember_server
        dialog.Destroy()

        if result != wx.ID_OK or not selected_server:
            return
        if remember_server:
            self.conf["favoriteServerId"] = selected_server.get("id")
            self.conf["favoriteServerLabel"] = format_server(selected_server)
            save_json(CONF_FILE, self.conf)
        self._start_test(selected_server)

    def _start_test(self, server=None):
        self.current_server = server
        self.cancel_evt.clear()
        self._canceling = False
        self.btn_start.SetLabel(_("Cancel"))
        self.btn_start.Enable(True)
        self.btn_advanced.Disable()
        if server:
            self.info.SetLabel(_("Testing with server: {server}").format(server=format_server(server)))
        else:
            self.info.SetLabel(_("Testing... Please wait."))
        self._start_progress()
        self.worker = threading.Thread(target=self._test_thread, daemon=True)
        self.worker.start()

    def _wait_for_thread_finish(self):
        if self.worker and self.worker.is_alive():
            wx.CallLater(200, self._wait_for_thread_finish)
            return
        self.btn_start.SetLabel(_("Start quick test"))
        self.btn_start.Enable(True)
        self.btn_advanced.Enable(is_feature_enabled(self.conf, FEATURE_ADVANCED_TEST))
        self._stop_progress()
        self._canceling = False

    def _test_thread(self):
        proc_holder = []
        server_id = self.current_server.get("id") if self.current_server else None
        try:
            ping, down, up, data = run_speedtest(self.cancel_evt, proc_holder, server_id=server_id)
            if proc_holder:
                self._speedtest_proc = proc_holder[0]
            wx.CallAfter(self._finish, ping, down, up, data)
        except Exception as error:
            wx.CallAfter(self._error, str(error))
        finally:
            self._speedtest_proc = None

    def _finish(self, ping, down, up, data):
        self.btn_start.SetLabel(_("Start quick test"))
        self.btn_start.Enable(True)
        self.btn_advanced.Enable(is_feature_enabled(self.conf, FEATURE_ADVANCED_TEST))
        self._stop_progress()
        self.current_server = None
        if self.cancel_evt.is_set() or down == 0:
            self.info.SetLabel(_("Test canceled or failed."))
            return

        speed_unit = self._get_display_speed_unit()
        message = _("Ping: {ping} ms\nDownload: {down}\nUpload: {up}").format(
            ping=ping,
            down=format_speed(down, speed_unit),
            up=format_speed(up, speed_unit),
        )
        if is_feature_enabled(self.conf, FEATURE_DIAGNOSIS):
            diagnosis = build_diagnostics(ping, down, up, data)
            message = message + "\n\n" + _("Diagnosis:") + "\n" + "\n".join(diagnosis)
        self.info.SetLabel(message.replace("\n", "  "))
        wx.MessageBox(message, _("SpeedTest result"))
        self._show_alerts(ping, down, up, data)

        if self.lst.GetCount() == 1 and self.lst.GetString(0) == self.empty_history_msg:
            self.lst.Delete(0)
        summary = _("{date} -> {down}/{up} ({ping}ms)").format(
            date=datetime.now().strftime("%d/%m %H:%M"),
            down=format_speed(down, speed_unit),
            up=format_speed(up, speed_unit),
            ping=ping,
        )
        server_label = _get_summary_server(data)
        if server_label:
            summary = f"{summary} - {server_label}"
        self.lst.InsertItems([summary], 0)
        self.items.insert(0, {"summary": summary, "timestamp": datetime.now().isoformat(), "full": data})
        save_json(HISTORY_FILE, self.items[:30])
        self._update_buttons()

    def _error(self, error):
        self.btn_start.SetLabel(_("Start quick test"))
        self.btn_start.Enable(True)
        self.btn_advanced.Enable(is_feature_enabled(self.conf, FEATURE_ADVANCED_TEST))
        self._stop_progress()
        self.current_server = None
        self.info.SetLabel(_("Error: {err}").format(err=error))

    def _show_details(self, event):
        selection = self.lst.GetSelection()
        if selection == wx.NOT_FOUND:
            return
        dialog = DetailsDialog(self, self.items[selection]["full"], self._get_display_speed_unit())
        dialog.ShowModal()
        dialog.Destroy()

    def _show_history_insights(self, event):
        if not is_feature_enabled(self.conf, FEATURE_HISTORY_INSIGHTS):
            return
        if not self.items:
            return
        dialog = HistoryDialog(self, self.items, self._get_display_speed_unit())
        dialog.ShowModal()
        dialog.Destroy()

    def _show_settings(self, event):
        dialog = SettingsDialog(self, self.conf)
        result = dialog.ShowModal()
        dialog.Destroy()
        if result == wx.ID_OK:
            save_json(CONF_FILE, self.conf)
            self._apply_feature_visibility()
            self._update_buttons()
            wx.CallLater(120, lambda: ui.message(_("Settings saved.")))

    def _show_alerts(self, ping, download, upload, data):
        alerts = evaluate_alerts(self.conf, ping, download, upload, data)
        if not alerts:
            return

        message = _("Connection below expected.") + "\n" + "\n".join(alerts)
        self.info.SetLabel(_("Connection below expected."))
        wx.CallLater(120, lambda: ui.message(_("Connection below expected.")))
        wx.MessageBox(message, _("Connection alert"), style=wx.OK | wx.ICON_WARNING)

    def _delete_item(self, event):
        selection = self.lst.GetSelection()
        if selection == wx.NOT_FOUND:
            return
        dialog = wx.MessageDialog(
            self,
            _("Are you sure you want to delete this test?"),
            _("Confirm delete"),
            style=wx.YES_NO | wx.ICON_WARNING,
        )
        if dialog.ShowModal() == wx.ID_YES:
            self.lst.Delete(selection)
            del self.items[selection]
            save_json(HISTORY_FILE, self.items)
            if not self.items:
                self.lst.Append(self.empty_history_msg)
            self._update_buttons()
        dialog.Destroy()

    def _clear_all(self, event):
        if not self.items:
            return
        dialog = wx.MessageDialog(
            self,
            _("Are you sure you want to clear all history?"),
            _("Clear history"),
            style=wx.YES_NO | wx.ICON_QUESTION,
        )
        if dialog.ShowModal() == wx.ID_YES:
            self.lst.Clear()
            self.items.clear()
            save_json(HISTORY_FILE, [])
            self.lst.Append(self.empty_history_msg)
            self._update_buttons()
        dialog.Destroy()

    def _on_close(self, event=None):
        self.cancel_evt.set()
        if self._speedtest_proc:
            try:
                self._speedtest_proc.terminate()
            except Exception:
                pass
        if self.worker and self.worker.is_alive():
            self.worker.join(timeout=2)
        self._stop_progress()
        self.Destroy()
