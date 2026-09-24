$ErrorActionPreference = 'Stop'
$projectFolder = $PSScriptRoot
$environmentFolder = Join-Path $projectFolder '.venv'
$pythonLauncher = Get-Command py -ErrorAction SilentlyContinue
if ($pythonLauncher) {
    & $pythonLauncher.Source -3 -c 'import sys; assert sys.version_info >= (3,11), "Python 3.11 or newer is required"'
    if ($LASTEXITCODE -ne 0) { throw 'Install Python 3.11 or newer with tkinter, then try again.' }
    & $pythonLauncher.Source -3 -m venv $environmentFolder
} else {
    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if (-not $pythonCommand) { throw 'Install Python from python.org with tkinter, then run setup.ps1 again.' }
    & $pythonCommand.Source -c 'import sys; assert sys.version_info >= (3,11), "Python 3.11 or newer is required"'
    if ($LASTEXITCODE -ne 0) { throw 'Python 3.11 or newer is required.' }
    & $pythonCommand.Source -m venv $environmentFolder
}
if ($LASTEXITCODE -ne 0) { throw 'Could not create the Python environment.' }
& (Join-Path $environmentFolder 'Scripts/python.exe') -c 'import tkinter; print("ChatShift setup is ready.")'
if ($LASTEXITCODE -ne 0) { throw 'Python tkinter is missing. Modify your Python installation to include Tcl/Tk.' }
Write-Host 'Sign in to Codex with ChatGPT, then open: norsk engelsk\Start ChatShift.vbs'
Write-Host 'Text translation needs no extra pip packages and no API key.'
Write-Host 'For voice, run: ./.venv/Scripts/python.exe -m pip install -r requirements-voice.txt'
Write-Host 'Read GET_STARTED.md for first-time setup and usage.'
