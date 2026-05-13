FEATURE_ADVANCED_TEST = "advancedTest"
FEATURE_HISTORY_INSIGHTS = "historyInsights"
FEATURE_DIAGNOSIS = "diagnosis"
FEATURE_CUSTOM_SPEED_UNIT = "customSpeedUnit"

DEFAULT_FEATURE_SETTINGS = {
    FEATURE_ADVANCED_TEST: True,
    FEATURE_HISTORY_INSIGHTS: True,
    FEATURE_DIAGNOSIS: False,
    FEATURE_CUSTOM_SPEED_UNIT: False,
}


def get_feature_settings(conf: dict):
    settings = dict(DEFAULT_FEATURE_SETTINGS)
    saved_settings = conf.get("features", {})
    if isinstance(saved_settings, dict):
        settings.update(saved_settings)
    return settings


def save_feature_settings(conf: dict, settings: dict):
    conf["features"] = {
        key: bool(settings.get(key, default))
        for key, default in DEFAULT_FEATURE_SETTINGS.items()
    }


def is_feature_enabled(conf: dict, feature: str):
    return bool(get_feature_settings(conf).get(feature, False))
