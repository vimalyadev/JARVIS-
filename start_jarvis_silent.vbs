' J.A.R.V.I.S. Silent Background Launcher
Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
currentDir = fso.GetParentFolderName(WScript.ScriptFullName)

WshShell.CurrentDirectory = currentDir
' Run pythonw if available or python hidden (window style 0)
WshShell.Run "python desktop\run_desktop.py", 0, False
