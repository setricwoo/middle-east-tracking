@echo off
chcp 65001 >nul
echo ===========================================
echo    Polymarket 伊朗预测市场 - TOP10 更新
echo ===========================================
echo.
python update_polymarket_top10.py
if %errorlevel% == 0 (
    echo.
    echo 正在打开页面...
    start polymarket_top10.html
) else (
    echo.
    echo [错误] 更新失败，请检查网络连接
)
echo.
pause
