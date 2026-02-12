@echo off
chcp 65001 >nul
REM ==========================================
REM Chromium 浏览器下载脚本
REM 用于抖音/小红书/快手上传（比 Chrome 更快、更稳定）
REM ==========================================

REM 设置 Playwright 浏览器下载路径（Chromium 专用文件夹）
set "ROOT=%~dp0"
set "PLAYWRIGHT_BROWSERS_PATH=%ROOT%browsers\chromium"

echo ==========================================
echo   下载 Chromium 浏览器（抖音/小红书/快手）
echo ==========================================
echo.
echo 目标路径: %PLAYWRIGHT_BROWSERS_PATH%
echo.

REM 下载 Chromium       
cd syn_backend
python -m playwright install chromium

echo.
echo ==========================================
echo ✅ Chromium 已下载完成
echo ==========================================
echo.
echo 浏览器结构:
echo   项目根目录\browsers\
echo   ├── chromium\       ← Chromium（抖音/小红书/快手）
echo   ├── firefox\        ← Firefox（视频号）
echo   └── chrome-for-testing\  ← Chrome for Testing（备用）
echo.
pause
