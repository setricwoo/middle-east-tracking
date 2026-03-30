@echo off
chcp 65001 >nul
title MarineTraffic 截图服务

echo ================================================
echo   MarineTraffic 截图服务
echo ================================================
echo.
echo 此窗口会启动Edge浏览器调试模式，请保持此窗口打开
echo.
echo 步骤:
echo 1. 等待Edge浏览器启动
echo 2. 在Edge中访问MarineTraffic网站
echo 3. 每20分钟会自动截图
echo.
echo ================================================
echo.

:: 检查Edge是否已经在调试模式运行
curl -s http://localhost:9222/json/version >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] 检测到Edge调试模式已在运行
    goto :open_url
)

:: 启动Edge调试模式
echo [INFO] 正在启动Edge调试模式...
start "" msedge.exe --remote-debugging-port=9222

:: 等待Edge启动
timeout /t 5 /nobreak >nul

:open_url
:: 打开MarineTraffic网站
echo [INFO] 正在打开MarineTraffic网站...
start "" msedge.exe "https://www.marinetraffic.com/en/ais/home/centerx:55.8/centery:25.7/zoom:8"

echo.
echo ================================================
echo   Edge浏览器已启动!
echo.
echo   请在Edge中确认MarineTraffic网站已加载
echo   每20分钟会自动截图
echo.
echo   此窗口将在10秒后自动最小化到系统托盘
echo   截图服务会继续在后台运行
echo ================================================
echo.

:: 磭待10秒后自动关闭窗口（服务继续运行）
timeout /t 10 /nobreak >nul
exit
