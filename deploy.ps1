Set-Location $PSScriptRoot
$ErrorActionPreference = "Stop"

$git = "C:\Program Files\Git\bin\git.exe"
if (-not (Test-Path $git)) {
  $git = "git"
}

Write-Host ""
Write-Host "  Deploy local changes -> michael.trent.dev (live site)" -ForegroundColor Cyan
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

Write-Host "Pushing to live site repo..." -ForegroundColor Green
& $git push live master:main
Write-Host ""
Write-Host "Done. Vercel will redeploy in ~1-2 minutes." -ForegroundColor Green
Write-Host "Live site: https://michaeltrentdev.vercel.app" -ForegroundColor Cyan
Write-Host ""
