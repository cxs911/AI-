@echo off
title AI-JD-Frontend
cd /d "%~dp0..\frontend"
npx vite --port 3000 --host
if errorlevel 1 (
    echo.
    echo [错误] 前端启动失败，按任意键退出
    pause
)
