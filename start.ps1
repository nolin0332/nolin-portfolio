Set-Location $PSScriptRoot
$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "  Portfolio - http://127.0.0.1:5136" -ForegroundColor Cyan
Write-Host ""

if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
  Write-Host "ERROR: Node.js is not installed. Get it from https://nodejs.org/" -ForegroundColor Red
  Read-Host "Press Enter to exit"
  exit 1
}

if (-not (Test-Path "node_modules\vite")) {
  Write-Host "Installing dependencies..."
  npm install
}

Write-Host "Starting server... (Ctrl+C to stop)" -ForegroundColor Green
npm run dev
