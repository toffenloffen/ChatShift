#ifndef AppIdValue
  #define AppIdValue "ChatShift.Windows"
#endif
[Setup]
AppId={#AppIdValue}
AppName=ChatShift
AppVersion=0.2.0
AppPublisher=toffenloffen
DefaultDirName={localappdata}\Programs\ChatShift
DefaultGroupName=ChatShift
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
OutputDir=..\dist
OutputBaseFilename=ChatShift-Setup
SetupIconFile=..\norsk engelsk\assets\chatshift.ico
UninstallDisplayIcon={app}\ChatShift.exe
LicenseFile=..\LICENSE
Compression=lzma2/fast
SolidCompression=yes
WizardStyle=modern
CloseApplications=no
RestartApplications=no
DisableProgramGroupPage=yes
[Tasks]
Name: desktopicon; Description: "Create a desktop shortcut"; Flags: unchecked
[Files]
Source: "..\dist\ChatShift\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
[Icons]
Name: "{group}\ChatShift"; Filename: "{app}\ChatShift.exe"
Name: "{group}\ChatShift Setup"; Filename: "{app}\ChatShift.exe"; Parameters: "--setup"
Name: "{group}\Uninstall ChatShift"; Filename: "{uninstallexe}"
Name: "{autodesktop}\ChatShift"; Filename: "{app}\ChatShift.exe"; Tasks: desktopicon
[Run]
Filename: "{app}\ChatShift.exe"; Description: "Open ChatShift and prepare voice"; Flags: nowait postinstall skipifsilent
[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
  if ('{#AppIdValue}' = 'ChatShift.Windows') and CheckForMutexes('Local\Spillprat.RightCtrlEnter') then
  begin
    if not WizardSilent() then
      MsgBox('Close ChatShift before installing or updating it. Your settings will be kept.', mbInformation, MB_OK);
    Result := False;
  end;
end;
