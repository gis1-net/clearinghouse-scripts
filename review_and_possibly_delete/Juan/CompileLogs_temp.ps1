# === Error Log Summary ===
$summaryLog = "batch_contouring_errors.log"
if (Test-Path $summaryLog) { Remove-Item $summaryLog }
 
Add-Content $summaryLog "Batch Contouring Error Summary - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Add-Content $summaryLog "------------------------------------------------------------"
 
foreach ($task in $taskQueue) {
    $state = $task.State
    $county = $task.County
    $logPath = "Z:\$state\$county\contouring.log"
 
    if (Test-Path $logPath) {
        $lines = Get-Content $logPath
        $errorIndices = @(for ($i = 0; $i -lt $lines.Count; $i++) {
            if ($lines[$i] -match 'ERROR') { $i }
        })
 
        $errorCount = $errorIndices.Count
        Add-Content $summaryLog "`nCounty: $county"
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
        Add-Content $summaryLog "`nCounty: $county"
        Add-Content $summaryLog "Errors found: 0"
        Add-Content $summaryLog "Log file not found: $logPath"
    }
}
 
Write-Host "Error summary written to: $summaryLog" -ForegroundColor Yellow