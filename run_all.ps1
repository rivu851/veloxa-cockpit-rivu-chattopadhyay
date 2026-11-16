# Veloxa CXO Cockpit — Single-Command Local Launch Script
# Author: Rivu Chattopadhyay
# Prerequisite: Python 3.10+ and Node.js 18+

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "       VELOXA CXO COCKPIT — LAUNCHING SERVICES           " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$RepoRoot = $PSScriptRoot

# 0. Environment File Initialization
if (-not (Test-Path "$RepoRoot\.env") -and (Test-Path "$RepoRoot\.env.example")) {
    Write-Host "Initializing .env from .env.example..." -ForegroundColor Yellow
    Copy-Item "$RepoRoot\.env.example" "$RepoRoot\.env"
}

# 1. Setup Backend
Write-Host "`n[1/3] Preparing Python Backend..." -ForegroundColor Yellow
Set-Location "$RepoRoot"
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
}

Write-Host "Installing backend dependencies..."
& "$RepoRoot\.venv\Scripts\pip.exe" install -r "$RepoRoot\backend\requirements.txt" --quiet

# 2. Run Backend Pytest Suite
Write-Host "`n[2/3] Running Automated Test Suite..." -ForegroundColor Yellow
& "$RepoRoot\.venv\Scripts\python.exe" -m pytest "$RepoRoot\backend\tests" -v
if ($LASTEXITCODE -ne 0) {
    Write-Host "Pytest suite encountered failures! Aborting launch." -ForegroundColor Red
    exit 1
}

# 3. Setup Frontend
Write-Host "`n[3/3] Preparing Frontend..." -ForegroundColor Yellow
Set-Location "$RepoRoot\frontend"
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing frontend npm dependencies..."
    npm install
}

Write-Host "`n==========================================================" -ForegroundColor Green
Write-Host "All verification checks passed!" -ForegroundColor Green
Write-Host "Starting FastAPI Backend on http://localhost:8000" -ForegroundColor Green
Write-Host "Starting Next.js Frontend on http://localhost:3000" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green

# Launch backend in separate window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$RepoRoot'; .venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload"

# Launch frontend in current window
npm run dev
