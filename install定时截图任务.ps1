# PowerShell script - Install MarineTraffic screenshot task
# Run as Administrator

$TaskName = "marine_screenshot"
$ScriptPath = "D:\python_code\海湾以来-最新\auto_marine_screenshot.py"

# Create task action
$Action = New-ScheduledTaskAction -Execute "python" -Argument $ScriptPath -WorkingDirectory "D:\python_code\海湾以来-最新"

# Create trigger (every 20 minutes)
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date)
$Trigger.Repetition.Interval = [TimeSpan]::FromMinutes(20)

# Create settings
$Settings = New-ScheduledTaskSettings -StartWhenAvailable $true

# Register task
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings

Write-Host ""
Write-Host "Task installed successfully!"
Write-Host ""
Write-Host "Commands:"
Write-Host "  Run now: schtasks /run /tn marine_screenshot"
Write-Host "  Query status: schtasks /query /tn marine_screenshot"
Write-Host "  Delete task: schtasks /delete /tn marine_screenshot"
