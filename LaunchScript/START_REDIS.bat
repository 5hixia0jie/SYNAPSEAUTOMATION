@echo off
echo ========================================
echo Starting Redis Server
echo ========================================

set "REDIS_PATH=D:\Redis\Redis-x64-5.0.14.1"

if not exist "%REDIS_PATH%\redis-server.exe" (
    echo ERROR: redis-server.exe not found at %REDIS_PATH%
    pause
    exit /b 1
)

cd /d "%REDIS_PATH%"

echo Starting Redis on port 6379 with password protection...
start "Redis Server" cmd /k "redis-server.exe \"D:\traeProject\SYNAPSEAUTOMATION\redis.conf\""

echo.
echo Redis Server is starting in a new window...
echo.
pause
