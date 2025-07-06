# NVDA SpeedTest

**NVDA SpeedTest** is an open source add-on for NVDA that allows you to run internet speed tests (download, upload, and ping) in a fully accessible way, with spoken results and integrated history.

## Features

* Speed test (download, upload, and ping) with automatic spoken results.
* Test history, including date and summary.
* Full details: server, jitter, packet loss, and IPs.
* Button to cancel a running test.
* Copy individual test items (e.g., download, upload, ping) to the clipboard via button or Ctrl+C.
* Customizable hotkey (default: `NVDA+Shift+L`).
* Multi-language support.

---

## How to Use

1. Install NVDA SpeedTest through the NVDA add-ons menu.
2. Open the add-on using the default hotkey (`NVDA+Shift+L`) or via the NVDA menu at **Tools → Internet Speed Test**.
3. On the main window, press **Start test** to run the speed test.
4. Use the **Cancel** button to stop the test if needed.
5. Navigate the history with the arrow keys; view details, delete individual tests, or clear all history.
6. To copy a specific result item (like download or ping), select it in the details list and press **Ctrl+C** or use the **Copy** button.
7. To change the hotkey, go to **Preferences → Input Gestures** and search for “NVDA SpeedTest”.

---

## Translating & Contributing

NVDA SpeedTest is fully ready for translations and open contributions. Here’s how to help:

### Translating

* Translation files (`.po`) are stored in the `addon/locale/` folder.
* To add a new language:

  1. Generate a `.po` file from the `.pot` template.
  2. Translate the messages and save using the NVDA structure: `xx/LC_MESSAGES/nvda.po` (where `xx` is the language code).
  3. Compile to `nvda.mo` and submit a pull request or open an issue.

### Developing & Environment Setup

To work on NVDA SpeedTest, you should always build the add-on using **SCons** to guarantee that translations, manifests, and all resources are generated correctly and automatically.

#### Environment Requirements

* **Python 3.10+** (Same or compatible version with your NVDA installation)
* **SCons** (`pip install scons`)
* **Markdown** (`pip install markdown`)
  (required for generating HTML docs from Markdown)
* **gettext** tools (for compiling `.po` to `.mo`, e.g., `msgfmt`)

#### Building the Add-on

1. **Clone the repository:**

   ```bash
   git clone https://github.com/leoguimaoficial/NVDA-SpeedTest.git
   cd NVDA-SpeedTest
