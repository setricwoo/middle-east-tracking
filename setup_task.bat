@echo off
chcp 65001 >nul
echo ========================================
echo 设置自动更新任务计划程序
echo ========================================

set "taskName=MiddleEast_News_AutoUpdate"
set "scriptPath=D:\python_code\海湾以来-最新\auto_update_news.bat"

:: 删除已存在的任务
schtasks /Delete /TN "%taskName%" /F 2>nul

:: 创建每小时执行的任务
:: 使用当前用户权限，每小时重复执行
schtasks /Create /TN "%taskName%" /TR "\"%scriptPath%\"" /SC HOURLY /ST 00:00 /RU "%USERNAME%" /RL LIMITED /F

if %errorlevel% equ 0 (
    echo [成功] 计划任务已创建！
    echo [任务名称] %taskName%
    echo [执行脚本] %scriptPath%
    echo [执行频率] 每小时一次
    echo [下次执行] 下一个整点
    echo.
    echo 你可以通过以下方式管理任务：
    echo 1. 运行 taskschd.msc 打开任务计划程序
    echo 2. 或在命令行运行: schtasks /Query /TN "%taskName%"
    echo 3. 删除任务: schtasks /Delete /TN "%taskName%" /F
) else (
    echo [失败] 创建计划任务失败，错误代码: %errorlevel%
)

pause
