@echo off
chcp 65001 >nul
echo ========================================
echo 中东新闻自动更新 - 循环模式
echo ========================================
echo 此窗口将保持运行，每20分钟自动执行更新
echo 按 Ctrl+C 可停止运行
echo ========================================
echo.

:loop
cls
echo [%date% %time%] 执行自动更新...
python "D:\python_code\海湾以来-最新\auto_update_news.py"

echo.
echo [%date% %time%] 本次更新完成，等待下次执行...
echo 下次执行时间: 20分钟后
echo.

:: 等待1200秒（20分钟）
timeout /t 1200 /nobreak >nul
goto loop
