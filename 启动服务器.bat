@echo off
chcp 65001 >nul
echo ========================================
echo  启动本地服务器
echo ========================================
echo.
echo 正在启动服务器，请稍候...
echo.
python start_server.py
pause
