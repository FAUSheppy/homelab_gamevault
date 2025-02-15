param (
    [string]$PathsJson
)

try {
    $Paths = $PathsJson | ConvertFrom-Json -ErrorAction Stop
} catch {
    # If it fails, assume it's Base64-encoded and decode it
    try {
        $DecodedJson = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($PathsJson))
        $Paths = $DecodedJson | ConvertFrom-Json -ErrorAction Stop
    } catch {
        Write-Error "Failed to parse PathsJson as JSON or Base64-encoded JSON."
        exit 1
    }
}

Write-Host "Paths"
Write-Host $PathsJson
Write-Host $PWD

# Check if running as administrator
$CurrentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent()
$Principal = New-Object System.Security.Principal.WindowsPrincipal($CurrentUser)
$IsAdmin = $Principal.IsInRole([System.Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $IsAdmin) {
    # Relaunch the script with elevated privileges
    $EncodedJson = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($PathsJson))
    $TempFile = New-TemporaryFile
    Start-Process powershell -ArgumentList "-ExecutionPolicy Bypass -Command `"Set-Location -Path '$PWD'; & '$PSCommandPath' '$EncodedJson' *> '$TempFile'`" " -Verb RunAs -Wait
    
    Start-Sleep 1
    if (Test-Path $TempFile) {
        # Output the captured output
        Get-Content $TempFile | Write-Host
        Remove-Item $TempFile
    }else{
        Write-Host "No output captured. Check if the script produces any output." 
    }

    exit
}


foreach($Path in $Paths){

    Write-Host "Running: $Path"

    # Run the process and capture output
    try {

        if ($Path -match '\.reg$') {
            # Run regedit silently to merge the .reg file
            $Process = Start-Process -FilePath "regedit.exe" -ArgumentList "/s `"$Path`"" -NoNewWindow -PassThru
        } else {
            # Run the file normally
            $Process = Start-Process -FilePath $Path -NoNewWindow -PassThru
        }
        $Process.WaitForExit()

    } catch {
        Write-Host "Error running the process: $_"
    }
}