# Define the URLs and output folder
$textFileUrl = "https://rockyweb.usgs.gov/vdelivery/Datasets/Staged/Elevation/1m/Projects/AL_CoffeeDaleGenevaEscambia_2021_D21/0_file_download_links.txt"
$outputFolder = "W:\ALABAMA\Tif_Files_UTM\AL_CoffeeDaleGenevaEscambia_2021_D21"

# Ensure the output folder exists
if (!(Test-Path -Path $outputFolder)) {
    New-Item -ItemType Directory -Path $outputFolder | Out-Null
}

# Define the local path for the text file
$localTextFile = Join-Path -Path $outputFolder -ChildPath "file_download_links.txt"

# Download the text file
Write-Host "Downloading the text file..."
Invoke-WebRequest -Uri $textFileUrl -OutFile $localTextFile

# Read the text file line by line
$tifUrls = Get-Content -Path $localTextFile

# Iterate through each TIF URL and download the file
foreach ($tifUrl in $tifUrls) {
    # Get the file name from the URL
    $fileName = [System.IO.Path]::GetFileName($tifUrl)
    $outputFilePath = Join-Path -Path $outputFolder -ChildPath $fileName

    # Check if the file already exists
    if (Test-Path -Path $outputFilePath) {
        # Get the local file size
        $localFileSize = (Get-Item -Path $outputFilePath).Length

        # Get the remote file size using a HEAD request
        $remoteFileSize = (Invoke-WebRequest -Uri $tifUrl -Method Head).Headers["Content-Length"]

        # Compare file sizes
        if ($localFileSize -eq $remoteFileSize) {
            Write-Host "Skipping $fileName (already downloaded and matches remote size)."
            continue
        } else {
            Write-Host "File $fileName exists but differs in size. Redownloading..."
        }
    } else {
        Write-Host "File $fileName does not exist. Downloading..."
    }

    # Attempt to download the TIF file with retries
    $downloadSuccessful = $false
    $maxRetries = 10
    $retryCount = 0

    while (-not $downloadSuccessful -and $retryCount -lt $maxRetries) {
        try {
            # Download the TIF file
            Invoke-WebRequest -Uri $tifUrl -OutFile $outputFilePath -ErrorAction Stop
            $downloadSuccessful = $true
            Write-Host "Successfully downloaded $fileName."
        } catch {
            $retryCount++
            Write-Warning "Failed to download $fileName. Retry attempt $retryCount of $maxRetries..."
            Start-Sleep -Seconds 5 # Wait for 5 seconds before retrying
        }
    }

    if (-not $downloadSuccessful) {
        Write-Error "Failed to download $fileName after $maxRetries attempts. Skipping..."
    }
}

Write-Host "Download process completed. All files saved to $outputFolder"
