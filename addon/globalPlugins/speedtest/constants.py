import addonHandler
import os

addonHandler.initTranslation()


GLOBAL_PLUGIN_DIR = os.path.dirname(os.path.dirname(__file__))
CLI_PATH = os.path.join(GLOBAL_PLUGIN_DIR, "speedtest.exe")
HISTORY_FILE = os.path.join(GLOBAL_PLUGIN_DIR, "speed_history.json")
CONF_FILE = os.path.join(GLOBAL_PLUGIN_DIR, "speed_conf.json")
DEFAULT_GESTURE = "kb:NVDA+shift+l"


def get_empty_history_msg():
    return _("No tests found.")
