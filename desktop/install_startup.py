import os
import sys
from pathlib import Path

def setup_startup():
    base_dir = Path(__file__).resolve().parent.parent
    desktop_runner = base_dir / "desktop" / "run_desktop.py"
    
    # Path to user startup folder
    appdata = os.getenv("APPDATA")
    if not appdata:
        print("Could not locate APPDATA directory.")
        return False
        
    startup_dir = Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
    startup_dir.mkdir(parents=True, exist_ok=True)
    
    # Locate pythonw (runs without opening a command prompt window)
    python_exe = sys.executable
    pythonw_exe = Path(python_exe).parent / "pythonw.exe"
    runner_binary = str(pythonw_exe) if pythonw_exe.exists() else python_exe

    # Create a silent VBScript launcher in the Startup directory
    vbs_path = startup_dir / "Launch_JARVIS_Silent.vbs"
    vbs_content = f'''Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "{base_dir}"
WshShell.Run "\"{runner_binary}\" \"{desktop_runner}\"", 0, False
'''
    with open(vbs_path, "w", encoding="utf-8") as f:
        f.write(vbs_content)

    print(f"[SUCCESS] J.A.R.V.I.S. autostart registered!")
    print(f"Startup Script: {vbs_path}")
    print("Jarvis will now start silently in the background whenever your laptop boots.")
    return True

if __name__ == "__main__":
    setup_startup()
