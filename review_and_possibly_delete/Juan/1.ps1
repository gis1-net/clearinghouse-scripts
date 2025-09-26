param (
    [string]$csvFile
)
 
# Validate input CSV file and initialize logging
if (-not (Test-Path $csvFile)) {
    Write-Host "Error: File '$csvFile' does not exist. Exiting." -ForegroundColor Red
    exit 1
}
 
# Set the path to Python executable and working directory
$pythonPath = "python.exe"
$pythonDir = "C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3"
 
# Read the CSV file (State,County,Unit)
$rows = Import-Csv -Path $csvFile -Header State,County,Unit
 
# Initialize variables
$logFile = "Process_Contouring_Batch.log"
if (Test-Path $logFile) { Remove-Item $logFile }
 
$taskQueue = @() # Queue of tasks to process
$processes = New-Object System.Collections.ArrayList
$completedTasks = @()
 
# Populate the task queue
foreach ($row in $rows) {
    $taskQueue += [PSCustomObject]@{
        State     = $row.State
        County    = $row.County
        Unit      = $row.Unit
        Processed = $false
    }
}
 
# Function to start a new task
function Start-NewTask {
    param (
        [string]$state,
        [string]$county,
        [string]$unit
    )
 
    $pythonCommand = "cd '$pythonDir'; .\python.exe -c `"print('hello world')`""
    Write-Host "Starting task: $state $county $unit" -ForegroundColor Green
    Add-Content $logFile "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Starting task: $state $county $unit"
 
    $process = Start-Process powershell.exe -ArgumentList "-Command", $pythonCommand -PassThru -WindowStyle Minimized
 
    # Attach metadata to process
    $process | Add-Member -MemberType NoteProperty -Name State -Value $state
    $process | Add-Member -MemberType NoteProperty -Name County -Value $county
    $process | Add-Member -MemberType NoteProperty -Name Unit -Value $unit
 
    return $process
}
 
# Initialize counters
$remainingTasks = $taskQueue.Count
$processedTasks = 0
 
# Main loop to manage tasks
while ($remainingTasks -gt 0 -or $processes.Count -gt 0) {
    Clear-Host
    Write-Host "=== Active Tasks ===" -ForegroundColor Yellow
    foreach ($process in $processes) {
        Write-Host "Process ID: $($process.Id) - Task: $($process.State) $($process.County) $($process.Unit)" -ForegroundColor White
    }
 
    Write-Host "`n=== Completed Tasks ===" -ForegroundColor Cyan
    foreach ($task in $completedTasks) {
        Write-Host "Task: $($task.State) $($task.County) $($task.Unit)" -ForegroundColor Gray
    }
 
    # Check for completed processes
    for ($i = 0; $i -lt $processes.Count; $i++) {
        $process = $processes[$i]
        if ($process.HasExited) {
            $completedTasks += [PSCustomObject]@{
                State  = $process.State
                County = $process.County
                Unit   = $process.Unit
            }
 
            Write-Host "Task completed: $($process.State) $($process.County)" -ForegroundColor Cyan
            Add-Content $logFile "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Task completed: $($process.State) $($process.County)"
 
            $processedTasks++
            $remainingTasks--
 
            $processes.RemoveAt($i)
            $i--
        }
    }
 
    # Launch new tasks if slots are available
    while ($processes.Count -lt 25 -and $remainingTasks -gt 0) {
        $task = $taskQueue | Where-Object { $_.Processed -eq $false } | Select-Object -First 1
        if ($task) {
            Write-Host "Launching: $($task.State) $($task.County) $($task.Unit)" -ForegroundColor Magenta
            $process = Start-NewTask -state $task.State -county $task.County -unit $task.Unit
            $processes.Add($process)
            $task.Processed = $true
        }
        else {
            Write-Host "No more unprocessed tasks available." -ForegroundColor Yellow
            break
        }
    }
 
    Write-Host "Remaining tasks: $remainingTasks" -ForegroundColor Yellow
    Write-Host "Active processes: $($processes.Count)" -ForegroundColor Yellow
 
    if ($remainingTasks -eq 0 -and $processes.Count -eq 0) {
        Write-Host "No tasks remaining to process. Exiting loop." -ForegroundColor Yellow
        break
    }
 
    #Start-Sleep -Seconds 60
}
 
Write-Host "All tasks completed." -ForegroundColor Yellow
Add-Content $logFile "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] All tasks completed."
 
 
# === Error Log Summary ===
$summaryLog = "batch_contouring_errors.log"
if (Test-Path $summaryLog) { Remove-Item $summaryLog }
 
Add-Content $summaryLog "Batch Contouring Error Summary - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Add-Content $summaryLog "------------------------------------------------------------"
 
foreach ($task in $taskQueue) {
    $state = $task.State
    $county = $task.County
	$logPath = "Z:\$state\${county}_contours\contouring.log"
 
    Add-Content $summaryLog "`nCounty: $county"
 
    if (Test-Path $logPath) {
        $lines = Get-Content $logPath
        $errorIndices = @(for ($i = 0; $i -lt $lines.Count; $i++) {
            if ($lines[$i] -match '(?i)error') { $i }
        })
 
        $errorCount = $errorIndices.Count
        Add-Content $summaryLog "Errors found: $errorCount"
 
        if ($errorCount -gt 0) {
            Add-Content $summaryLog "Suspect lines:"
            foreach ($index in $errorIndices) {
                $start = [Math]::Max(0, $index - 3)
                $end = [Math]::Min($lines.Count - 1, $index + 3)
                for ($j = $start; $j -le $end; $j++) {
                    Add-Content $summaryLog ("    " + $lines[$j])
                }
                Add-Content $summaryLog "----"
            }
        }
    }
    else {
        Add-Content $summaryLog "Errors found: 0"
        Add-Content $summaryLog "Log file not found: $logPath"
    }
}
 
Write-Host "Error summary written to: $summaryLog" -ForegroundColor Yellow