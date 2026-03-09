@echo off
chcp 65001 >nul
echo ========================================
echo 中东新闻自动更新 - 循环模式
echo ========================================
echo 此窗口将保持运行，每小时自动执行更新
echo 按 Ctrl+C 可停止运行
echo ========================================
echo.

:loop
cls
echo [%date% %time%] 执行自动更新...
python "D:\python_code\海湾以来-最新\auto_update_news.py"

echo.
echo [%date% %time%] 本次更新完成，等待下次执行...
echo 下次执行时间: 1小时后
echo.

:: 等待3600秒（1小时）
timeout /t 3600 /nobreak >nul
goto loop
