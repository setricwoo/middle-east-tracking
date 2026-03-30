# PowerShell脚本 - 安装MarineTraffic定时截图任务
# 以管理员身份运行此脚本

$TaskName = "marine_screenshot"
$ScriptPath = "D:\python_code\海湾以来-最新\auto_marine_screenshot.py"
$Interval = 20  # 分钟

Write-Host "正在创建定时任务: $TaskName"

# 删除已存在的任务
Unregister-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue

# 创建新任务
$Action = New-ScheduledTaskAction -Execute "python" -Argument "$ScriptPath"
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date)
$Settings = New-ScheduledTaskSettings -StartWhenAvailable $true

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings

Write-Host "任务创建成功!"
Write-Host ""
Write-Host "任务详情:"
Get-ScheduledTask -TaskName $TaskName | Format-List

Write-Host ""
Write-Host "使用方法:"
Write-Host "1. 双击运行 '启动MarineTraffic截图.bat'"
Write-Host "2. 在Edge中打开MarineTraffic网站"
Write-Host "3. 每$Interval分钟会自动截图"
Write-Host ""
Write-Host "管理命令:"
Write-Host "  立即运行: schtasks /run /tn marine_screenshot"
Write-Host "  查看状态: schtasks /query /tn marine_screenshot"
Write-Host "  删除任务: schtasks /delete /tn marine_screenshot"
