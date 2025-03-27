# PowerShell script to set up Twitter Manager as a scheduled task

Write-Host "Setting up Twitter Manager scheduled task..."

# Get the current directory and paths
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonExe = "python.exe"
$scriptToRun = Join-Path $scriptPath "src\twitter_manager.py"
$logDir = Join-Path $scriptPath "logs"

# Create logs directory if it doesn't exist
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir
    Write-Host "Created logs directory at: $logDir"
}

# Create the scheduled task action
$action = New-ScheduledTaskAction `
    -Execute $pythonExe `
    -Argument "-m src.twitter_manager" `
    -WorkingDirectory $scriptPath

# Create trigger (run every hour)
$trigger = New-ScheduledTaskTrigger `
    -Once `
    -At (Get-Date) `
    -RepetitionInterval (New-TimeSpan -Hours 1)

# Set up task settings
$settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 10) `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1)

# Create the task
$taskName = "TwitterManager"
$description = "Runs Twitter Manager hourly to post updates"

# Remove existing task if it exists
Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue | Unregister-ScheduledTask -Confirm:$false

# Register the new task
Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Description $description

Write-Host "Setup complete! The Twitter Manager will now run every hour."
Write-Host "You can find the task in Task Scheduler under the name 'TwitterManager'"
Write-Host "Logs will be stored in: $logDir"
Write-Host "To test the setup, you can right-click the task in Task Scheduler and select 'Run'"