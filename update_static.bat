@echo off
chcp 65001 >nul
echo ==========================================
echo Polymarket 静态网页数据更新工具
echo ==========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请确保Python已安装并添加到PATH
    pause
    exit /b 1
)

REM 检查数据文件是否存在
if not exist "iran_events.json" (
    echo 未找到数据文件，先执行数据获取...
    python update_polymarket.py
    echo.
)

echo 正在更新静态网页数据...
python update_polymarket_static.py

if errorlevel 1 (
    echo.
    echo 更新失败
    pause
    exit /b 1
)

echo.
pause
