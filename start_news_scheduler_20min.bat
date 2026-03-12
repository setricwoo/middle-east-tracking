@echo off
chcp 65001
echo ==========================================
echo  20分钟新闻定时更新任务
echo ==========================================
echo.
echo 执行内容：
echo   1. 更新实时新闻（财联社）
echo   2. 更新Polymarket预测数据
echo   3. 推送到GitHub
echo.
echo 执行频率：每20分钟
echo.
echo 正在启动调度器...
echo 按 Ctrl+C 可停止
echo.

python news_scheduler_20min.py

pause
