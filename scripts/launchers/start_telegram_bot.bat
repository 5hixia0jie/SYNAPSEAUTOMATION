@echo off
chcp 65001 >nul
:: Telegram Bot Start Script
:: Usage:
:: 1. Make sure TELEGRAM_BOT_TOKEN environment variable is set
:: 2. Make sure backend service is running
:: 3. Run this script

echo ========================================
echo   Telegram Bot Start Script (synenv)
echo ========================================
echo.

set "ROOT=%~dp0..\.."
set "BACKEND_DIR=%ROOT%\syn_backend"
set "VENV_PATH=%ROOT%\synenv"
set "PY=%VENV_PATH%\Scripts\python.exe"

REM Activate synenv virtual environment
if not exist "%PY%" (
    echo [ERROR] Virtual environment "synenv" not found at: %VENV_PATH%
    echo Please run: python -m venv synenv
    pause
    exit /b 1
)

call "%VENV_PATH%\Scripts\activate.bat"
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment 'synenv'
    pause
    exit /b 1
)
echo OK Activated virtual environment 'synenv'
set "PY=%VENV_PATH%\Scripts\python.exe"
if not exist "%PY%" set "PY=python"
echo.

REM Check environment variables
echo [Check] Checking environment variables...
if "%TELEGRAM_BOT_TOKEN%" == "" (
    echo [Error] Please set TELEGRAM_BOT_TOKEN environment variable
    echo [Hint] You can set it in system environment variables, or run before starting:
    echo        set TELEGRAM_BOT_TOKEN=your_bot_token
    pause
    exit /b 1
)

REM Check Python environment
echo [Check] Checking Python environment...
%PY% --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [Error] Python not found in virtual environment
    pause
    exit /b 1
)

REM Check dependencies
echo [Check] Checking dependencies...
%PY% -m pip list | findstr "python-telegram-bot" >nul 2>&1
if %errorlevel% neq 0 (
    echo [Install] Installing python-telegram-bot dependency...
    %PY% -m pip install python-telegram-bot
    if %errorlevel% neq 0 (
        echo [Error] Failed to install dependency
        pause
        exit /b 1
    )
)

pushd "%BACKEND_DIR%"

echo [Start] Starting Telegram Bot...
echo [Hint] Bot will connect to backend service http://localhost:7000
echo.
echo [Log] Starting bot service...
%PY% telegram_bot.py

popd

pause