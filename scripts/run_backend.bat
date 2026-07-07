@echo off
title AI-JD-Backend
cd /d "%~dp0..\backend"
call venv\Scripts\activate.bat
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
if errorlevel 1 (
    echo.
    echo [错误] 后端启动失败，按任意键退出
    pause
)
