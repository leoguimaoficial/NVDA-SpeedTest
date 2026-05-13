import addonHandler

addonHandler.initTranslation()

import csv
from datetime import date, datetime, timedelta
import json

from .units import format_speed, format_speed_delta


FILTER_ALL = 0
FILTER_TODAY = 1
FILTER_LAST_7_DAYS = 2
FILTER_LAST_30_DAYS = 3


def get_timestamp(item: dict):
    timestamp = item.get("timestamp") or item.get("full", {}).get("timestamp")
    parsed = _parse_timestamp(timestamp)
    if parsed:
        return parsed
    return _parse_summary_timestamp(item.get("summary", ""))


def get_metrics(item: dict):
    data = item.get("full", {})
    download = data.get("download", {})
    upload = data.get("upload", {})
    ping = data.get("ping", {})
    server = data.get("server", {})
    result = data.get("result", {})
    timestamp = get_timestamp(item)

    return {
        "timestamp": timestamp,
        "summary": item.get("summary", ""),
        "ping": _round(ping.get("latency"), 1),
        "download": _bandwidth_to_mbps(download.get("bandwidth")),
        "upload": _bandwidth_to_mbps(upload.get("bandwidth")),
        "packet_loss": data.get("packetLoss"),
        "server_id": server.get("id", ""),
        "server_name": server.get("name", ""),
        "server_location": server.get("location", ""),
        "server_country": server.get("country", ""),
        "result_url": result.get("url", ""),
        "full": data,
    }


def filter_items(items: list, filter_index: int):
    if filter_index == FILTER_ALL:
        return list(items)

    now = datetime.now()
    filtered = []
    for item in items:
        timestamp = get_timestamp(item)
        if not timestamp:
            continue
        if filter_index == FILTER_TODAY and timestamp.date() == date.today():
            filtered.append(item)
        elif filter_index == FILTER_LAST_7_DAYS and timestamp >= now - timedelta(days=7):
            filtered.append(item)
        elif filter_index == FILTER_LAST_30_DAYS and timestamp >= now - timedelta(days=30):
            filtered.append(item)
    return filtered


def build_statistics(items: list, speed_unit="Mbps"):
    records = [get_metrics(item) for item in items]
    records = [record for record in records if _has_test_metrics(record)]
    if not records:
        return [_("No tests found.")]

    newest_records = _sort_newest_first(records)
    avg_ping = _average(record["ping"] for record in records)
    avg_download = _average(record["download"] for record in records)
    avg_upload = _average(record["upload"] for record in records)
    best_download = max(records, key=lambda record: record["download"])
    worst_download = min(records, key=lambda record: record["download"])
    best_upload = max(records, key=lambda record: record["upload"])
    worst_upload = min(records, key=lambda record: record["upload"])
    best_ping = min(records, key=lambda record: record["ping"])
    worst_ping = max(records, key=lambda record: record["ping"])

    lines = [
        _("Tests in this view: {count}").format(count=len(records)),
        _("Average ping: {ping:.1f} ms").format(ping=avg_ping),
        _("Average download: {download}").format(download=format_speed(avg_download, speed_unit)),
        _("Average upload: {upload}").format(upload=format_speed(avg_upload, speed_unit)),
        _("Best download: {download} ({server})").format(
            download=format_speed(best_download["download"], speed_unit),
            server=_get_server_label(best_download),
        ),
        _("Worst download: {download} ({server})").format(
            download=format_speed(worst_download["download"], speed_unit),
            server=_get_server_label(worst_download),
        ),
        _("Best upload: {upload} ({server})").format(
            upload=format_speed(best_upload["upload"], speed_unit),
            server=_get_server_label(best_upload),
        ),
        _("Worst upload: {upload} ({server})").format(
            upload=format_speed(worst_upload["upload"], speed_unit),
            server=_get_server_label(worst_upload),
        ),
        _("Best ping: {ping:.1f} ms ({server})").format(
            ping=best_ping["ping"], server=_get_server_label(best_ping)
        ),
        _("Worst ping: {ping:.1f} ms ({server})").format(
            ping=worst_ping["ping"], server=_get_server_label(worst_ping)
        ),
    ]
    lines.extend(_build_comparison_lines(newest_records, speed_unit))
    return lines


def export_csv(items: list, path: str):
    with open(path, "w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=_get_export_fieldnames())
        writer.writeheader()
        for item in items:
            writer.writerow(_get_export_row(get_metrics(item)))


def export_json(items: list, path: str):
    records = []
    for item in items:
        metrics = get_metrics(item)
        record = _get_export_row(metrics)
        record["raw"] = metrics["full"]
        records.append(record)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(records, file, ensure_ascii=False, indent=2)


def _parse_timestamp(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo:
            parsed = parsed.astimezone().replace(tzinfo=None)
        return parsed
    except ValueError:
        return None


def _parse_summary_timestamp(summary):
    try:
        head = summary.split(" ", 2)
        if len(head) < 2:
            return None
        return datetime.strptime(f"{date.today().year}/{head[0]} {head[1]}", "%Y/%d/%m %H:%M")
    except ValueError:
        return None


def _bandwidth_to_mbps(value):
    if value is None:
        return 0.0
    return round(value * 8 / 1_000_000, 2)


def _round(value, precision):
    if value is None:
        return 0.0
    return round(value, precision)


def _average(values):
    values = list(values)
    if not values:
        return 0.0
    return sum(values) / len(values)


def _has_test_metrics(record):
    return record["download"] > 0 or record["upload"] > 0 or record["ping"] > 0


def _sort_newest_first(records):
    return sorted(
        records,
        key=lambda record: record["timestamp"] or datetime.min,
        reverse=True,
    )


def _build_comparison_lines(records, speed_unit):
    if len(records) < 2:
        return [_("Comparison with previous test: not enough data.")]

    current, previous = records[0], records[1]
    return [
        _("Compared with previous test:"),
        _("Download change: {change}").format(
            change=format_speed_delta(current["download"] - previous["download"], speed_unit)
        ),
        _("Upload change: {change}").format(
            change=format_speed_delta(current["upload"] - previous["upload"], speed_unit)
        ),
        _("Ping change: {change:+.1f} ms").format(change=current["ping"] - previous["ping"]),
    ]


def _get_server_label(record):
    name = record.get("server_name", "")
    location = record.get("server_location", "")
    if name and location:
        return f"{name} - {location}"
    return name or location or _("Unknown server")


def _format_timestamp(timestamp):
    if not timestamp:
        return ""
    return timestamp.isoformat(timespec="seconds")


def _get_export_fieldnames():
    return [
        "timestamp",
        "summary",
        "ping_ms",
        "download_mbps",
        "upload_mbps",
        "packet_loss",
        "server_id",
        "server_name",
        "server_location",
        "server_country",
        "result_url",
    ]


def _get_export_row(record):
    return {
        "timestamp": _format_timestamp(record["timestamp"]),
        "summary": record["summary"],
        "ping_ms": record["ping"],
        "download_mbps": record["download"],
        "upload_mbps": record["upload"],
        "packet_loss": record["packet_loss"],
        "server_id": record["server_id"],
        "server_name": record["server_name"],
        "server_location": record["server_location"],
        "server_country": record["server_country"],
        "result_url": record["result_url"],
    }
