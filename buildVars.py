# -*- coding: UTF-8 -*-

def _(arg):
    return arg

addon_info = {
    "addon_name": "NVDASpeedTest",
    "addon_summary": _("NVDA SpeedTest"),
    "addon_description": _("Run accessible internet speed tests (download, upload, ping) directly from NVDA. Friendly interface, spoken results, integrated history and multi-language support."),
    "addon_version": "1.0",
    "addon_author": "Leo Guima",
    "addon_url": "https://github.com/leoguimaoficial/NVDA-SpeedTest",
    "addon_sourceURL": "https://github.com/leoguimaoficial/NVDA-SpeedTest",
    "addon_docFileName": "readme.html",
    "addon_minimumNVDAVersion": "2021.1",
    "addon_lastTestedNVDAVersion": "2025.1",
    "addon_updateChannel": None,
    "addon_license": "GPL v3",
    "addon_licenseURL": "https://www.gnu.org/licenses/gpl-3.0.html",
}

pythonSources = [
    "addon/*.py",
    "addon/globalPlugins/speedTest.py"
]

i18nSources = pythonSources + ["buildVars.py"]

excludedFiles = []

baseLanguage = "en"

markdownExtensions = []

brailleTables = {}
symbolDictionaries = {}
