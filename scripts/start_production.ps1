# Run Vytal in production mode: one process serves the built website and the API.
# Build first with scripts\build_release.ps1 (or: cd frontend; npm run build).
# Usage (from the project root):
#   powershell -ExecutionPolicy Bypass -File scripts\start_production.ps1
#   powershell -ExecutionPolicy Bypass -File scripts\start_production.ps1 -Port 8080
# By default it listens on this computer only (127.0.0.1). Do not expose it to the
# internet without HTTPS and a reverse proxy (docs\deployment\DEPLOYMENT.md).

param([string]$BindHost = '127.0.0.1', [int]$Port = 8000)
$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root '.venv\Scripts\python.exe'

if (-not (Test-Path (Join-Path $root 'frontend\dist\index.html'))) {
    Write-Host 'frontend\dist is missing. Run scripts\build_release.ps1 first.' -ForegroundColor Red
    exit 1
}

$env:VYTAL_SERVE_FRONTEND = 'true'
if (-not $env:VYTAL_ENABLE_API_DOCS) { $env:VYTAL_ENABLE_API_DOCS = 'false' }
Write-Host "Vytal: http://${BindHost}:$Port   (readiness: /api/health/ready)"
Push-Location $root
try {
    # One worker: models are loaded into memory once, and the rate limiter is per process.
    & $python -m uvicorn app.main:app --app-dir backend --host $BindHost --port $Port --workers 1 --no-server-header
} finally { Pop-Location }
