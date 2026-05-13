import addonHandler

addonHandler.initTranslation()

import json
import os
import subprocess
import threading

from .constants import CLI_PATH


def _run_command(command: list, cancel_evt: threading.Event, proc_holder: list):
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    proc_holder.append(proc)

    try:
        while True:
            if cancel_evt.is_set():
                proc.terminate()
                return "", "", 0
            if proc.poll() is not None:
                break
            threading.Event().wait(0.1)

        stdout, stderr = proc.communicate()
        return stdout, stderr, proc.returncode
    finally:
        try:
            proc.kill()
        except Exception:
            pass


def _ensure_cli_exists():
    if not os.path.isfile(CLI_PATH):
        raise FileNotFoundError(_("speedtest.exe not found in the add-on folder."))


def list_servers(cancel_evt: threading.Event, proc_holder: list):
    if cancel_evt.is_set():
        return []
    _ensure_cli_exists()

    command = [CLI_PATH, "--accept-license", "--accept-gdpr", "--servers", "--format=json"]
    stdout, stderr, returncode = _run_command(command, cancel_evt, proc_holder)
    if cancel_evt.is_set():
        return []
    if returncode != 0:
        raise RuntimeError(stderr.strip() or _("Failed to load servers."))

    data = json.loads(stdout)
    servers = data.get("servers", [])
    if not servers:
        raise RuntimeError(_("No servers were found."))
    return servers


def run_speedtest(cancel_evt: threading.Event, proc_holder: list, server_id=None):
    if cancel_evt.is_set():
        return 0, 0, 0, {}
    _ensure_cli_exists()

    command = [CLI_PATH, "--accept-license", "--accept-gdpr", "--format=json"]
    if server_id:
        command.append(f"--server-id={server_id}")

    stdout, stderr, returncode = _run_command(command, cancel_evt, proc_holder)
    if cancel_evt.is_set():
        return 0, 0, 0, {}
    if returncode != 0:
        raise RuntimeError(stderr.strip() or _("Failed to run speedtest.exe"))

    data = json.loads(stdout)
    ping = data["ping"]["latency"]
    down = data["download"]["bandwidth"] * 8 / 1_000_000
    up = data["upload"]["bandwidth"] * 8 / 1_000_000
    return round(ping, 1), round(down, 2), round(up, 2), data
