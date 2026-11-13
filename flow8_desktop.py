import os
import sys
import time
import socket
import subprocess
import urllib.request
import webbrowser

if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w", encoding="utf-8")

import server

PORT = server.PORT
APP_URL = f"http://127.0.0.1:{PORT}"


def is_server_running():
    try:
        with urllib.request.urlopen(f"{APP_URL}/api/status", timeout=0.8) as resp:
            return resp.status == 200
    except Exception:
        return False


def wait_for_server(timeout=5.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if is_server_running():
            return True
        time.sleep(0.1)
    return False


def find_app_browser_exe():
    """Locate Microsoft Edge or Google Chrome on Windows for standalone --app window mode."""
    candidates = [
        os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%LocalAppData%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
    ]
    for path in candidates:
        if path and os.path.isfile(path):
            return path
    return None


def main():
    if "--server-only" in sys.argv:
        server.start_flow8_server(blocking=True)
        return

    httpd = None
    already_running = is_server_running()
    if not already_running:
        try:
            httpd = server.start_flow8_server(blocking=False)
            wait_for_server(timeout=5.0)
        except Exception as e:
            print(f"Notice: Could not bind port {PORT} ({e}), connecting to existing instance...")

    browser_exe = find_app_browser_exe()
    if browser_exe:
        profile_dir = os.path.join(
            os.environ.get("LOCALAPPDATA", os.path.expanduser("~")),
            "Flow8RemotePro",
            "AppWindowProfile",
        )
        os.makedirs(profile_dir, exist_ok=True)
        args = [
            browser_exe,
            f"--app={APP_URL}",
            f"--user-data-dir={profile_dir}",
            "--window-size=1440,860",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-features=Translate",
        ]
        try:
            proc = subprocess.Popen(args)
            proc.wait()
        except KeyboardInterrupt:
            pass
    else:
        webbrowser.open(APP_URL)
        if httpd is not None:
            try:
                while True:
                    time.sleep(1.0)
            except KeyboardInterrupt:
                pass

    if httpd is not None:
        try:
            httpd.shutdown()
        except Exception:
            pass
        server.midi_engine.close()


if __name__ == "__main__":
    main()
