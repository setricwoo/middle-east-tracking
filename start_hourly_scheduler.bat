@echo off
chcp 65001
echo ==========================================
echo  每小时定时任务调度器
echo ==========================================
echo.
echo 执行内容：
echo   1. 更新冲突每日简报
echo   2. 更新实时新闻
echo   3. 推送到GitHub
echo.
echo 执行频率：每1小时
echo.
echo 正在启动调度器...
echo 按 Ctrl+C 可停止
echo.

python hourly_scheduler.py

pause
