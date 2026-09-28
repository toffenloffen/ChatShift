param([switch]$Production)
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$testRoot = [IO.Path]::GetFullPath((Join-Path $root 'build/installer-verification'))
$installRoot = Join-Path $testRoot 'program'
$dataRoot = Join-Path $testRoot 'data'
$appId = if ($Production) { 'ChatShift.Windows' } else { 'ChatShift.IsolatedInstallerTest' }
$groupName = if ($Production) { 'ChatShift' } else { 'ChatShiftInstallerVerification' }
$registry = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\' + $appId + '_is1'
if (Test-Path $registry) { throw 'An isolated installer test is already registered. Inspect it before continuing.' }
New-Item -ItemType Directory -Force $dataRoot | Out-Null
$env:CHATSHIFT_DATA_DIR = $dataRoot
$sentinel = Join-Path $dataRoot '.settings.json'
'{"source_language":"Norwegian","target_language":"English"}' | Set-Content $sentinel
$before = (Get-FileHash $sentinel).Hash
$setupName = if ($Production) { 'ChatShift-Setup.exe' } else { 'ChatShift-Test-Setup.exe' }
$setup = Join-Path $root ('dist/' + $setupName)
$arguments = @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART',('/DIR="' + $installRoot + '"'),'/TASKS=')
foreach ($phase in @('install','update')) {
    $process = Start-Process -FilePath $setup -ArgumentList ($arguments + ('/LOG="' + (Join-Path $testRoot ($phase + '.log')) + '"')) -WindowStyle Hidden -Wait -PassThru
    if ($process.ExitCode -ne 0) { throw "$phase failed: $($process.ExitCode)" }
    if (-not (Test-Path $registry)) { throw 'Missing uninstall registration' }
    $registered = (Get-ItemProperty $registry).InstallLocation.TrimEnd('\')
    if ($registered -ne $installRoot.Replace('/', '\')) { throw "Unexpected install location: $registered" }
    $programs = [Environment]::GetFolderPath('Programs')
    $shortcut = Join-Path $programs ($groupName + '/ChatShift.lnk')
    if (-not (Test-Path $shortcut)) { throw 'Missing Start Menu shortcut' }
    $shell = New-Object -ComObject WScript.Shell
    if ($shell.CreateShortcut($shortcut).TargetPath -ne (Join-Path $installRoot 'ChatShift.exe')) { throw 'Incorrect shortcut target' }
    $process = Start-Process -FilePath (Join-Path $installRoot 'ChatShift.exe') -ArgumentList '--self-test' -WindowStyle Hidden -Wait -PassThru
    if ($process.ExitCode -ne 0) { throw 'Installed executable self-test failed' }
    $selfTest = Get-Content -LiteralPath (Join-Path $dataRoot 'self-test.json') -Raw | ConvertFrom-Json
    if (-not $selfTest.ok -or @($selfTest.speech_models.PSObject.Properties).Count -ne 5) { throw 'Speech model selector self-test failed' }
    $desktopShortcut = Join-Path ([Environment]::GetFolderPath('Desktop')) ($groupName + '.lnk')
    $desktopLink = $shell.CreateShortcut($desktopShortcut)
    if ($desktopLink.TargetPath -ne (Join-Path $installRoot 'ChatShift.exe') -or $desktopLink.Arguments -ne '--settings') { throw 'Incorrect desktop shortcut' }
    if ((Get-FileHash $sentinel).Hash -ne $before) { throw 'Settings changed during install/update' }
}
$uninstaller = Join-Path $installRoot 'unins000.exe'
$resolved = [IO.Path]::GetFullPath($uninstaller)
if (-not $resolved.StartsWith(([IO.Path]::GetFullPath($testRoot) + [IO.Path]::DirectorySeparatorChar))) { throw 'Uninstaller outside test directory' }
$process = Start-Process -FilePath $resolved -ArgumentList @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART') -WindowStyle Hidden -Wait -PassThru
if ($process.ExitCode -ne 0) { throw 'Uninstall failed' }
# Inno's temporary uninstaller process may finish cleanup just after the launcher.
for ($attempt = 0; $attempt -lt 20 -and (Test-Path $registry); $attempt++) { Start-Sleep -Milliseconds 250 }
if (Test-Path $registry) { throw 'Uninstall registration remained' }
if (Test-Path (Join-Path $installRoot 'ChatShift.exe')) { throw 'Installed application remained' }
if (Test-Path $shortcut) { throw 'Start Menu shortcut remained' }
if ((Get-FileHash $sentinel).Hash -ne $before) { throw 'Uninstall changed settings' }
if (Test-Path $desktopShortcut) { throw 'Desktop shortcut remained' }
@{ install='passed'; update='passed'; uninstall='passed'; shortcuts='passed'; settings='preserved'; self_test='passed'; speech_models=5; live_transcription='not tested by installer check' } | ConvertTo-Json | Set-Content (Join-Path $testRoot 'result.json')
Get-Content (Join-Path $testRoot 'result.json')
