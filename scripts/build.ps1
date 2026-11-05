$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $projectRoot
$pythonExe = Join-Path $projectRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $pythonExe)) {
    throw '请先按 README 创建 .venv 并安装 requirements-dev.txt'
}
& $pythonExe -m unittest discover -s tests -v
if ($LASTEXITCODE -ne 0) { throw '测试未通过，停止打包。' }
& $pythonExe -m PyInstaller --noconfirm --clean --windowed --onedir --name AlanWaterPet --add-data 'alan_water_pet/quotes.json;alan_water_pet' --add-data 'LICENSE;.' --add-data 'THIRD_PARTY_NOTICES.md;.' --add-data 'README.md;.' main.py
if ($LASTEXITCODE -ne 0) { throw '打包失败。' }
$licensesSource = Join-Path $projectRoot '.venv\Lib\site-packages\PySide6_Essentials-6.10.2.dist-info\licenses'
if (Test-Path -LiteralPath $licensesSource) {
    Copy-Item -LiteralPath $licensesSource -Destination (Join-Path $projectRoot 'dist\AlanWaterPet\qt-licenses') -Recurse -Force
}
Copy-Item -LiteralPath (Join-Path $projectRoot 'licenses') -Destination (Join-Path $projectRoot 'dist\AlanWaterPet\open-source-licenses') -Recurse -Force
Copy-Item -LiteralPath (Join-Path $projectRoot 'README.md'), (Join-Path $projectRoot 'THIRD_PARTY_NOTICES.md'), (Join-Path $projectRoot 'LICENSE') -Destination (Join-Path $projectRoot 'dist\AlanWaterPet') -Force
Compress-Archive -Path (Join-Path $projectRoot 'dist\AlanWaterPet') -DestinationPath (Join-Path $projectRoot 'dist\AlanWaterPet-0.1.0-windows-x64.zip') -Force
Write-Output '已生成 dist\AlanWaterPet-0.1.0-windows-x64.zip，解压后运行 AlanWaterPet.exe。'
