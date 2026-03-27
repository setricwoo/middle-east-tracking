@echo off
chcp 65001 >nul
echo ==========================================
echo  正在启动本地服务器...
echo  浏览器将自动打开页面
echo ==========================================
echo.
cd /d "%~dp0"
start http://localhost:8000/tracking.html
python -m http.server 8000
