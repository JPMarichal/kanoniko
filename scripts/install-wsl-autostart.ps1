# Run this script once as Administrator to enable WSL Ubuntu auto-start on login.
# This ensures Docker Engine + Alejandria containers start automatically.
#
# Usage (elevated PowerShell):
#   powershell -ExecutionPolicy Bypass -File C:\own\alejandria\scripts\install-wsl-autostart.ps1

$taskName = "WSL-Ubuntu-Autostart"
$action = New-ScheduledTaskAction -Execute "wsl.exe" -Argument "-d Ubuntu-20.04 -- echo started"
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -RunLevel Highest

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force

Write-Host "Task '$taskName' created. WSL Ubuntu-20.04 will start on login." -ForegroundColor Green
Write-Host "Docker Engine (systemd) will start automatically, then containers with restart:unless-stopped." -ForegroundColor Cyan
