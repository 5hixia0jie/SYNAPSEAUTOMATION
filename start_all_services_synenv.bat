@echo off
chcp 65001 >nul
REM Set UTF-8 encoding environment
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

set "REDIS_CLI=redis-cli"
if exist "D:\Redis\Redis-x64-5.0.14.1\redis-cli.exe" set "REDIS_CLI=D:\Redis\Redis-x64-5.0.14.1\redis-cli.exe"
if exist "D:\Redis\Redis-x64-5.0.14.1\redis-server.exe" set "SYNAPSE_REDIS_PATH=D:\Redis\Redis-x64-5.0.14.1\redis-server.exe"

echo ============================================
echo   SynapseAutomation 全服务启动 (synenv)
echo ============================================
echo.
echo 说明: 本模式各服务独立启动（开发调试模式）
echo   - 每个服务在独立窗口运行，方便查看日志
echo   - 适用于开发调试场景
echo.
echo 如需使用 Supervisor 统一管理模式，请运行:
echo   start_all_with_supervisor.bat
echo.

REM
echo [1] 检查 Redis 服务...
%REDIS_CLI% -a 123456 ping >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Redis 未运行，正在启动...
    REM 使用指定路径的 Redis
    if exist "%SYNAPSE_REDIS_PATH%" (
        echo 正在启动 Redis: %SYNAPSE_REDIS_PATH%
        echo 使用配置文件: D:\traeProject\SYNAPSEAUTOMATION\redis.conf
        start "Redis Server" "%SYNAPSE_REDIS_PATH%" "D:\traeProject\SYNAPSEAUTOMATION\redis.conf"
    ) else (
        echo ❌ Redis 可执行文件不存在: %SYNAPSE_REDIS_PATH%
        pause
        exit /b 1
    )
    timeout /t 3 /nobreak >nul

    REM 再次检查
    %REDIS_CLI% -a 123456 ping >nul 2>&1
    if errorlevel 1 (
        echo ❌ Redis 启动失败，请手动运行: %SYNAPSE_REDIS_PATH%
        pause
        exit /b 1
    )
    echo ✅ Redis 已启动
) else (
    echo ✅ Redis 运行正常
)

echo.
echo [2] 启动 Celery Worker（发布任务队列）...
start "Celery Worker (synenv)" "%~dp0start_celery_worker_synenv.bat"
timeout /t 2 /nobreak >nul

echo.
echo [3] 启动 Playwright Worker（浏览器自动化，端口7002）...
start "Playwright Worker" "%~dp0scripts\launchers\start_worker_synenv.bat"
timeout /t 3 /nobreak >nul

echo.
echo [4] 启动 FastAPI Backend（后端API，端口7000）...
start "FastAPI Backend" "%~dp0scripts\launchers\start_backend_synenv.bat"
timeout /t 3 /nobreak >nul

echo.
echo [5] 启动 Frontend（前端界面，端口3000）...
start "React Frontend" "%~dp0scripts\launchers\start_frontend.bat"
timeout /t 2 /nobreak >nul

echo.
echo [6] 启动 Telegram 机器人...
echo 提示: 请确保已设置 TELEGRAM_BOT_TOKEN 环境变量
echo 如需设置，请在系统环境变量中添加: TELEGRAM_BOT_TOKEN=your_bot_token
REM 检查当前 shell 类型，如果是 PowerShell，则使用 PowerShell 脚本
if "%SHELL%"=="powershell" (
    start "Telegram Bot" powershell -ExecutionPolicy Bypass -File "%~dp0scripts\launchers\Start-TelegramBot.ps1"
) else (
    start "Telegram Bot" "%~dp0scripts\launchers\start_telegram_bot.bat"
)

echo.
echo ============================================
echo   ✅ 所有服务已启动
echo ============================================
echo.
echo 服务列表:
echo   - Redis Server        (localhost:6379)
echo   - Celery Worker       (任务队列)
echo   - Playwright Worker   (localhost:7002)
echo   - FastAPI Backend     (http://localhost:7000)
echo   - React Frontend      (http://localhost:3000)
echo   - Telegram Bot        (消息处理)
echo.
echo 提示:
echo   - 各服务会在独立窗口中运行
echo   - 关闭窗口即可停止对应服务
echo   - 查看日志请切换到对应窗口
echo.
pause
