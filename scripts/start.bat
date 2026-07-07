@echo off
title AI JD简历适配系统 - 启动器

set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:\=/%"

echo ============================================
echo   AI JD简历适配系统 v1.0.0
echo   正在启动...
echo ============================================
echo.

:: 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] 未检测到Python
    echo         请安装 Python 3.10+: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version 2^>^&1') do echo [OK] %%i

:: 检查Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] 未检测到Node.js
    echo         请安装 Node.js 18+: https://nodejs.org/
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('node --version') do echo [OK] %%i

echo.

:: ========== 安装后端依赖 ==========
echo [1/3] 安装后端依赖...
cd /d "%~dp0..\backend"

if not exist "venv" (
    echo   -- 创建Python虚拟环境...
    python -m venv venv
)
echo   -- 激活虚拟环境并安装包...
call venv\Scripts\activate.bat
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
if errorlevel 1 (
    echo [WARN] pip安装遇到问题，继续尝试启动...
)
echo [OK]
echo.

:: ========== 安装前端依赖 ==========
echo [2/3] 安装前端依赖...
cd /d "%~dp0..\frontend"

if not exist "node_modules" (
    echo   -- 首次安装需要下载依赖，请稍候...
    call npm install --registry=https://registry.npmmirror.com
)
echo [OK]
echo.

:: ========== 启动服务 ==========
echo [3/3] 启动服务...

echo   -- 启动后端 (端口 8000) ...
:: 用独立的bat启动，避免引号嵌套问题
start "AI-JD-Backend" "%~dp0run_backend.bat"
if errorlevel 1 (
    echo [ERROR] 后端启动失败
    pause
    exit /b 1
)

echo   -- 等待后端初始化...
timeout /t 4 /nobreak >nul

echo   -- 启动前端 (端口 3000) ...
start "AI-JD-Frontend" "%~dp0run_frontend.bat"

echo.
echo ============================================
echo   启动完成！
echo.
echo   前端页面: http://localhost:3001
echo   后端接口: http://localhost:8000
echo   API文档: http://localhost:8000/docs
echo.
echo   下一步操作:
echo   1. 确认 Ollama 服务已启动
echo   2. 打开浏览器访问 http://localhost:3001
echo   3. 在投递管理 -> 启动浏览器 -> 扫码登录
echo.
echo   停止服务: 关闭 AI-JD-Backend / AI-JD-Frontend 窗口
echo ============================================
echo.
pause
