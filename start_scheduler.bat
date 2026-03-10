@echo off
chcp 65001 >nul
title Middle East News Auto Update - Every 20min
cls
echo ============================================
echo   Middle East News Auto Update Service
echo ============================================
echo   Frequency: Every 20 minutes
echo   Operation: Crawl CLS News + Incremental Update + GitHub Upload
echo   Features: 
echo     - Keep all old news
echo     - Auto deduplication
echo     - New news on top
echo   Log: scheduler_log.txt
echo   Stop: Press Ctrl+C or close this window
echo ============================================
echo.
echo Initializing...
echo.

:: Install schedule library if not exists
pip install schedule -q 2>nul

:: Run scheduler
echo [Start] Scheduler started, waiting for execution...
echo.
python scheduler.py

pause
