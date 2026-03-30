@echo off
chcp 65001 >nul
title 安装MarineTraffic定时截图任务

echo ================================================
echo   安装 MarineTraffic 定时截图任务
echo ================================================
echo.

:: 获取当前用户名
for /f "tokens=2 delims=\" %%a in ('whoami /user /fo list ^| findstr "User:"') do set USERNAME=%%a
for /f "tokens=3" %%a in ('whoami /user /fo list ^| findstr "SID:"') do set USERSID=%%a

echo 当前用户: %USERNAME%
echo.

:: 更新XML中的用户SID
echo [1/3] 更新任务配置...
powershell -Command "(Get-Content 'marine_screenshot_task.xml') -replace 'S-1-5-21-3905708099-1838249906-2080767689-1001', '%USERSID%' | Set-Content 'marine_screenshot_task.xml'"

:: 删除已存在的任务（如果有）
echo [2/3] 删除旧任务（如果存在）...
schtasks /delete /tn "marine_screenshot" /f >nul 2>&1

:: 创建新任务
echo [3/3] 创建定时任务...
schtasks /create /tn "marine_screenshot" /xml "marine_screenshot_task.xml"

if %errorlevel% equ 0 (
    echo.
    echo ================================================
    echo   安装成功!
    echo ================================================
    echo.
    echo   任务名称: marine_screenshot
    echo   执行频率: 每20分钟
    echo   执行脚本: auto_marine_screenshot.py
    echo.
    echo   使用方法:
    echo   1. 双击运行 "启动MarineTraffic截图.bat"
    echo   2. 在Edge中打开MarineTraffic网站
    echo   3. 每20分钟会自动截图
    echo.
    echo   管理命令:
    echo   - 查看任务: schtasks /query /tn "marine_screenshot"
    echo   - 立即运行: schtasks /run /tn "marine_screenshot"
    echo   - 删除任务: schtasks /delete /tn "marine_screenshot"
    echo ================================================
) else (
    echo.
    echo [ERROR] 安装失败，请以管理员身份运行此脚本
)

echo.
echo 按任意键关闭此窗口（定时任务将继续在后台运行）...
timeout /t 3 /nobreak >nul
exit
