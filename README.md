# NVDA SpeedTest

**NVDA SpeedTest** is an open source add-on for NVDA that lets you run accessible internet speed tests directly from NVDA. It measures download, upload, ping, jitter and packet loss using Ookla's Speedtest CLI, then presents the results with speech-friendly dialogs, history, diagnostics and export options.

---

## Features

* Quick speed test with automatic server selection.
* Advanced speed test with manual server selection from the nearest Speedtest servers.
* Optional favorite server for the advanced test screen.
* Spoken and readable results for ping, download and upload.
* Optional simple connection diagnosis, such as video call readiness, high ping for gaming, low upload for live streaming and packet loss detection.
* Optional configurable display units: Mbps, Gbps, MB/s and GB/s.
* Optional configurable alerts for low download speed, low upload speed, high ping and packet loss.
* Test history with date, summary and server information.
* History insights with averages, best/worst results, comparison with the previous test, date filters and export.
* Export filtered history to CSV or JSON.
* Full test details, including server, jitter, packet loss, ISP, IP addresses and result URL when available.
* Copy selected detail items to the clipboard with `Ctrl+C` or the **Copy selected item** button.
* Button to cancel a running test.
* Customizable hotkey, defaulting to `NVDA+Shift+L`.
* Multi-language support.
* Metadata updated for NVDA compatibility through `2026.3`.

---

## How to Use

1. Install NVDA SpeedTest through NVDA's add-on manager.
2. Open the add-on with `NVDA+Shift+L` or from **NVDA menu > Tools > Internet Speed Test**.
3. Press **Start quick test** to run a normal speed test using automatic server selection.
4. Press **Advanced test...** to load nearby servers, choose one manually and run a fixed-server test.
5. In the advanced test screen, check **Remember this server for next time** if you want that server preselected the next time you open the advanced test.
6. Use **Cancel** to stop a running test.
7. Select a history item and press **View details** to inspect server, jitter, packet loss, ISP and IP information.
8. Use the history controls in order: **View details**, **Delete**, **History insights**, then **Clear history**.
9. Press **History insights** to view averages, best/worst results, comparison with the previous test, date filters and export options.
10. Press **Settings...** to enable optional features, configure connection alerts and choose the displayed speed unit.
11. To copy a detail item, open **View details**, select an item and press `Ctrl+C` or **Copy selected item**.
12. To change the hotkey, go to **Preferences > Input Gestures** and search for **NVDA SpeedTest**.

---

## Settings

Advanced server selection and history insights are enabled by default. Diagnosis, custom display units and connection alerts stay disabled until enabled in **Settings...**. The screen includes:

* **Enable advanced server selection:** show or hide the advanced test button and allow fixed-server tests.
* **Enable history insights:** show or hide the history insights button.
* **Enable simple diagnosis after tests:** add plain-language connection feedback after each test.
* **Enable custom display unit:** allow choosing a display unit other than the default Mbps.
* **Display speed unit:** choose Mbps, Gbps, MB/s or GB/s for visible results when custom units are enabled.
* **Enable connection alerts:** make NVDA warn when a result is below your configured expectations.
* **Minimum download (Mbps):** alert when download is below this value.
* **Minimum upload (Mbps):** alert when upload is below this value.
* **Maximum ping (ms):** alert when ping is above this value.
* **Maximum packet loss (%):** alert when packet loss is above this value.

Alert thresholds are stored in Mbps/ms/percent so they remain clear even if the display unit is changed.

The settings tab order keeps related controls together. When you enable custom display units, the next control is the unit selector. When you enable connection alerts, the next controls are the alert thresholds. Feature checkboxes also include accessible help text describing what each option changes.

---

## Changelog

### 2.0

* **New:** Advanced tests with manual server selection and optional favorite server, enabled by default.
* **New:** History insights with averages, best/worst results, comparison, filters and CSV/JSON export, enabled by default.
* **New:** Optional configurable connection alerts.
* **New:** Optional simple post-test diagnosis in plain language.
* **New:** Optional configurable display units.
* **Changed:** Diagnosis, custom display units and connection alerts are disabled by default and can be enabled from Settings.
* **Changed:** The original start button is now **Start quick test**.
* **Changed:** Main window controls were reorganized so history actions and settings are separated for clearer keyboard navigation.
* **Changed:** Add-on metadata now supports NVDA through `2026.3`.
* **Changed:** Codebase refactored into smaller modules for easier maintenance.

### 1.1

* **Fix:** Empty history list now reports as "No tests found" instead of "Unknown list".
* **New:** Added ability to copy test result details to the clipboard with `Ctrl+C` or the **Copy selected item** button.

### 1.0

* Initial release.

---

## Translating & Contributing

NVDA SpeedTest is ready for translations and open contributions.

### Translating

* Translation files (`.po`) are stored in `addon/locale/`.
* To add a new language:
  1. Generate a `.po` file from the `.pot` template.
  2. Translate the messages and save it using the NVDA structure: `xx/LC_MESSAGES/nvda.po`.
  3. Compile to `nvda.mo` and submit a pull request or open an issue.

### Developing & Environment Setup

To work on NVDA SpeedTest, build the add-on with **SCons** so translations, manifests and resources are generated correctly.

#### Environment Requirements

* **Python 3.10+**.
* **SCons** (`pip install scons`).
* **Markdown** (`pip install markdown`) for generating HTML help.
* **gettext** tools, such as `msgfmt`, for compiling `.po` files.

#### Building the Add-on

1. Clone the repository:

   ```bash
   git clone https://github.com/leoguimaoficial/NVDA-SpeedTest.git
   cd NVDA-SpeedTest
   ```

2. Install dependencies:

   ```bash
   pip install scons markdown
   ```

3. Build the `.nvda-addon` package:

   ```bash
   scons
   ```

   If SCons is not on PATH, use:

   ```bash
   py -m SCons
   ```

The build generates translated manifests, compiled translations, HTML documentation and the installable `.nvda-addon` package.

---

## FAQ

* **What does ping mean?**
  It is the response time between your computer and the test server.

* **Can I choose the server?**
  Yes. Use **Advanced test...** to choose a server from the list returned by Speedtest CLI.

* **What does the favorite server option do?**
  It preselects that server the next time you open the advanced test screen. The quick test still uses automatic server selection.

* **Where can I find history statistics?**
  Use **History insights** in the main window.

* **Can I export my results?**
  Yes. The history insights screen can export the filtered history to CSV or JSON.

* **How do I change the displayed speed unit?**
  Open **Settings...**, enable custom display unit and choose Mbps, Gbps, MB/s or GB/s.

* **How do I change the hotkey?**
  Go to **Preferences > Input Gestures** and search for **NVDA SpeedTest**.

---

Created by Leo Guima.

Project: [github.com/leoguimaoficial/NVDA-SpeedTest](https://github.com/leoguimaoficial/NVDA-SpeedTest)
