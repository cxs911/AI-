# AI JD简历适配系统 - 安装配置脚本
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  AI JD简历适配系统 v1.0.0 - 安装配置" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# 检查管理员权限
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "[提示] 建议以管理员身份运行此脚本，某些操作可能需要权限" -ForegroundColor Yellow
}

# 进入项目根目录
$rootDir = Split-Path -Parent (Split-Path -Parent $PSCommandPath)
Set-Location $rootDir

# 检查Python
try {
    $pyVersion = python --version
    Write-Host "[OK] Python: $pyVersion" -ForegroundColor Green
} catch {
    Write-Host "[错误] 未检测到Python 3.10+" -ForegroundColor Red
    Write-Host "       请从 https://www.python.org/downloads/ 安装"
    exit 1
}

# 检查Node.js
try {
    $nodeVersion = node --version
    Write-Host "[OK] Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "[错误] 未检测到Node.js 18+" -ForegroundColor Red
    Write-Host "       请从 https://nodejs.org/ 安装"
    exit 1
}

# 检查Chrome
try {
    $chrome = Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe" -ErrorAction SilentlyContinue
    if ($chrome) {
        Write-Host "[OK] Chrome 已检测" -ForegroundColor Green
    }
} catch {
    Write-Host "[提示] 未检测到Chrome，Selenium需要Chrome浏览器" -ForegroundColor Yellow
}

# 检查Ollama
try {
    $ollama = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method Get -ErrorAction SilentlyContinue
    if ($ollama) {
        Write-Host "[OK] Ollama 服务运行中" -ForegroundColor Green
    }
} catch {
    Write-Host "[提示] Ollama 服务未运行，请确保已启动Ollama" -ForegroundColor Yellow
    Write-Host "       下载: https://ollama.com/"
    Write-Host "       安装后执行: ollama pull qwen2.5:7b"
}

Write-Host ""
Write-Host "--- 安装后端依赖 ---" -ForegroundColor Cyan
Set-Location "$rootDir\backend"
if (-not (Test-Path "venv")) {
    python -m venv venv
    Write-Host "[OK] 虚拟环境已创建" -ForegroundColor Green
}

# 激活虚拟环境
$venvActivate = "$rootDir\backend\venv\Scripts\Activate.ps1"
& $venvActivate

pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] 后端依赖安装完成" -ForegroundColor Green
} else {
    Write-Host "[警告] 部分依赖安装失败，请手动检查" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "--- 安装前端依赖 ---" -ForegroundColor Cyan
Set-Location "$rootDir\frontend"
npm install --registry=https://registry.npmmirror.com
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] 前端依赖安装完成" -ForegroundColor Green
} else {
    Write-Host "[警告] 前端依赖安装失败" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  安装完成！" -ForegroundColor Cyan
Write-Host "  请使用 start.bat 启动系统" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

Set-Location $rootDir
