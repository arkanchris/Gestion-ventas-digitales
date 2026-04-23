Dim objShell
Dim strFolder
Set objShell = CreateObject("WScript.Shell")
strFolder = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\"))
objShell.CurrentDirectory = strFolder
objShell.Run "pythonw.exe """ & strFolder & "main.py""", 0, False
Set objShell = Nothing
