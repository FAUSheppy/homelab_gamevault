# Check if Python is installed
$pythonInstalled = Get-Command python -ErrorAction SilentlyContinue

if (-not $pythonInstalled) {
    Write-Host "Python is not installed. Please install Python before running this script." -ForegroundColor Red
    pause
    exit 1
}

# install dependencies
Start-Process python -ArgumentList "-m", "pip", "install", "-r", $requirementsFilePath -Wait

# Get the directory of the script
$scriptDirectory = Split-Path -Parent $MyInvocation.MyCommand.Path

# Check if client.exe exists in the script directory
$clientExePath = Join-Path -Path $scriptDirectory -ChildPath "client.exe"

if (-not (Test-Path $clientExePath)) {
    Write-Host "client.exe not found in the script directory." -ForegroundColor Red
    pause
    exit 1
}

# Execute client.exe
Start-Process $clientExePath