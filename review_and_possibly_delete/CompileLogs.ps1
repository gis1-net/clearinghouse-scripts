# After all tasks are completed, compile all contouring logs
Write-Host "Compiling contouring logs..." -ForegroundColor Yellow
$compiledLogFile = "CompiledContouringLogs.log"
if (Test-Path $compiledLogFile) { Remove-Item $compiledLogFile }
 
$finalErrorCount = 0  # Total ERROR count across all counties
 
# Get list of states (directories) in Z:\
$states = Get-ChildItem -Path "Z:\" -Directory | Select-Object -ExpandProperty Name
 
foreach ($state in $states) {
    $countyFolders = Get-ChildItem -Path "Z:\$state" -Directory -Filter "*_County_Contours"
    foreach ($countyFolder in $countyFolders) {
        $logFilePath = "$($countyFolder.FullName)\contouring.log"
        if (Test-Path $logFilePath) {
            $logContent = Get-Content $logFilePath
            $errorCount = ($logContent | Select-String -Pattern "ERROR" -CaseSensitive:$false).Count
            $finalErrorCount += $errorCount
            # Append county log content to compiled log
            Add-Content $compiledLogFile "--- $state / $($countyFolder.Name) ---"
            Add-Content $compiledLogFile $logContent
            Add-Content $compiledLogFile "ERROR occurrences: $errorCount"
            Add-Content $compiledLogFile ""
        }
    }
}
 
# Append final error count
Add-Content $compiledLogFile "Total ERROR occurrences across all counties: $finalErrorCount"
Write-Host "Compilation complete. Total ERROR occurrences: $finalErrorCount" -ForegroundColor Green