import addonHandler

addonHandler.initTranslation()

import gui
import ui
import wx

from .alerts import get_alert_settings, save_alert_settings
from .features import (
    FEATURE_ADVANCED_TEST,
    FEATURE_CUSTOM_SPEED_UNIT,
    FEATURE_DIAGNOSIS,
    FEATURE_HISTORY_INSIGHTS,
    get_feature_settings,
    save_feature_settings,
)
from .units import (
    get_speed_unit,
    get_speed_unit_choices,
    get_speed_unit_index,
    get_speed_unit_key,
    save_speed_unit,
)


def _set_control_help(control, message, announce=False):
    control.SetToolTip(message)
    control.SetHelpText(message)
    if announce:
        control.Bind(wx.EVT_SET_FOCUS, lambda event: _announce_help(event, message))


def _announce_help(event, message):
    event.Skip()
    wx.CallAfter(ui.message, message)


class SettingsDialog(wx.Dialog):
    def __init__(self, parent, conf: dict):
        super().__init__(parent, title=_("SpeedTest settings"), size=(620, 520))
        self.SetEscapeId(wx.ID_CANCEL)
        self.conf = conf
        self.feature_settings = get_feature_settings(conf)
        self.alert_settings = get_alert_settings(conf)
        self.speed_unit = get_speed_unit(conf)

        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        helper = gui.guiHelper.BoxSizerHelper(panel, sizer=sizer)
        helper.addItem(wx.StaticText(panel, label=_("Optional features:")))

        self.chk_advanced = wx.CheckBox(panel, label=_("&Enable advanced server selection"))
        _set_control_help(
            self.chk_advanced,
            _("Shows the advanced test button so you can choose a fixed Speedtest server."),
            announce=True,
        )
        helper.addItem(self.chk_advanced)

        self.chk_history = wx.CheckBox(panel, label=_("&Enable history insights"))
        _set_control_help(
            self.chk_history,
            _("Shows history insights with averages, best and worst results, filters and export."),
            announce=True,
        )
        helper.addItem(self.chk_history)

        self.chk_diagnosis = wx.CheckBox(panel, label=_("&Enable simple diagnosis after tests"))
        _set_control_help(
            self.chk_diagnosis,
            _("Adds plain-language guidance after a test, such as video call readiness or high ping."),
            announce=True,
        )
        helper.addItem(self.chk_diagnosis)

        self.chk_custom_unit = wx.CheckBox(panel, label=_("&Enable custom display unit"))
        _set_control_help(
            self.chk_custom_unit,
            _("Lets you choose how speeds are displayed. If disabled, results use Mbps."),
            announce=True,
        )
        helper.addItem(self.chk_custom_unit)
        self.choice_speed_unit = helper.addLabeledControl(
            _("Display speed unit:"),
            wx.Choice,
            choices=get_speed_unit_choices(),
        )
        self.choice_speed_unit.SetName(_("Display speed unit selection"))
        _set_control_help(
            self.choice_speed_unit,
            _("Choose the speed unit used in results and details."),
        )

        self.chk_alerts = wx.CheckBox(panel, label=_("&Enable connection alerts"))
        _set_control_help(
            self.chk_alerts,
            _("Lets NVDA warn when download, upload, ping or packet loss crosses your limits."),
            announce=True,
        )
        helper.addItem(self.chk_alerts)
        self.txt_download = helper.addLabeledControl(_("Minimum download (Mbps):"), wx.TextCtrl)
        self.txt_download.SetName(_("Minimum download alert in Mbps"))
        _set_control_help(self.txt_download, _("Alert when download is below this Mbps value."))
        self.txt_upload = helper.addLabeledControl(_("Minimum upload (Mbps):"), wx.TextCtrl)
        self.txt_upload.SetName(_("Minimum upload alert in Mbps"))
        _set_control_help(self.txt_upload, _("Alert when upload is below this Mbps value."))
        self.txt_ping = helper.addLabeledControl(_("Maximum ping (ms):"), wx.TextCtrl)
        self.txt_ping.SetName(_("Maximum ping alert in milliseconds"))
        _set_control_help(self.txt_ping, _("Alert when ping is above this ms value."))
        self.txt_packet_loss = helper.addLabeledControl(_("Maximum packet loss (%):"), wx.TextCtrl)
        self.txt_packet_loss.SetName(_("Maximum packet loss alert percentage"))
        _set_control_help(
            self.txt_packet_loss,
            _("Alert when packet loss is above this percentage."),
        )
        btn_save = wx.Button(panel, id=wx.ID_OK, label=_("&Save"))
        btn_back = wx.Button(panel, id=wx.ID_CANCEL, label=_("&Back"))

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(btn_save, 0, wx.RIGHT, 8)
        button_sizer.Add(btn_back, 0)
        sizer.Add(button_sizer, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        panel.SetSizer(sizer)

        self.chk_advanced.SetValue(bool(self.feature_settings[FEATURE_ADVANCED_TEST]))
        self.chk_history.SetValue(bool(self.feature_settings[FEATURE_HISTORY_INSIGHTS]))
        self.chk_diagnosis.SetValue(bool(self.feature_settings[FEATURE_DIAGNOSIS]))
        self.chk_custom_unit.SetValue(bool(self.feature_settings[FEATURE_CUSTOM_SPEED_UNIT]))
        self.chk_alerts.SetValue(bool(self.alert_settings["enabled"]))
        self.choice_speed_unit.SetSelection(get_speed_unit_index(self.speed_unit))
        self.txt_download.SetValue(str(self.alert_settings["minDownloadMbps"]))
        self.txt_upload.SetValue(str(self.alert_settings["minUploadMbps"]))
        self.txt_ping.SetValue(str(self.alert_settings["maxPingMs"]))
        self.txt_packet_loss.SetValue(str(self.alert_settings["maxPacketLossPercent"]))

        self.chk_custom_unit.Bind(wx.EVT_CHECKBOX, self._update_controls)
        self.chk_alerts.Bind(wx.EVT_CHECKBOX, self._update_controls)
        btn_save.Bind(wx.EVT_BUTTON, self._save)
        btn_back.Bind(wx.EVT_BUTTON, lambda event: self.EndModal(wx.ID_CANCEL))
        self.Bind(wx.EVT_CHAR_HOOK, self._on_key)
        self._update_controls()

    def _update_controls(self, event=None):
        self.choice_speed_unit.Enable(self.chk_custom_unit.IsChecked())
        alerts_enabled = self.chk_alerts.IsChecked()
        for control in (
            self.txt_download,
            self.txt_upload,
            self.txt_ping,
            self.txt_packet_loss,
        ):
            control.Enable(alerts_enabled)
        if event:
            event.Skip()

    def _save(self, event):
        feature_settings = {
            FEATURE_ADVANCED_TEST: self.chk_advanced.IsChecked(),
            FEATURE_HISTORY_INSIGHTS: self.chk_history.IsChecked(),
            FEATURE_DIAGNOSIS: self.chk_diagnosis.IsChecked(),
            FEATURE_CUSTOM_SPEED_UNIT: self.chk_custom_unit.IsChecked(),
        }

        alert_settings = dict(self.alert_settings)
        alert_settings["enabled"] = self.chk_alerts.IsChecked()
        try:
            if alert_settings["enabled"]:
                alert_settings.update(
                    {
                        "minDownloadMbps": self._read_non_negative_float(self.txt_download),
                        "minUploadMbps": self._read_non_negative_float(self.txt_upload),
                        "maxPingMs": self._read_non_negative_float(self.txt_ping),
                        "maxPacketLossPercent": self._read_non_negative_float(self.txt_packet_loss),
                    }
                )
        except ValueError as error:
            wx.MessageBox(str(error), _("Invalid settings"))
            return

        save_feature_settings(self.conf, feature_settings)
        save_alert_settings(self.conf, alert_settings)
        save_speed_unit(self.conf, get_speed_unit_key(self.choice_speed_unit.GetSelection()))
        self.EndModal(wx.ID_OK)

    def _read_non_negative_float(self, control):
        text = control.GetValue().replace(",", ".").strip()
        try:
            value = float(text)
        except ValueError:
            control.SetFocus()
            raise ValueError(_("Enter a valid number."))
        if value < 0:
            control.SetFocus()
            raise ValueError(_("Enter a number greater than or equal to zero."))
        return value

    def _on_key(self, event):
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_CANCEL)
            return
        event.Skip()
