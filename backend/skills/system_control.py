import subprocess
import os
import sys
import webbrowser

def open_application(app_name: str) -> str:
    """Launches commonly requested desktop applications or websites."""
    name = app_name.lower().strip()
    
    app_mapping_windows = {
        "chrome": "start chrome",
        "google chrome": "start chrome",
        "browser": "start chrome",
        "edge": "start msedge",
        "firefox": "start firefox",
        "spotify": "start spotify",
        "notepad": "notepad",
        "calculator": "calc",
        "calc": "calc",
        "cmd": "start cmd",
        "terminal": "start wt",
        "code": "code",
        "vs code": "code",
        "vscode": "code",
        "explorer": "explorer",
        "file explorer": "explorer",
        "settings": "start ms-settings:"
    }

    url_mapping = {
        "youtube": "https://www.youtube.com",
        "github": "https://www.github.com",
        "gmail": "https://mail.google.com",
        "google": "https://www.google.com",
        "twitter": "https://www.x.com",
        "reddit": "https://www.reddit.com",
        "netflix": "https://www.netflix.com"
    }

    for site, url in url_mapping.items():
        if site in name:
            webbrowser.open(url)
            return f"Opening {site.capitalize()} for you."

    if sys.platform == "win32":
        for key, cmd in app_mapping_windows.items():
            if key in name:
                try:
                    subprocess.Popen(cmd, shell=True)
                    return f"Opening {key.capitalize()}."
                except Exception as e:
                    return f"Failed to launch {key}: {str(e)}"

        try:
            subprocess.Popen(f"start {name}", shell=True)
            return f"Attempting to launch {name}."
        except Exception as e:
            return f"Could not launch {name}: {str(e)}"
            
    else:
        # Cross platform fallback
        webbrowser.open(f"https://www.google.com/search?q={app_name}")
        return f"Searching for {app_name}."

def set_volume(action: str) -> str:
    """Control audio volume on Windows."""
    if sys.platform == "win32":
        try:
            if "up" in action or "raise" in action or "increase" in action:
                # Send volume up virtual key
                subprocess.run('powershell -c "(New-Object -ComObject WScript.Shell).SendKeys([char]175)"', shell=True)
                return "Volume increased."
            elif "down" in action or "lower" in action or "decrease" in action:
                subprocess.run('powershell -c "(New-Object -ComObject WScript.Shell).SendKeys([char]174)"', shell=True)
                return "Volume decreased."
            elif "mute" in action or "unmute" in action:
                subprocess.run('powershell -c "(New-Object -ComObject WScript.Shell).SendKeys([char]173)"', shell=True)
                return "Audio muted/unmuted."
        except Exception as e:
            return f"Volume adjustment error: {str(e)}"
    return "Volume control is currently supported on Windows hosts."

def lock_screen() -> str:
    """Locks the workstation."""
    if sys.platform == "win32":
        try:
            subprocess.run("rundll32.exe user32.dll,LockWorkStation", shell=True)
            return "Screen locked."
        except Exception as e:
            return f"Failed to lock screen: {str(e)}"
    return "Locking screen is supported on Windows hosts."
