@echo off
chcp 65001 >nul
echo ========================================
echo 启动本地HTTP服务器
echo 访问地址: http://localhost:8080
echo ========================================
echo.
echo 支持的页面:
echo   - http://localhost:8080/tracking.html  (海峡跟踪)
echo   - http://localhost:8080/data-tracking.html  (数据跟踪)
echo   - http://localhost:8080/war-situation.html  (战争形势)
echo   - http://localhost:8080/index.html  (首页)
echo.
echo 按 Ctrl+C 停止服务器
echo ========================================
python -m http.server 8080
pause
