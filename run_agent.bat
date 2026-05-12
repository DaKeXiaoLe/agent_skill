@echo off
chcp 65001 >nul

REM Agent SKILL智能体启动脚本
REM 用法: 双击此文件或从命令行运行

echo ================================================
echo [Agent SKILL Smart Assistant]
echo ================================================

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found. Please install Python 3.7 or higher.
    pause
    exit /b 1
)

python -c "import sys; print('Python version:', sys.version_info.major, sys.version_info.minor, sys.version_info.micro)"
if errorlevel 1 (
    echo Error: Python cannot run.
    pause
    exit /b 1
)

REM 检查依赖是否安装
echo Checking dependencies...
python -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo Error: requests module not installed. Please run: pip install requests
    pause
    exit /b 1
)

python -c "import openai" >nul 2>&1
if errorlevel 1 (
    echo Error: openai module not installed. Please run: pip install openai
    pause
    exit /b 1
)

echo.
echo Starting Agent SKILL Smart Assistant...
echo Interactive terminal will open.
echo.

REM 在新窗口中启动智能体，并将输出重定向到日志文件
start "Agent SKILL Assistant" python main.py 

echo You can close this window.
timeout /t 2 /nobreak >nul
