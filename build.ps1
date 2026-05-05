#!/usr/bin/env pwsh
$ErrorActionPreference = "Stop"
$root = $PSScriptRoot

Write-Host "=== OfferTrack 打包 (单文件 exe) ===" -ForegroundColor Cyan

try {
    $pyVer = python --version 2>&1
    Write-Host "[OK] Python: $pyVer"
} catch {
    Write-Host "[X] 未检测到 Python，请先安装 Python 3.11+" -ForegroundColor Red
    exit 1
}

try {
    $nodeVer = node --version 2>&1
    Write-Host "[OK] Node: $nodeVer"
} catch {
    Write-Host "[X] 未检测到 Node.js，请先安装 Node.js 18+" -ForegroundColor Red
    exit 1
}

$backendDir = Join-Path $root "backend"
$frontendDir = Join-Path $root "frontend"
$venvDir = Join-Path $backendDir ".venv"
$venvPython = Join-Path $venvDir "Scripts\python.exe"
$pyinstallerExe = Join-Path $venvDir "Scripts\pyinstaller.exe"
$specFile = Join-Path $root "OfferTrack.spec"

Write-Host ""
Write-Host "-> [1/4] 构建前端静态文件..." -ForegroundColor Yellow
Push-Location $frontendDir
if (-not (Test-Path "node_modules")) {
    Write-Host "   首次打包：安装前端依赖（可能耗时 1~2 分钟）..."
    npm install
}
npm run build
Pop-Location
if (-not (Test-Path (Join-Path $frontendDir "dist\index.html"))) {
    Write-Host "[X] 前端构建失败，未找到 frontend\dist\index.html" -ForegroundColor Red
    exit 1
}
Write-Host "   [OK] 前端已构建到 frontend\dist\"

Write-Host ""
Write-Host "-> [2/4] 准备后端虚拟环境..." -ForegroundColor Yellow
if (-not (Test-Path $venvDir)) {
    Write-Host "   首次打包：创建后端 venv..."
    Push-Location $backendDir
    python -m venv .venv
    Pop-Location
}
& $venvPython -m pip install --upgrade pip --quiet
& $venvPython -m pip install -r (Join-Path $backendDir "requirements.txt") --quiet
Write-Host "   [OK] 后端依赖已安装"

Write-Host ""
Write-Host "-> [3/4] 安装 PyInstaller..." -ForegroundColor Yellow
& $venvPython -m pip install pyinstaller --quiet
Write-Host "   [OK] PyInstaller 已安装"

Write-Host ""
Write-Host "-> [4/4] 调用 PyInstaller 打包..." -ForegroundColor Yellow
& $pyinstallerExe $specFile --noconfirm --clean
if ($LASTEXITCODE -ne 0) {
    Write-Host "[X] PyInstaller 打包失败" -ForegroundColor Red
    exit 1
}

$outputExe = Join-Path $root "dist\OfferTrack.exe"
if (Test-Path $outputExe) {
    $size = [math]::Round((Get-Item $outputExe).Length / 1MB, 1)
    Write-Host ""
    Write-Host "===============================================" -ForegroundColor Green
    Write-Host " [OK] 打包完成！" -ForegroundColor Green
    Write-Host " 产物：$outputExe ($size MB)" -ForegroundColor Green
    Write-Host " 用法：把 OfferTrack.exe 放到任意空文件夹双击运行" -ForegroundColor Green
    Write-Host "===============================================" -ForegroundColor Green
} else {
    Write-Host "[X] 未找到产物 $outputExe" -ForegroundColor Red
    exit 1
}
