@echo off
chcp 65001 >nul
echo ==========================================
echo Polymarket 数据更新工具
echo ==========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请确保Python已安装并添加到PATH
    pause
    exit /b 1
)

echo 正在更新Polymarket数据...
python update_polymarket.py

if errorlevel 1 (
    echo.
    echo 更新失败，请检查网络连接
    pause
    exit /b 1
)

echo.
echo 更新完成！
pause
