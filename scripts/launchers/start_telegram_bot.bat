@echo off
chcp 65001 >nul

:: Telegram 机器人启动脚本
:: 使用方法：
:: 1. 确保已设置 TELEGRAM_BOT_TOKEN 环境变量
:: 2. 确保后端服务已启动
:: 3. 运行此脚本

echo ========================================
echo   Telegram 机器人启动脚本
echo ========================================

echo [检查] 检查环境变量...
if "%TELEGRAM_BOT_TOKEN%" == "" (
    echo [错误] 请设置 TELEGRAM_BOT_TOKEN 环境变量
    echo [提示] 可以在系统环境变量中设置，或在启动前执行：
    echo        set TELEGRAM_BOT_TOKEN=your_bot_token
    pause
    exit /b 1
)

echo [检查] 检查 Python 环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] Python 未安装或未添加到 PATH
    pause
    exit /b 1
)

echo [检查] 检查依赖...
pip list | findstr "python-telegram-bot" >nul 2>&1
if %errorlevel% neq 0 (
    echo [安装] 安装 python-telegram-bot 依赖...
    pip install python-telegram-bot
    if %errorlevel% neq 0 (
        echo [错误] 安装依赖失败
        pause
        exit /b 1
    )
)

echo [启动] 启动 Telegram 机器人...
echo [提示] 机器人将连接到后端服务 http://localhost:7000

echo [日志] 启动机器人服务...
python "%~dp0..\..\syn_backend\telegram_bot.py"

pause
