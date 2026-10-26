# Start the backend and the frontend dev server in two new PowerShell windows.
# Usage (from the project root):  powershell -ExecutionPolicy Bypass -File scripts\start_dev.ps1
# Close the two windows (or press Ctrl+C in them) to stop.

$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root '.venv\Scripts\python.exe'
if (-not (Test-Path $python)) {
    Write-Host 'The Python environment is missing. See README.md "Setup".' -ForegroundColor Red
    exit 1
}
if (-not (Test-Path (Join-Path $root 'frontend\node_modules'))) {
    Write-Host 'Frontend packages are missing. Run: cd frontend; npm install' -ForegroundColor Red
    exit 1
}

Start-Process powershell -WorkingDirectory $root -ArgumentList '-NoExit', '-Command',
    "& '$python' -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload"
Start-Process powershell -WorkingDirectory (Join-Path $root 'frontend') -ArgumentList '-NoExit', '-Command', 'npm run dev'

Write-Host 'Backend:  http://127.0.0.1:8000  (API docs at /docs)'
Write-Host 'Frontend: http://localhost:5173  (open this one)'
