#!/usr/bin/env pwsh
$ErrorActionPreference = "Stop"
$root = $PSScriptRoot

Write-Host "=== OfferTrack 启动 ===" -ForegroundColor Cyan

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

if (-not (Test-Path $venvDir)) {
    Write-Host "-> 首次运行：创建后端虚拟环境..." -ForegroundColor Yellow
    Push-Location $backendDir
    python -m venv .venv
    Write-Host "-> 安装后端依赖..." -ForegroundColor Yellow
    & $venvPython -m pip install --upgrade pip --quiet
    & $venvPython -m pip install -r requirements.txt
    Pop-Location
}

if (-not (Test-Path (Join-Path $frontendDir "node_modules"))) {
    Write-Host "-> 首次运行：安装前端依赖（可能耗时 1~2 分钟）..." -ForegroundColor Yellow
    Push-Location $frontendDir
    npm install
    Pop-Location
}

Write-Host "-> 启动后端 (http://localhost:8000) ..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendDir'; & '$venvPython' -m uvicorn app.main:app --reload"

Write-Host "-> 启动前端 (http://localhost:5173) ..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendDir'; npm run dev"

Start-Sleep -Seconds 3
Write-Host ""
Write-Host "[OK] 启动完成！浏览器打开 http://localhost:5173" -ForegroundColor Cyan
Write-Host "    关闭服务：直接关掉两个新弹出的 PowerShell 窗口"
