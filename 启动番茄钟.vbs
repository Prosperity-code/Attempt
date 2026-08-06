' Tomato Clock Launcher - Double-click to run
Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")

dir = fso.GetParentFolderName(WScript.ScriptFullName)
html = dir & "\pomodoro.html"
fileUrl = "file:///" & Replace(Replace(html, "\", "/"), " ", "%20")

chromePaths = Array( _
    shell.ExpandEnvironmentStrings("%ProgramFiles%") & "\Google\Chrome\Application\chrome.exe", _
    shell.ExpandEnvironmentStrings("%ProgramFiles(x86)%") & "\Google\Chrome\Application\chrome.exe", _
    shell.ExpandEnvironmentStrings("%LOCALAPPDATA%") & "\Google\Chrome\Application\chrome.exe" _
)

edgePaths = Array( _
    shell.ExpandEnvironmentStrings("%ProgramFiles(x86)%") & "\Microsoft\Edge\Application\msedge.exe", _
    shell.ExpandEnvironmentStrings("%ProgramFiles%") & "\Microsoft\Edge\Application\msedge.exe" _
)

browserExe = ""

For Each p In chromePaths
    If fso.FileExists(p) Then
        browserExe = p
        Exit For
    End If
Next

If browserExe = "" Then
    For Each p In edgePaths
        If fso.FileExists(p) Then
            browserExe = p
            Exit For
        End If
    Next
End If

If browserExe <> "" Then
    shell.Run """" & browserExe & """ --app=""" & fileUrl & """ --window-size=420,620 --disable-extensions --no-first-run --no-default-browser-check", 1, False
Else
    shell.Run """" & html & """", 1, False
End If
