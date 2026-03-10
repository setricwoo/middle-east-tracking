# 设置每小时定时任务
# 以管理员身份运行 PowerShell 执行此脚本

$TaskName = "MiddleEastTracking_Hourly"
$ScriptPath = "D:\python_code\海湾以来-最新\hourly_scheduler.py"
$PythonPath = "python"

# 检查是否已存在同名任务
$existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "任务 $TaskName 已存在，正在删除旧任务..."
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# 创建任务动作
$Action = New-ScheduledTaskAction -Execute $PythonPath -Argument $ScriptPath -WorkingDirectory "D:\python_code\海湾以来-最新"

# 创建触发器 - 每小时执行一次
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration (New-TimeSpan -Days 3650)

# 创建任务设置
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable

# 注册任务（以当前用户身份运行）
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description "中东跟踪系统每小时自动更新：简报、新闻、GitHub推送"

Write-Host ""
Write-Host "=========================================="
Write-Host "定时任务创建成功！"
Write-Host "=========================================="
Write-Host ""
Write-Host "任务名称: $TaskName"
Write-Host "执行频率: 每1小时"
Write-Host "执行内容:"
Write-Host "  1. 更新冲突每日简报"
Write-Host "  2. 更新实时新闻"  
Write-Host "  3. 推送到GitHub"
Write-Host ""
Write-Host "查看任务: 任务计划程序 -> $TaskName"
Write-Host ""
pause
