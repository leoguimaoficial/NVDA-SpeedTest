import wx, os, json, threading, subprocess, webbrowser
from datetime import datetime
import globalPluginHandler
import gui
import addonHandler
from scriptHandler import script
import ui

addonHandler.initTranslation()

ADDON_DIR   = os.path.dirname(__file__)
CLI_PATH    = os.path.join(ADDON_DIR, "speedtest.exe")
HISTORY_FILE= os.path.join(ADDON_DIR, "speed_history.json")
CONF_FILE   = os.path.join(ADDON_DIR, "speed_conf.json")
DEFAULT_GESTURE = "kb:NVDA+shift+l"
EMPTY_HISTORY_MSG = _("No tests found.")

def _load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def _save_json(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def _format_details(data: dict):
    try:
        server                 = data["server"]
        download, upload       = data["download"], data["upload"]
        ping, packet_loss      = data["ping"], data.get("packetLoss", 0.0)
        interface, isp         = data.get("interface", {}), data.get("isp", "")

        d_mbps = download["bandwidth"]*8/1_000_000
        u_mbps = upload  ["bandwidth"]*8/1_000_000
        d_mb   = download["bytes"]/(1024*1024)
        u_mb   = upload  ["bytes"]/(1024*1024)
        d_sec  = download["elapsed"]/1000
        u_sec  = upload  ["elapsed"]/1000

        lines = [
            _("• Server: {name} – {location} (ID {id})").format(
                name=server['name'], location=server['location'], id=server['id']),
            _("• Ping: {latency:.2f} ms").format(latency=ping['latency']),
            _("• Jitter: {jitter:.2f} ms").format(jitter=ping['jitter']),
            _("• Packet loss: {ploss:.0%}").format(ploss=packet_loss),
            _("• Download: {d_mbps:.2f} Mbps ({d_mb:.0f} MB in {d_sec:.1f} s)").format(
                d_mbps=d_mbps, d_mb=d_mb, d_sec=d_sec),
            _("• Upload: {u_mbps:.2f} Mbps ({u_mb:.0f} MB in {u_sec:.1f} s)").format(
                u_mbps=u_mbps, u_mb=u_mb, u_sec=u_sec),
            _("• ISP: {isp}").format(isp=isp),
            _("• External IP: {ip}").format(ip=interface.get('externalIp','')),
            _("• Internal IP: {ip}").format(ip=interface.get('internalIp',''))
        ]
        return lines
    except Exception as e:
        return [_("Error formatting details"), str(e)]

def _run_speedtest(cancel_evt: threading.Event, proc_holder: list):
    if cancel_evt.is_set():
        return 0,0,0,{}
    if not os.path.isfile(CLI_PATH):
        raise FileNotFoundError(_("speedtest.exe not found in the add-on folder."))

    cmd = [CLI_PATH, "--accept-license", "--accept-gdpr", "--format=json"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    proc_holder.append(proc)

    try:
        while True:
            if cancel_evt.is_set():
                proc.terminate()
                return 0,0,0,{}
            if proc.poll() is not None:
                break
            threading.Event().wait(0.1)
        stdout, stderr = proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError(stderr.strip() or _("Failed to run speedtest.exe"))
        data = json.loads(stdout)
        ping = data["ping"]["latency"]
        down = data["download"]["bandwidth"]*8/1_000_000
        up = data["upload"]["bandwidth"]*8/1_000_000
        return round(ping,1), round(down,2), round(up,2), data
    finally:
        try:
            proc.kill()
        except Exception:
            pass

class DetailsDialog(wx.Dialog):
    def __init__(self, parent, data: dict):
        super().__init__(parent, title=_("Test details"), size=(560, 500))
        self.SetEscapeId(wx.ID_CANCEL)
        pnl = wx.Panel(self)

        self.lst = wx.ListBox(pnl, name=_("Test result details"))
        url = data.get("result", {}).get("url", "")
        btn_copy = wx.Button(pnl, label=_("Copy selected item"))
        btn_open = wx.Button(pnl, label=_("Open in browser"))
        btn_back = wx.Button(pnl, id=wx.ID_CANCEL, label=_("Back"))

        vs = wx.BoxSizer(wx.VERTICAL)
        vs.Add(self.lst, 1, wx.ALL | wx.EXPAND, 10)
        vs.Add(btn_copy, 0, wx.LEFT | wx.BOTTOM, 10)
        vs.Add(btn_open, 0, wx.LEFT | wx.BOTTOM, 10)
        vs.Add(btn_back, 0, wx.LEFT | wx.BOTTOM, 10)
        pnl.SetSizer(vs)

        self.lst.InsertItems(_format_details(data), 0)

        btn_open.Enable(bool(url))
        btn_copy.Enable(False)

        btn_copy.Bind(wx.EVT_BUTTON, self._copy_selected)
        btn_open.Bind(wx.EVT_BUTTON, lambda e: webbrowser.open(url))
        btn_back.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_CANCEL))

        self.lst.Bind(wx.EVT_LISTBOX, lambda e: btn_copy.Enable(self.lst.GetSelection() != wx.NOT_FOUND))
        self.Bind(wx.EVT_CHAR_HOOK, self._on_key)

        self.btn_copy = btn_copy  

    def _on_key(self, event):
        key = event.GetKeyCode()
        control_down = event.ControlDown()

        if key == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_CANCEL)
        elif control_down and key == ord('C'):
            self._copy_selected(event)
        else:
            event.Skip()

    def _copy_selected(self, event):
        sel = self.lst.GetSelection()
        if sel == wx.NOT_FOUND:
            wx.CallLater(120, lambda: ui.message(_("Please select an item to copy.")))
            return

        text = self.lst.GetString(sel)
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(text))
            wx.TheClipboard.Close()
            wx.CallLater(120, lambda: ui.message(_("Copied to clipboard.")))
        else:
            wx.CallLater(120, lambda: ui.message(_("Failed to open clipboard.")))


class SpeedTestDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title=_("NVDA Speedtest"), size=(520,570))
        self.cancel_evt = threading.Event()
        self.worker = None
        self.items  = []
        self.conf   = _load_json(CONF_FILE,{"accepted":False})
        self._speedtest_proc = None
        self._canceling = False

        pnl = wx.Panel(self)
        self.info      = wx.StaticText(pnl, label=_("Click Start to measure your connection."))
        self.btn_start = wx.Button(pnl, label=_("&Start test"))
        self.lst       = wx.ListBox(pnl, name=_("History"))
        self.btn_view  = wx.Button(pnl, label=_("&View details"))
        self.btn_del   = wx.Button(pnl, label=_("&Delete"))
        self.btn_clear = wx.Button(pnl, label=_("&Clear history"))
        btn_close      = wx.Button(pnl, id=wx.ID_CLOSE, label=_("&Close"))
        self.progress  = wx.Gauge(pnl, range=100, style=wx.GA_HORIZONTAL)
        self.progress.Hide()

        v = wx.BoxSizer(wx.VERTICAL)
        for w in (self.info, self.btn_start):
            v.Add(w,0,wx.ALL|wx.EXPAND,10)
        v.Add(self.progress,0,wx.ALL|wx.EXPAND,10)
        v.Add(wx.StaticText(pnl,label=_("History:")),0,wx.LEFT,10)
        v.Add(self.lst,1,wx.ALL|wx.EXPAND,10)
        for w in (self.btn_view, self.btn_del, self.btn_clear):
            v.Add(w,0,wx.LEFT|wx.EXPAND,10)
        v.Add(btn_close,0,wx.ALL|wx.ALIGN_RIGHT,10)
        pnl.SetSizer(v)

        self.btn_start.Bind(wx.EVT_BUTTON, self._start_or_cancel)
        self.btn_view .Bind(wx.EVT_BUTTON, self._show_details)
        self.btn_del  .Bind(wx.EVT_BUTTON, self._delete_item)
        self.btn_clear.Bind(wx.EVT_BUTTON, self._clear_all)
        btn_close     .Bind(wx.EVT_BUTTON, self._on_close)
        self.lst.Bind(wx.EVT_LISTBOX, lambda e: self._update_buttons())
        self.Bind(wx.EVT_CHAR_HOOK, self._on_key)
        self.Bind(wx.EVT_CLOSE, self._on_close)

        raw = _load_json(HISTORY_FILE, [])
        self.items = raw if raw and isinstance(raw[0], dict) else []
        if not self.items:
            self.lst.Append(EMPTY_HISTORY_MSG)
        else:
            for it in self.items:
                self.lst.Append(it["summary"])
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

    def _on_progress_timer(self, evt):
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

    def _update_buttons(self):
        if self.lst.GetCount() == 1 and self.lst.GetString(0) == EMPTY_HISTORY_MSG:
            self.btn_view.Enable(False)
            self.btn_del.Enable(False)
            self.btn_clear.Enable(False)
        else:
            sel = self.lst.GetSelection() != wx.NOT_FOUND
            self.btn_view.Enable(sel)
            self.btn_del.Enable(sel)
            self.btn_clear.Enable(bool(self.items))

    def _on_key(self, evt):
        if evt.GetKeyCode() == wx.WXK_ESCAPE:
            self._on_close(evt)
            return
        evt.Skip()

    def _prompt_terms(self):
        dlg = wx.MessageDialog(self,_("This test uses Ookla's Speedtest CLI. By proceeding, you agree to the Terms. Continue?"),
                               _("Accept terms"), style=wx.YES_NO|wx.ICON_QUESTION)
        res = dlg.ShowModal(); dlg.Destroy()
        if res==wx.ID_YES:
            self.conf["accepted"] = True
            _save_json(CONF_FILE,self.conf)
            return True
        return False

    def _start_or_cancel(self, evt):
        if self.worker and self.worker.is_alive():
            self.cancel_evt.set()
            self._canceling = True
            self.btn_start.Disable()
            self.info.SetLabel(_("Test canceled or failed."))
            if self._speedtest_proc:
                try:
                    self._speedtest_proc.terminate()
                except Exception:
                    pass
            wx.CallLater(200, self._wait_for_thread_finish)
            return

        if not self.conf.get("accepted") and not self._prompt_terms():
            return
        self.cancel_evt.clear()
        self._canceling = False
        self.btn_start.SetLabel(_("Cancel"))
        self.btn_start.Enable(True)
        self.info.SetLabel(_("Testing... Please wait."))
        self._start_progress()
        self.worker = threading.Thread(target=self._test_thread, daemon=True)
        self.worker.start()

    def _wait_for_thread_finish(self):
        if self.worker and self.worker.is_alive():
            wx.CallLater(200, self._wait_for_thread_finish)
            return
        self.btn_start.SetLabel(_("Start test"))
        self.btn_start.Enable(True)
        self._stop_progress()
        self._canceling = False

    def _test_thread(self):
        proc_holder = []
        try:
            ping, down, up, data = _run_speedtest(self.cancel_evt, proc_holder)
            if proc_holder:
                self._speedtest_proc = proc_holder[0]
            wx.CallAfter(self._finish, ping, down, up, data)
        except Exception as e:
            wx.CallAfter(self._error, str(e))
        finally:
            self._speedtest_proc = None

    def _finish(self, ping, down, up, data):
        self.btn_start.SetLabel(_("Start test"))
        self.btn_start.Enable(True)
        self._stop_progress()
        if self.cancel_evt.is_set() or down==0:
            self.info.SetLabel(_("Test canceled or failed."))
            return
        msg = _("Ping: {ping} ms\nDownload: {down} Mbps\nUpload: {up} Mbps").format(
            ping=ping, down=down, up=up)
        self.info.SetLabel(msg.replace("\n","  "))
        wx.MessageBox(msg, _("SpeedTest result"))

        if self.lst.GetCount() == 1 and self.lst.GetString(0) == EMPTY_HISTORY_MSG:
            self.lst.Delete(0)
        summary = f"{datetime.now().strftime('%d/%m %H:%M')} → {down}/{up} ({ping}ms)"
        self.lst.InsertItems([summary],0)
        self.items.insert(0,{"summary":summary,"full":data})
        _save_json(HISTORY_FILE, self.items[:30])
        self._update_buttons()

    def _error(self, err):
        self.btn_start.SetLabel(_("Start test"))
        self.btn_start.Enable(True)
        self._stop_progress()
        self.info.SetLabel(_("Error: {err}").format(err=err))

    def _show_details(self, evt):
        sel = self.lst.GetSelection()
        if sel==wx.NOT_FOUND: return
        dlg = DetailsDialog(self, self.items[sel]["full"])
        dlg.ShowModal(); dlg.Destroy()

    def _delete_item(self, evt):
        sel = self.lst.GetSelection()
        if sel==wx.NOT_FOUND: return
        dlg = wx.MessageDialog(self, _("Are you sure you want to delete this test?"), _("Confirm delete"), style=wx.YES_NO|wx.ICON_WARNING)
        if dlg.ShowModal()==wx.ID_YES:
            self.lst.Delete(sel); del self.items[sel]; _save_json(HISTORY_FILE,self.items)
            if not self.items:
                self.lst.Append(EMPTY_HISTORY_MSG)
            self._update_buttons()
        dlg.Destroy()

    def _clear_all(self, evt):
        if not self.items: return
        dlg = wx.MessageDialog(self, _("Are you sure you want to clear all history?"), _("Clear history"), style=wx.YES_NO|wx.ICON_QUESTION)
        if dlg.ShowModal()==wx.ID_YES:
            self.lst.Clear(); self.items.clear(); _save_json(HISTORY_FILE,[])
            self.lst.Append(EMPTY_HISTORY_MSG)
            self._update_buttons()
        dlg.Destroy()

    def _on_close(self, evt=None):
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

def getGlobalPluginClasses():
    return [GlobalPlugin]

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    scriptCategory = _("NVDA Speedtest")

    def __init__(self):
        super().__init__()
        self._toolsMenuId = wx.NewId()
        gui.mainFrame.sysTrayIcon.toolsMenu.Append(self._toolsMenuId, _("Internet Speed Test"))
        gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.on_tools_menu, id=self._toolsMenuId)

    @script(
        description=_("Opens the NVDA Speedtest dialog."),
        gesture=DEFAULT_GESTURE,
        category=_("NVDA Speedtest")
    )
    def script_showUI(self, gesture):
        self._launch_dialog()

    def on_tools_menu(self, event):
        self._launch_dialog()

    def _launch_dialog(self):
        dlg = SpeedTestDialog(wx.GetApp().GetTopWindow())
        dlg.Show()
        dlg.Raise()
        wx.CallAfter(dlg.btn_start.SetFocus)

    __gestures = {
        DEFAULT_GESTURE: "showUI"
    }
