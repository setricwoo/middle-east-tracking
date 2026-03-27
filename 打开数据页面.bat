@echo off
chcp 65001 >nul
echo ==========================================
echo   启动本地数据追踪页面
echo ==========================================
echo.
echo 正在检查Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请安装Python
    pause
    exit /b 1
)

echo [1/3] Python已找到
echo [2/3] 正在生成本地版本...
python generate_local_html.py

echo [3/3] 正在启动HTTP服务器 (端口8000)...
start /B python -m http.server 8000 >nul 2>&1

:: 等待服务器启动
timeout /t 2 /nobreak >nul

echo.
echo ==========================================
echo   正在打开页面...
echo   地址: http://localhost:8000/data-tracking.html
echo ==========================================
start http://localhost:8000/data-tracking.html

echo.
echo 提示: 按任意键关闭服务器窗口
echo.
pause
:: 关闭Python服务器
taskkill /F /IM python.exe /FI "WINDOWTITLE eq http.server*" >nul 2>&1
