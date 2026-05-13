import addonHandler

addonHandler.initTranslation()


DEFAULT_SPEED_UNIT = "Mbps"

SPEED_UNITS = [
    ("Mbps", "Mbps"),
    ("Gbps", "Gbps"),
    ("MB/s", "MB/s"),
    ("GB/s", "GB/s"),
]


def get_speed_unit(conf: dict):
    unit = conf.get("speedUnit", DEFAULT_SPEED_UNIT)
    valid_units = {key for key, label in SPEED_UNITS}
    if unit not in valid_units:
        return DEFAULT_SPEED_UNIT
    return unit


def save_speed_unit(conf: dict, unit: str):
    conf["speedUnit"] = unit if unit in {key for key, label in SPEED_UNITS} else DEFAULT_SPEED_UNIT


def get_speed_unit_choices():
    return [label for key, label in SPEED_UNITS]


def get_speed_unit_key(index: int):
    try:
        return SPEED_UNITS[index][0]
    except IndexError:
        return DEFAULT_SPEED_UNIT


def get_speed_unit_index(unit: str):
    for index, (key, label) in enumerate(SPEED_UNITS):
        if key == unit:
            return index
    return 0


def format_speed(mbps: float, unit: str):
    value = convert_mbps(mbps, unit)
    return _("{value:.2f} {unit}").format(value=value, unit=unit)


def format_speed_delta(mbps: float, unit: str):
    value = convert_mbps(mbps, unit)
    return _("{value:+.2f} {unit}").format(value=value, unit=unit)


def convert_mbps(mbps: float, unit: str):
    if unit == "Gbps":
        return mbps / 1000
    if unit == "MB/s":
        return mbps / 8
    if unit == "GB/s":
        return mbps / 8000
    return mbps
