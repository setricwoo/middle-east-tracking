@echo off
chcp 65001 >nul
echo ========================================
echo 自动更新实时新闻任务
echo 开始时间: %date% %time%
echo ========================================

cd /d "D:\python_code\海湾以来-最新"

python auto_update_news.py >> auto_update_log.txt 2>&1

if %errorlevel% neq 0 (
    echo [错误] 更新失败，请检查日志
    exit /b 1
) else (
    echo [成功] 更新完成
    exit /b 0
)
