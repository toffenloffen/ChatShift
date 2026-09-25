#ifndef AppIdValue
  #define AppIdValue "ChatShift.Windows"
#endif
#ifndef GroupNameValue
  #define GroupNameValue "ChatShift"
#endif
[Setup]
AppId={#AppIdValue}
AppName=ChatShift
AppVersion=0.2.0
AppPublisher=toffenloffen
DefaultDirName={localappdata}\Programs\ChatShift
DefaultGroupName={#GroupNameValue}
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
[Files]
Source: "..\dist\ChatShift\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
[Icons]
Name: "{userprograms}\{#GroupNameValue}\ChatShift"; Filename: "{app}\ChatShift.exe"
Name: "{userprograms}\{#GroupNameValue}\ChatShift Setup"; Filename: "{app}\ChatShift.exe"; Parameters: "--setup"
Name: "{userprograms}\{#GroupNameValue}\Uninstall ChatShift"; Filename: "{uninstallexe}"
Name: "{autodesktop}\ChatShift"; Filename: "{app}\ChatShift.exe"
[Run]
Filename: "{app}\ChatShift.exe"; Flags: nowait skipifsilent
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
