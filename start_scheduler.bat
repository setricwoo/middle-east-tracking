@echo off
chcp 65001 >nul
title 中东新闻自动更新 - 每20分钟
cls
echo ============================================
echo   中东新闻自动更新服务
echo ============================================
echo   频率: 每20分钟执行一次
echo   操作: 爬取财联社新闻 + 增量更新 + GitHub上传
echo   特点: 
          - 保留所有旧新闻
echo          - 自动去重
echo          - 新增新闻置顶显示
echo   日志: scheduler_log.txt
echo   停止: 按 Ctrl+C 或关闭此窗口
echo ============================================
echo.
echo 正在初始化...
echo.

:: 安装schedule库（如果未安装）
pip install schedule -q

:: 执行调度器
echo [启动] 调度器已启动，等待执行...
echo.
python scheduler.py

pause
