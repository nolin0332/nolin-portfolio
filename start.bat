@echo off
cd /d "%~dp0"
title Portfolio - http://127.0.0.1:5136

echo.
echo  Timothy Calder Portfolio
echo  ========================
echo.

where node >nul 2>&1
if errorlevel 1 (
  echo ERROR: Node.js is not installed.
  echo Install from https://nodejs.org/ then run this file again.
  pause
  exit /b 1
)

if not exist "node_modules\vite" (
  echo Installing dependencies...
  call npm install
  if errorlevel 1 (
    echo ERROR: npm install failed.
    pause
    exit /b 1
  )
)

echo Starting server at http://127.0.0.1:5136/
echo Press Ctrl+C to stop.
echo.

call npm run dev

if errorlevel 1 (
  echo.
  echo If port 5136 is busy, close other terminals or run:
  echo   netstat -ano ^| findstr :5136
  echo   taskkill /PID ^<pid^> /F
  pause
)
