# UI Shell Build & Dev Script

Write-Host "SERP UI Shell - Build & Development" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

$uiShellPath = Join-Path $PSScriptRoot ".." "ui-shell"

# Check if Node.js is installed
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Node.js is not installed" -ForegroundColor Red
    Write-Host "Please install Node.js 18+ from https://nodejs.org" -ForegroundColor Yellow
    exit 1
}

# Check Node version
$nodeVersion = node --version
Write-Host "Node.js version: $nodeVersion" -ForegroundColor Green

# Navigate to ui-shell
Push-Location $uiShellPath

try {
    Write-Host "`nInstalling dependencies..." -ForegroundColor Yellow
    npm install
    
    Write-Host "`nRunning type check..." -ForegroundColor Yellow
    npm run type-check
    
    Write-Host "`nRunning linter..." -ForegroundColor Yellow
    npm run lint
    
    Write-Host "`nBuild complete!" -ForegroundColor Green
    Write-Host "`nTo start development server:" -ForegroundColor Cyan
    Write-Host "  cd ui-shell" -ForegroundColor White
    Write-Host "  npm run dev" -ForegroundColor White
    Write-Host "`nTo build for production:" -ForegroundColor Cyan
    Write-Host "  cd ui-shell" -ForegroundColor White
    Write-Host "  npm run build" -ForegroundColor White
}
finally {
    Pop-Location
}
