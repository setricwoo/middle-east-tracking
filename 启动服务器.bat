@echo off
chcp 65001 >nul
echo ==========================================
echo 启动本地HTTP服务器
echo 访问地址: http://localhost:8080/war-situation.html
echo ==========================================
echo.
python start_server.py
pause
