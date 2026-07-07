@echo off
title 环境检查
echo ============================================
echo   AI JD简历适配系统 - 环境检查
echo ============================================
echo.

:: 检查Python
echo [1/6] 检查 Python ...
python --version >nul 2>&1
if errorlevel 1 (
    echo   ❌ 未安装 Python
    echo   请从 https://www.python.org/downloads/ 安装 Python 3.10+
) else (
    for /f "tokens=*" %%i in ('python --version 2^>^&1') do set "PY_VER=%%i"
    echo   ✅ %PY_VER%
)

:: 检查Node.js
echo [2/6] 检查 Node.js ...
node --version >nul 2>&1
if errorlevel 1 (
    echo   ❌ 未安装 Node.js
    echo   请从 https://nodejs.org/ 安装 Node.js 18+
) else (
    for /f "tokens=*" %%i in ('node --version') do set "NODE_VER=%%i"
    echo   ✅ %NODE_VER%
)

:: 检查Chrome
echo [3/6] 检查 Chrome ...
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe" >nul 2>&1
if errorlevel 1 (
    echo   ⚠️ 未检测到 Chrome（Selenium需要）
    echo   请从 https://www.google.com/chrome/ 安装
) else (
    echo   ✅ Chrome 已安装
)

:: 检查Ollama
echo [4/6] 检查 Ollama 服务 ...
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo   ⚠️ Ollama 服务未运行
    echo   请启动 Ollama（https://ollama.com/）
) else (
    echo   ✅ Ollama 服务运行中
)

:: 检查后端依赖
echo [5/6] 检查后端依赖 ...
if exist "%ROOT_DIR%\backend\venv\Scripts\activate.bat" (
    echo   ✅ Python虚拟环境已创建
) else (
    echo   ⚠️ Python虚拟环境未创建
    echo   运行 start.bat 或手动执行:
    echo   cd backend ^&^& python -m venv venv
)

:: 检查前端依赖
echo [6/6] 检查前端依赖 ...
if exist "%ROOT_DIR%\frontend\node_modules" (
    echo   ✅ 前端依赖已安装
) else (
    echo   ⚠️ 前端依赖未安装
    echo   运行 start.bat 或手动执行:
    echo   cd frontend ^&^& npm install
)

echo.
echo ============================================
echo   检查完成！
echo   全部 ✅ 即可正常运行
echo   有 ⚠️ 则需安装对应组件
echo   有 ❌ 则必须安装
echo ============================================
echo.
pause
