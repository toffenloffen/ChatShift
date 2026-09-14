Set shell = CreateObject("WScript.Shell")
Set fs = CreateObject("Scripting.FileSystemObject")
folder = fs.GetParentFolderName(WScript.ScriptFullName)
shell.CurrentDirectory = folder
runtime = fs.GetParentFolderName(folder) & "\.venv\Scripts\pythonw.exe"
If fs.FileExists(runtime) Then
    shell.Run """" & runtime & """ """ & folder & "\app.py""", 0, False
Else
    MsgBox "Setup is missing. Run setup.ps1 from the project folder first.", 48, "ChatShift"
End If
