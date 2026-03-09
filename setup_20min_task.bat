@echo off
chcp 65001 >nul
echo ========================================
echo 设置每20分钟自动更新任务
echo ========================================

set "taskName=MiddleEast_News_AutoUpdate"
set "scriptPath=D:\python_code\海湾以来-最新\auto_update_news.py"
set "pythonPath=python"

:: 先删除已存在的任务
echo [信息] 删除已存在的任务...
schtasks /Delete /TN "%taskName%" /F >nul 2>&1

:: 创建新的每20分钟任务
echo [信息] 创建新任务...
schtasks /Create /TN "%taskName%" /TR "%pythonPath% %scriptPath%" /SC MINUTE /MO 20 /RU "%USERNAME%" /RL LIMITED /F

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo [成功] 计划任务已创建！
    echo ========================================
    echo [任务名称] %taskName%
    echo [执行命令] %pythonPath% %scriptPath%
    echo [执行频率] 每20分钟一次
    echo.
    echo [管理命令]
    echo - 查看任务: schtasks /Query /TN "%taskName%"
    echo - 删除任务: schtasks /Delete /TN "%taskName%" /F
    echo - 运行任务: schtasks /Run /TN "%taskName%"
    echo.
    echo 日志文件: D:\python_code\海湾以来-最新\auto_update_log.txt
    echo ========================================
) else (
    echo [失败] 创建计划任务失败
    echo [提示] 请以管理员身份运行此脚本
)

pause
