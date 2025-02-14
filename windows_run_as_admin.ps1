param (
    [string]$Path
)

# Check if running as administrator
$CurrentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent()
$Principal = New-Object System.Security.Principal.WindowsPrincipal($CurrentUser)
$IsAdmin = $Principal.IsInRole([System.Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $IsAdmin) {
    # Relaunch the script with elevated privileges
    Start-Process powershell -ArgumentList "-File `"$PSCommandPath`" `"$Path`"" -Verb RunAs
    exit
}

# Run the process and capture output
try {
    $Process = Start-Process -FilePath $Path -NoNewWindow -PassThru -RedirectStandardOutput output.txt -RedirectStandardError error.txt
    $Process.WaitForExit()

    # Read and display output
    Get-Content output.txt
    Get-Content error.txt | ForEach-Object { Write-Host $_ -ForegroundColor Red }

} catch {
    Write-Host "Error running the process: $_" -ForegroundColor Red
}