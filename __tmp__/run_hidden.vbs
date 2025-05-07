Set WshShell = CreateObject("WScript.Shell")

WshShell.Run "cmd.exe /c call venv\Scripts\activate && python 011.py", 0, False