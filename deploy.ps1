Set-Location $PSScriptRoot
$ErrorActionPreference = "Stop"

$git = "C:\Program Files\Git\bin\git.exe"
if (-not (Test-Path $git)) {
  $git = "git"
}

Write-Host ""
Write-Host "  Deploy local changes -> github.com/nolin0332/nolin-portfolio" -ForegroundColor Cyan
Write-Host ""

$status = & $git status --porcelain
if ($status) {
  Write-Host "Committing local changes..." -ForegroundColor Yellow
  & $git add -A
  if (-not $args[0]) {
    $msg = Read-Host "Commit message"
    if (-not $msg) { $msg = "Update portfolio" }
  } else {
    $msg = ($args -join " ")
  }
  & $git commit -m $msg
} else {
  Write-Host "No local changes to commit." -ForegroundColor Gray
}

Write-Host "Pushing to origin/master..." -ForegroundColor Green
& $git push origin master
Write-Host ""
Write-Host "Done. If the repo is connected to Vercel it redeploys in ~1-2 minutes." -ForegroundColor Green
Write-Host ""
