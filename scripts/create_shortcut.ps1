#!/usr/bin/env pwsh
<#
.SYNOPSIS
  在桌面创建/重建 OfferTrack 快捷方式，并显式指定图标，绕过 Windows 图标缓存。

.PARAMETER OutDir
  快捷方式输出目录，默认当前用户桌面。

.PARAMETER Name
  快捷方式文件名（不含后缀），默认 "OfferTrack"。

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File scripts\create_shortcut.ps1
#>
[CmdletBinding()]
param(
  [string] $OutDir = [Environment]::GetFolderPath('Desktop'),
  [string] $Name = 'OfferTrack'
)

$ErrorActionPreference = 'Stop'

# 项目根 = 本脚本所在目录的父目录
$root = Split-Path -Parent (Split-Path -Parent $PSCommandPath)
$exe  = Join-Path $root 'dist\OfferTrack.exe'
$ico  = Join-Path $root 'assets\app.ico'

if (-not (Test-Path -LiteralPath $exe)) { throw "找不到 exe：$exe（先跑 build.ps1）" }
if (-not (Test-Path -LiteralPath $ico)) { throw "找不到图标：$ico" }
if (-not (Test-Path -LiteralPath $OutDir)) { New-Item -ItemType Directory -Path $OutDir -Force | Out-Null }

# 1. 删旧 .lnk（含两种默认名 + Recent 里的同名）
$victims = @(
  (Join-Path $OutDir ($Name + '.lnk')),
  (Join-Path $OutDir ($Name + ' - 快捷方式.lnk')),
  (Join-Path $env:APPDATA 'Microsoft\Windows\Recent\OfferTrack.lnk')
)
foreach ($v in $victims) {
  if (Test-Path -LiteralPath $v) {
    Write-Output "[del] $v"
    Remove-Item -LiteralPath $v -Force -Confirm:$false
  }
}

# 2. 软刷新图标缓存（不重启 explorer，最低破坏）
try {
  & ie4uinit.exe -show 2>$null | Out-Null
  Write-Output "[ok] ie4uinit.exe -show 已触发"
} catch {
  Write-Output "[warn] ie4uinit 调用失败（不影响后续创建）：$($_.Exception.Message)"
}

# 3. 创建新的 .lnk，显式指定 IconLocation 指向 .ico 文件（绕开 PE 资源缓存）
$lnkPath = Join-Path $OutDir ($Name + '.lnk')
$shell   = New-Object -ComObject WScript.Shell
$lnk     = $shell.CreateShortcut($lnkPath)
$lnk.TargetPath       = $exe
$lnk.WorkingDirectory = (Split-Path -Parent $exe)
$lnk.IconLocation     = "$ico,0"
$lnk.Description      = 'OfferTrack - 求职追踪'
$lnk.WindowStyle      = 1   # SW_SHOWNORMAL
$lnk.Save()

# 4. 验证写入
$verify = $shell.CreateShortcut($lnkPath)
Write-Output ""
Write-Output "[OK] 快捷方式已创建：$lnkPath"
Write-Output "  TargetPath   = $($verify.TargetPath)"
Write-Output "  IconLocation = $($verify.IconLocation)"
Write-Output "  WorkingDir   = $($verify.WorkingDirectory)"
Write-Output ""
Write-Output "如果桌面上仍然显示旧图标，按 F5 刷新一次桌面；还不行就跑："
Write-Output "  taskkill /im explorer.exe /f"
Write-Output "  Remove-Item `$env:LOCALAPPDATA\IconCache.db -Force -EA SilentlyContinue"
Write-Output "  Remove-Item `$env:LOCALAPPDATA\Microsoft\Windows\Explorer\iconcache_*.db -Force -EA SilentlyContinue"
Write-Output "  start explorer.exe"
