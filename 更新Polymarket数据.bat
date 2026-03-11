@echo off
chcp 65001 >nul
echo === 更新 Polymarket 伊朗预测市场数据 ===
echo.
python update_polymarket_data.py
if %errorlevel% == 0 (
    echo.
    echo 正在打开页面...
    start polymarket_events.html
) else (
    echo.
    echo [错误] 更新失败
)
pause
