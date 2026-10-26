# Build and check a release: install exact frontend packages, run every automated
# check, and build the frontend into frontend\dist for production mode.
# Usage (from the project root):  powershell -ExecutionPolicy Bypass -File scripts\build_release.ps1
# Add -SkipBrowserTests to skip the Playwright tests (they need Microsoft Edge).

param([switch]$SkipBrowserTests)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root '.venv\Scripts\python.exe'

function Step($name, [scriptblock]$action) {
    Write-Host "`n== $name" -ForegroundColor Cyan
    & $action
    if ($LASTEXITCODE -ne 0) { Write-Host "FAILED: $name" -ForegroundColor Red; exit 1 }
}

Push-Location $root
try {
    Step 'Python tests' { & $python -m pytest -q }
    Push-Location frontend
    try {
        Step 'Install exact frontend packages (npm ci)' { npm ci }
        Step 'Lint' { npm run lint }
        Step 'Frontend unit tests' { npm test }
        Step 'Production build' { npm run build }
        if (-not $SkipBrowserTests) { Step 'Browser tests (Edge)' { npm run test:e2e } }
    } finally { Pop-Location }
    Write-Host "`nRelease build ready in frontend\dist. Start it with scripts\start_production.ps1" -ForegroundColor Green
} finally { Pop-Location }
