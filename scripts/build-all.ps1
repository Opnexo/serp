# Build all packages in the workspace
# PowerShell version of build-all.sh

$ErrorActionPreference = "Stop"

Write-Host "Building SERP workspace packages..." -ForegroundColor Cyan

# Build core packages first (order matters due to dependencies)
Write-Host "Building serp-core..." -ForegroundColor Yellow
Set-Location packages/serp-core
uv build
Set-Location ../..

Write-Host "Building serp-shell..." -ForegroundColor Yellow
Set-Location packages/serp-shell
uv build
Set-Location ../..

Write-Host "Building serp-cli..." -ForegroundColor Yellow
Set-Location packages/serp-cli
uv build
Set-Location ../..

# Build official modules
Write-Host "Building serp-users..." -ForegroundColor Yellow
Set-Location modules/serp-users
uv build
Set-Location ../..

Write-Host "Building serp-crm..." -ForegroundColor Yellow
Set-Location modules/serp-crm
uv build
Set-Location ../..

Write-Host "Building serp-invoicing..." -ForegroundColor Yellow
Set-Location modules/serp-invoicing
uv build
Set-Location ../..

Write-Host "✓ All packages built successfully!" -ForegroundColor Green
Write-Host "Build artifacts are in each package's dist/ directory"
