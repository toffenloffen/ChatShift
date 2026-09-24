$ErrorActionPreference = 'Stop'
& (Join-Path $PSScriptRoot 'Install ChatShift.cmd')
if ($LASTEXITCODE -ne 0) { throw 'Setup did not finish. See the error above.' }
