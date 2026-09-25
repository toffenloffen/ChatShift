$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$testRoot = [IO.Path]::GetFullPath((Join-Path $root 'build/installer-verification'))
$installRoot = Join-Path $testRoot 'program'
$dataRoot = Join-Path $testRoot 'data'
$registry = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\ChatShift.IsolatedInstallerTest_is1'
if (Test-Path $registry) { throw 'An isolated installer test is already registered. Inspect it before continuing.' }
New-Item -ItemType Directory -Force $dataRoot | Out-Null
$env:CHATSHIFT_DATA_DIR = $dataRoot
$sentinel = Join-Path $dataRoot '.settings.json'
'{"source_language":"Norwegian","target_language":"English"}' | Set-Content $sentinel
$before = (Get-FileHash $sentinel).Hash
# Synthesize a public test phrase locally; never record the user's microphone.
Add-Type -AssemblyName System.Speech
$speaker = New-Object System.Speech.Synthesis.SpeechSynthesizer
$fixture = Join-Path $testRoot 'speech-fixture.wav'
$speaker.SetOutputToWaveFile($fixture)
$speaker.Speak('Hello my friend. Can you help me with this quest?')
$speaker.Dispose()
$setup = Join-Path $root 'dist/ChatShift-Test-Setup.exe'
$arguments = @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART',('/DIR="' + $installRoot + '"'),'/TASKS=')
foreach ($phase in @('install','update')) {
    $process = Start-Process -FilePath $setup -ArgumentList ($arguments + ('/LOG="' + (Join-Path $testRoot ($phase + '.log')) + '"')) -WindowStyle Hidden -Wait -PassThru
    if ($process.ExitCode -ne 0) { throw "$phase failed: $($process.ExitCode)" }
    if (-not (Test-Path $registry)) { throw 'Missing uninstall registration' }
    $registered = (Get-ItemProperty $registry).InstallLocation.TrimEnd('\')
    if ($registered -ne $installRoot.Replace('/', '\')) { throw "Unexpected install location: $registered" }
    $programs = [Environment]::GetFolderPath('Programs')
    $shortcut = Join-Path $programs 'ChatShiftInstallerVerification/ChatShift.lnk'
    if (-not (Test-Path $shortcut)) { throw 'Missing Start Menu shortcut' }
    $shell = New-Object -ComObject WScript.Shell
    if ($shell.CreateShortcut($shortcut).TargetPath -ne (Join-Path $installRoot 'ChatShift.exe')) { throw 'Incorrect shortcut target' }
    $process = Start-Process -FilePath (Join-Path $installRoot 'ChatShift.exe') -ArgumentList '--self-test' -WindowStyle Hidden -Wait -PassThru
    if ($process.ExitCode -ne 0) { throw 'Installed executable self-test failed' }
    if ($phase -eq 'install') {
        $process = Start-Process -FilePath (Join-Path $installRoot 'ChatShift.exe') -ArgumentList @('--test-models','--speech-fixture',('"' + $fixture + '"')) -WindowStyle Hidden -Wait -PassThru
        if ($process.ExitCode -ne 0) { throw 'Installed model download/load test failed' }
    }
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
if (-not (Test-Path (Join-Path $dataRoot 'setup-complete.json'))) { throw 'Uninstall removed model preparation state' }
@{ install='passed'; update='passed'; uninstall='passed'; shortcuts='passed'; settings='preserved'; self_test='passed'; models='downloaded and loaded'; pcm_transcription='passed' } | ConvertTo-Json | Set-Content (Join-Path $testRoot 'result.json')
Get-Content (Join-Path $testRoot 'result.json')
