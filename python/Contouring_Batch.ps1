<#
This PowerShell script automates the execution of Python scripts for multiple tasks related to processing county and state data.

Script Name: Contouring_Batch.ps1
Created by: Juan Machado - GIS1.net
Date: 1/4/2025

Parameters:
    - $csvFile (string): Path to the input CSV file. The CSV must have columns 'State' and 'County' to define tasks.
	
Example of CSV file:
			ALABAMA.csv contents:
							ALABAMA,Autauga,9749
							ALABAMA,Baldwin,9749
							ALABAMA,Bibb,9749
							ALABAMA,Bullock,9748
							ALABAMA,Butler,9749
							ALABAMA,Calhoun,9748
							ALABAMA,Chambers,9748
							ALABAMA,Cherokee,9748
							ALABAMA,Chilton,9749
							ALABAMA,Choctaw,6507

Syntax Example:
		cd Z:\Clearinghouse_Support\python
		.\Contouring_Batch.ps1 .\ALABAMA.csv
		
Notes:
		The script will open 4 minimized windows doing the contouring process for counties.
		The main dashboard screen will show current processing counties until it finishes.

Operation:
1. The script validates the existence of the input CSV file. If the file does not exist, the script exits with an error message.
2. It initializes logging and sets up a task queue from the input CSV file. Each task is represented by a combination of State, County, and Coordinate Reference System ID.
3. The script spawns new PowerShell processes to execute a Python script (`contouring.py` in this case) for each task, passing the state and county as parameters to the Python script.
4. Tasks are processed concurrently with a limit of 4 active processes at a time.
5. Active and completed tasks are logged in a file named 'Contouring_Batch.log'.
6. The script continually monitors the progress of each task and dynamically starts new tasks when there are available slots for processing.

Logging:
- Log entries include timestamps and task information for both starting and completing tasks.
	Log stored at Contouring_Batch.log
- Any errors or progress are reported to the console in real-time.

Exit Condition:
- The script exits when all tasks are processed or when no tasks are available to process.

#>



param (
    [string]$csvFile
)

# Validate input CSV file and initialize logging
if (-not (Test-Path $csvFile)) {
    Write-Host "Error: File '$csvFile' does not exist. Exiting." -ForegroundColor Red
    exit 1
}

# Read the CSV file
$rows = Import-Csv -Path $csvFile -Header State,County,CRS

# Initialize variables
$logFile = "Contouring_Batch.log"
if (Test-Path $logFile) { Remove-Item $logFile }

$taskQueue = @() # Queue of tasks to process
$processes = New-Object System.Collections.ArrayList # Initialize as ArrayList
$completedTasks = @() # List of completed tasks

# Populate the task queue with initial task data
foreach ($row in $rows) {
    $taskQueue += [PSCustomObject]@{
        State = $row.State
        County = $row.County
        CRS = $row.CRS
        Processed = $false  # Flag for whether the task has been processed
    }
}

# Function to start a new task in a PowerShell window
function Start-NewTask {
    param (
        [string]$state,
        [string]$county,
        [string]$crs
    )

    
    $pythonCommand = "python Z:\Clearinghouse_Support\python\Contouring.py $state $county $crs"
    Write-Host "Starting task: $state $county $crs" -ForegroundColor Green
    Add-Content $logFile "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Starting task: $state $county $crs"

    $process = Start-Process powershell.exe -ArgumentList "-Command", $pythonCommand -PassThru -WindowStyle Minimized
    return $process
}

# Initialize counters for remaining and processed tasks
$remainingTasks = $taskQueue.Count
$processedTasks = 0

# Main loop to manage tasks
while ($remainingTasks -gt 0 -or $processes.Count -gt 0) {
    Clear-Host
    Write-Host "=== Active Tasks ===" -ForegroundColor Yellow
    foreach ($process in $processes) {
        Write-Host "Process ID: $($process.Id) - Task: $($process.StartInfo.Arguments)" -ForegroundColor White
    }

    Write-Host "`n=== Completed Tasks ===" -ForegroundColor Cyan
    foreach ($task in $completedTasks) {
        Write-Host "Task: $($task.State) $($task.County) $($task.CRS)" -ForegroundColor Gray
    }

    # Check for completed processes
    for ($i = 0; $i -lt $processes.Count; $i++) {
        $process = $processes[$i]
        if ($process.HasExited) {
            # Log task completion
            $completedTask = $process.StartInfo.Arguments -replace '.*contouring\.py ', ''
            $state, $county, $crs = $completedTask -split ' '
            $completedTasks += [PSCustomObject]@{ State = $state; County = $county; CRS = $crs;}

            Write-Host "Task completed: $state $county $crs" -ForegroundColor Cyan
            Add-Content $logFile "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Task completed: $state $county $crs"

            # Increment processed task counter and decrement remaining task counter
            $processedTasks++
            $remainingTasks--

            # Remove the completed process from the list
            $processes.RemoveAt($i)
            $i--  # Decrease the index to account for the removed element
        }
    }

    # Start new tasks if there are slots available
    while ($processes.Count -lt 5 -and $remainingTasks -gt 0) {
        $task = $taskQueue | Where-Object { $_.Processed -eq $false } | Select-Object -First 1
        if ($task) {
            Write-Host "Starting new task: $($task.State) $($task.County) $($task.CRS)" -ForegroundColor Magenta
            $process = Start-NewTask -state $task.State -county $task.County -crs $task.CRS
            $processes.Add($process) # Add the process to ArrayList

            # Mark this task as processed
            $task.Processed = $true
        }
        else {
            Write-Host "No more unprocessed tasks available. Exiting." -ForegroundColor Yellow
            break
        }
    }

    # Debugging Log: Check the current task queue and processes
    Write-Host "Remaining tasks in queue: $remainingTasks" -ForegroundColor Yellow
    Write-Host "Active processes count: $($processes.Count)" -ForegroundColor Yellow

    # If no tasks are left and no processes are running, exit the loop
    if ($remainingTasks -eq 0 -and $processes.Count -eq 0) {
        Write-Host "No tasks remaining to process. Exiting loop." -ForegroundColor Yellow
        break
    }

    Start-Sleep -Seconds 60
}

Write-Host "All tasks completed." -ForegroundColor Yellow
Add-Content $logFile "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] All tasks completed."
