# Juan Machado - 2/5/25
# Define source and destination drives
$sourceDrive = "z:\ALABAMA"
$destinationDrive = "w:\ALABAMA"

# Define folders to exclude
$excludeFolders = @("Shapefiles", "DWG_files")

# Construct the Robocopy command with exclusions
$robocopyCommand = "robocopy `"$sourceDrive`" `"$destinationDrive`" /E /COPY:DAT /DCOPY:DAT /PURGE /it /im /MT:16"

# Append exclusion parameters
foreach ($folder in $excludeFolders) {
    $robocopyCommand += " /XD `"$folder`""
}

# Execute the Robocopy command
Write-Output "Executing: $robocopyCommand"
Invoke-Expression $robocopyCommand
