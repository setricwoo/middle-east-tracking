$taskName = "marine_screenshot"
$scriptPath = "D:\python_code\海湾以来-最新\auto_marine_screenshot.py"
$workDir = "D:\python_code\海湾以来-最新"

# Delete existing task if any
try {
    Unregister-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
} catch {}

# Create action
$action = New-ScheduledTaskAction -Execute "pythonw.exe" -Argument $scriptPath -WorkingDirectory $workDir

# Create trigger - every 20 minutes
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date)
$trigger.Repetition.Interval = [TimeSpan]::FromMinutes(20)

# Settings
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable $true

# Register
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings

Write-Host ""
Write-Host "Task created successfully!"
Write-Host ""
schtasks /query /tn $taskName
