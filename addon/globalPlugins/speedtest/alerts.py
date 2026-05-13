import addonHandler

addonHandler.initTranslation()


DEFAULT_ALERT_SETTINGS = {
    "enabled": False,
    "minDownloadMbps": 100.0,
    "minUploadMbps": 10.0,
    "maxPingMs": 80.0,
    "maxPacketLossPercent": 0.0,
}


def get_alert_settings(conf: dict):
    settings = dict(DEFAULT_ALERT_SETTINGS)
    settings.update(conf.get("alerts", {}))
    return settings


def save_alert_settings(conf: dict, settings: dict):
    conf["alerts"] = {
        "enabled": bool(settings.get("enabled")),
        "minDownloadMbps": _to_float(
            settings.get("minDownloadMbps"),
            DEFAULT_ALERT_SETTINGS["minDownloadMbps"],
        ),
        "minUploadMbps": _to_float(
            settings.get("minUploadMbps"),
            DEFAULT_ALERT_SETTINGS["minUploadMbps"],
        ),
        "maxPingMs": _to_float(settings.get("maxPingMs"), DEFAULT_ALERT_SETTINGS["maxPingMs"]),
        "maxPacketLossPercent": _to_float(
            settings.get("maxPacketLossPercent"),
            DEFAULT_ALERT_SETTINGS["maxPacketLossPercent"],
        ),
    }


def evaluate_alerts(conf: dict, ping: float, download: float, upload: float, data: dict):
    settings = get_alert_settings(conf)
    if not settings["enabled"]:
        return []

    messages = []
    min_download = settings["minDownloadMbps"]
    min_upload = settings["minUploadMbps"]
    max_ping = settings["maxPingMs"]
    max_packet_loss = settings["maxPacketLossPercent"]
    packet_loss = data.get("packetLoss")

    if download < min_download:
        messages.append(
            _("Download below limit: {current:.2f} Mbps, limit {limit:.2f} Mbps.").format(
                current=download,
                limit=min_download,
            )
        )
    if upload < min_upload:
        messages.append(
            _("Upload below limit: {current:.2f} Mbps, limit {limit:.2f} Mbps.").format(
                current=upload,
                limit=min_upload,
            )
        )
    if ping > max_ping:
        messages.append(
            _("Ping above limit: {current:.1f} ms, limit {limit:.1f} ms.").format(
                current=ping,
                limit=max_ping,
            )
        )
    if packet_loss is not None and packet_loss * 100 > max_packet_loss:
        messages.append(
            _("Packet loss above limit: {current:.2f}%, limit {limit:.2f}%.").format(
                current=packet_loss * 100,
                limit=max_packet_loss,
            )
        )
    return messages


def _to_float(value, default):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default
