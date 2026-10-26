# Checks that the tools Vytal needs are installed with suitable versions.
# Usage (from the project root):  powershell -ExecutionPolicy Bypass -File scripts\check_environment.ps1

$ErrorActionPreference = 'Continue'
$allOk = $true

function Test-Tool {
    param([string]$Name, [scriptblock]$GetVersion, [version]$Minimum)
    try {
        $raw = (& $GetVersion) 2>&1 | Select-Object -First 1
        $match = [regex]::Match("$raw", '\d+\.\d+(\.\d+)?')
        if (-not $match.Success) { throw "no version found in '$raw'" }
        $found = [version]$match.Value
        if ($Minimum -and $found -lt $Minimum) {
            Write-Host ("[FAIL] {0} {1} (need {2} or newer)" -f $Name, $found, $Minimum) -ForegroundColor Red
            return $false
        }
        Write-Host ("[ OK ] {0} {1}" -f $Name, $found) -ForegroundColor Green
        return $true
    } catch {
        Write-Host ("[FAIL] {0} not found ({1})" -f $Name, $_) -ForegroundColor Red
        return $false
    }
}

$allOk = (Test-Tool 'Python' { python --version } ([version]'3.10')) -and $allOk
$allOk = (Test-Tool 'Node.js' { node --version } ([version]'20.19')) -and $allOk
$allOk = (Test-Tool 'npm' { npm --version } $null) -and $allOk
$allOk = (Test-Tool 'Git' { git --version } $null) -and $allOk

if (Test-Path '.venv\Scripts\python.exe') {
    Write-Host '[ OK ] Project virtual environment found (.venv)' -ForegroundColor Green
} else {
    Write-Host '[INFO] .venv not found. Create it with: python -m venv .venv' -ForegroundColor Yellow
}

$gitName = git config user.name
$gitEmail = git config user.email
if ($gitName -and $gitEmail) {
    Write-Host "[ OK ] Git identity: $gitName <$gitEmail>" -ForegroundColor Green
} else {
    Write-Host '[WARN] Git user.name / user.email are not set; commits will fail.' -ForegroundColor Yellow
}

if ($allOk) { exit 0 } else { exit 1 }
