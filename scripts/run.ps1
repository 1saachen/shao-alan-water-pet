$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $projectRoot
$pythonExe = Join-Path $projectRoot '.venv\Scripts\pythonw.exe'
if (-not (Test-Path -LiteralPath $pythonExe)) { throw '请先按 README 创建 .venv 并安装依赖。' }
Start-Process -FilePath $pythonExe -ArgumentList 'main.py' -WorkingDirectory $projectRoot -WindowStyle Hidden
