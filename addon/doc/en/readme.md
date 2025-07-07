# NVDA SpeedTest

**NVDA SpeedTest** is an open source add-on for NVDA that allows you to run internet speed tests (download, upload, and ping) in a fully accessible way, with spoken results and integrated history.

---

## Features

* Speed test (download, upload, and ping) with automatic spoken results.
* Test history, including date and summary.
* Full details: server, jitter, packet loss, and IPs.
* Button to cancel a running test.
* Customizable hotkey (default: `NVDA+Shift+L`).
* Copy results to clipboard with `Ctrl+C` (on a selected item) or with the **Copy** button after selecting an item in the list.
* Multi-language support.

---

## How to Use

1. Install NVDA SpeedTest through the NVDA add-ons menu.
2. Open the add-on using the default hotkey (`NVDA+Shift+L`) or via the NVDA menu at **Tools → Internet Speed Test**.
3. On the main window, press **Start test** to run the speed test.
4. Use the **Cancel** button to stop the test if needed.
5. Navigate the history with the arrow keys; view details, delete individual tests, or clear all history.
6. **To copy a test result to the clipboard:**

   * Select the desired item in the list and press `Ctrl+C`,
   * or use the **Copy** button after selecting an item in the list.
7. To change the hotkey, go to **Preferences → Input Gestures** and search for “NVDA SpeedTest”.

---

## Changelog

### 1.1 (latest)

* **Fix:** Empty history list now reports as "No tests found" instead of "Unknown list".
* **New:** Added ability to copy test results to clipboard with `Ctrl+C` or the **Copy** button after selecting an item in the list.

### 1.0

* Initial release.

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
   ```

2. **Install dependencies:**

   ```bash
   pip install scons  markdown
   ```

3. **Build the add-on (.nvda-addon file):**

   * If you installed SCons globally:

     ```bash
     SCons
     ```
   * If you did not add SCons to PATH, use:

     ```bash
     python -m SCons
     ```

   This will automatically generate:

   * Translated manifest files (`addon/locale/xx/manifest.ini`)
   * Compiled translation files (`nvda.mo`)
   * HTML documentation from Markdown
   * The `.nvda-addon` package for installation

4. **(Optional) Compile translations manually:**

   ```bash
   msgfmt addon/locale/xx/LC_MESSAGES/nvda.po -o addon/locale/xx/LC_MESSAGES/nvda.mo
   ```

   (Replace `xx` with your language code, e.g., `pt_BR`, `es`, etc.)

#### Best Practices

* **Always use SCons for building and packaging the add-on.**
  Never copy files manually — the build process automates translation and manifest generation, preventing version or language mismatches.
* Test your changes in NVDA using the generated `.nvda-addon` package.
* For translation or documentation, always follow the folder structure used by NVDA add-ons.

#### Contributing Code

* Always keep the add-on name as **NVDA SpeedTest** (do not translate or change it).
* Open pull requests for new features, bug fixes, or translation updates.
* Discuss major changes in issues before submitting large PRs.

---

## FAQ

* **What does ping mean?**
  It’s the response time between your computer and the server.

* **Can I choose the server?**
  For now, the server is chosen automatically. Future versions will allow manual selection.

* **Where can I find the history?**
  The history appears in the NVDA SpeedTest window, right after the results.

* **How do I change the hotkey?**
  Go to **Preferences → Input Gestures** and search for “NVDA SpeedTest”.

* **How do I contribute with code, translations, or ideas?**
  Open an issue, fork the repo, send a pull request, or join the discussions!

