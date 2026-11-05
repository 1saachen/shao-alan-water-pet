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
# Qt's Windows build uses the OS ICU API. A different ICU from an unrelated
# PATH entry (e.g. Poppler/Conda) exports versioned names and breaks QtCore.
# Let Windows resolve its own ICU instead of shipping that foreign library.
$internalRoot = Join-Path $projectRoot 'dist\AlanWaterPet\_internal'
$quarantineRoot = Join-Path $projectRoot ('artifacts\foreign-icu-' + (Get-Date -Format 'yyyyMMddHHmmssfff'))
New-Item -ItemType Directory -Path $quarantineRoot -Force | Out-Null
Get-ChildItem -LiteralPath $internalRoot -File | Where-Object {
    $_.Name -ieq 'icuuc.dll' -or $_.Name -imatch '^icudt\d+\.dll$'
} | ForEach-Object { Move-Item -LiteralPath $_.FullName -Destination $quarantineRoot }
$licensesSource = Join-Path $projectRoot '.venv\Lib\site-packages\PySide6_Essentials-6.10.2.dist-info\licenses'
if (Test-Path -LiteralPath $licensesSource) {
    Copy-Item -LiteralPath $licensesSource -Destination (Join-Path $projectRoot 'dist\AlanWaterPet\qt-licenses') -Recurse -Force
}
Copy-Item -LiteralPath (Join-Path $projectRoot 'licenses') -Destination (Join-Path $projectRoot 'dist\AlanWaterPet\open-source-licenses') -Recurse -Force
Copy-Item -LiteralPath (Join-Path $projectRoot 'README.md'), (Join-Path $projectRoot 'THIRD_PARTY_NOTICES.md'), (Join-Path $projectRoot 'LICENSE') -Destination (Join-Path $projectRoot 'dist\AlanWaterPet') -Force
$smokeDirectory = Join-Path $projectRoot 'artifacts\packaged-smoke'
$smokeProcess = Start-Process -FilePath (Join-Path $projectRoot 'dist\AlanWaterPet\AlanWaterPet.exe') -ArgumentList @('--preview-dir', ('"' + $smokeDirectory + '"')) -WindowStyle Hidden -PassThru
if (-not $smokeProcess.WaitForExit(30000)) {
    Stop-Process -Id $smokeProcess.Id -ErrorAction SilentlyContinue
    throw '便携版启动检查超时，停止发布。'
}
if ($smokeProcess.ExitCode -ne 0) { throw '便携版启动检查未通过，停止发布。' }
foreach ($previewFile in @('dashboard.png', 'pet.png', 'settings.png', 'quotes.png')) {
    if (-not (Test-Path -LiteralPath (Join-Path $smokeDirectory $previewFile))) { throw ('缺少预览：' + $previewFile) }
}
Compress-Archive -Path (Join-Path $projectRoot 'dist\AlanWaterPet') -DestinationPath (Join-Path $projectRoot 'dist\AlanWaterPet-0.1.0-windows-x64.zip') -Force
Write-Output '已生成 dist\AlanWaterPet-0.1.0-windows-x64.zip，解压后运行 AlanWaterPet.exe。'
