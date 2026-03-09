# 创建每小时自动更新新闻的Windows计划任务
$taskName = "MiddleEast_News_AutoUpdate"
$taskDescription = "每小时自动更新中东实时新闻网页并上传至GitHub"

# 任务执行路径
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -WindowStyle Hidden -File `"D:\python_code\海湾以来-最新\auto_update_news_wrapper.ps1`""

# 触发器：每小时执行一次
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration (New-TimeSpan -Days 365)

# 任务设置
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable

# 使用当前用户运行
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -LogonType Interactive

# 注册任务
try {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description $taskDescription
    Write-Host "[成功] 计划任务 '$taskName' 已创建！" -ForegroundColor Green
    Write-Host "[信息] 任务将每小时自动执行一次" -ForegroundColor Cyan
    Write-Host "[信息] 下次执行时间: $((Get-Date).AddMinutes(1))" -ForegroundColor Cyan
} catch {
    Write-Host "[错误] 创建计划任务失败: $_" -ForegroundColor Red
}
