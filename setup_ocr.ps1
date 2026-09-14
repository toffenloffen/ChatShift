$ErrorActionPreference = 'Stop'
$ocrPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $ocrPython)) { throw 'Run setup.ps1 first.' }
& $ocrPython -m pip install -r (Join-Path $PSScriptRoot 'requirements-ocr.txt')
if ($LASTEXITCODE -ne 0) { throw 'OCR dependency installation failed.' }
Write-Host 'Restart ChatShift. Among Us OCR support is experimental and requires a supported Windows OCR language.'
