import addonHandler

addonHandler.initTranslation()


def build_diagnostics(ping: float, download: float, upload: float, data: dict):
    packet_loss = data.get("packetLoss") or 0.0
    packet_loss_percent = packet_loss * 100
    lines = []
    has_issues = False
    video_calls_good = download >= 10 and upload >= 3 and ping <= 100 and packet_loss_percent <= 1

    if video_calls_good:
        lines.append(_("Good for video calls."))
    else:
        has_issues = True
        lines.append(_("Video calls may be unstable."))

    if ping > 80:
        has_issues = True
        lines.append(_("Ping high for gaming."))
    elif packet_loss_percent <= 1:
        lines.append(_("Good for online gaming."))

    if upload < 5:
        has_issues = True
        lines.append(_("Upload low for live streaming."))
    else:
        lines.append(_("Upload good for live streaming."))

    if download < 10:
        has_issues = True
        lines.append(_("Download low for streaming or large downloads."))

    if packet_loss_percent > 0:
        has_issues = True
        lines.append(_("Packet loss detected."))

    if not has_issues:
        lines.append(_("Connection looks good for everyday use."))
    return lines
