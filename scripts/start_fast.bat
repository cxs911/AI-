@echo off
title AI JD简历适配系统 - 快速启动

:: ===== 直接启动，不检查依赖 =====
:: 前提：已经运行过 start.bat 完成了安装
:: ==================================

set "SCRIPT_DIR=%~dp0"
set "ROOT_DIR=%SCRIPT_DIR%.."

echo 启动后端服务...
start "AI-JD-Backend" cmd /c "title AI-JD-Backend && cd /d \"%ROOT_DIR%\backend\" && call venv\Scripts\activate.bat && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

timeout /t 3 /nobreak >nul

echo 启动前端服务...
start "AI-JD-Frontend" cmd /c "title AI-JD-Frontend && cd /d \"%ROOT_DIR%\frontend\" && npx vite --port 3001 --host"

echo.
echo 前端: http://localhost:3001
echo 后端: http://localhost:8000
echo.
echo 关闭后台服务请关掉对应的cmd窗口
echo.
pause
