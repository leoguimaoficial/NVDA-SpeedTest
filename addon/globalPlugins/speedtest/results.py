import addonHandler

addonHandler.initTranslation()

from .units import format_speed


def format_details(data: dict, speed_unit="Mbps"):
    try:
        server = data["server"]
        download, upload = data["download"], data["upload"]
        ping, packet_loss = data["ping"], data.get("packetLoss", 0.0)
        interface, isp = data.get("interface", {}), data.get("isp", "")

        d_mbps = download["bandwidth"] * 8 / 1_000_000
        u_mbps = upload["bandwidth"] * 8 / 1_000_000
        d_mb = download["bytes"] / (1024 * 1024)
        u_mb = upload["bytes"] / (1024 * 1024)
        d_sec = download["elapsed"] / 1000
        u_sec = upload["elapsed"] / 1000

        return [
            _("• Server: {name} – {location} (ID {id})").format(
                name=server["name"], location=server["location"], id=server["id"]
            ),
            _("• Ping: {latency:.2f} ms").format(latency=ping["latency"]),
            _("• Jitter: {jitter:.2f} ms").format(jitter=ping["jitter"]),
            _("• Packet loss: {ploss:.0%}").format(ploss=packet_loss),
            _("• Download: {speed} ({size:.0f} MB in {seconds:.1f} s)").format(
                speed=format_speed(d_mbps, speed_unit), size=d_mb, seconds=d_sec
            ),
            _("• Upload: {speed} ({size:.0f} MB in {seconds:.1f} s)").format(
                speed=format_speed(u_mbps, speed_unit), size=u_mb, seconds=u_sec
            ),
            _("• ISP: {isp}").format(isp=isp),
            _("• External IP: {ip}").format(ip=interface.get("externalIp", "")),
            _("• Internal IP: {ip}").format(ip=interface.get("internalIp", "")),
        ]
    except Exception as error:
        return [_("Error formatting details"), str(error)]
