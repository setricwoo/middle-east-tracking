@echo off
chcp 65001 >nul
title 中东新闻自动更新 - 每20分钟
cls
echo ========================================
echo 中东新闻自动更新服务
echo ========================================
echo 频率: 每20分钟
echo 操作: 财联社新闻爬取 + GitHub上传
echo 日志: scheduler_log.txt
echo ========================================
echo.

:: 安装schedule库（如果未安装）
pip install schedule -q

:: 执行调度器
python scheduler.py

pause
