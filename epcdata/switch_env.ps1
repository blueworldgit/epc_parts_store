# Environment switcher script for Windows PowerShell

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("local", "production", "status")]
    [string]$Environment
)

function Switch-ToLocal {
    Write-Host "🏠 Switching to LOCAL environment..." -ForegroundColor Green
    if (Test-Path ".prod") {
        Rename-Item ".prod" ".prod.disabled"
        Write-Host "Disabled .prod file" -ForegroundColor Yellow
    }
    if (Test-Path ".env.production") {
        Rename-Item ".env.production" ".env.production.disabled"
        Write-Host "Disabled .env.production file" -ForegroundColor Yellow
    }
    Write-Host "✅ Now using .env for local development" -ForegroundColor Green
    Write-Host "Database will use local credentials from .env file" -ForegroundColor Cyan
}

function Switch-ToProduction {
    Write-Host "🌐 Switching to PRODUCTION environment..." -ForegroundColor Green
    if (Test-Path ".prod.disabled") {
        Rename-Item ".prod.disabled" ".prod"
        Write-Host "Enabled .prod file" -ForegroundColor Yellow
    }
    elseif (Test-Path ".env.production.disabled") {
        Rename-Item ".env.production.disabled" ".env.production"
        Write-Host "Enabled .env.production file" -ForegroundColor Yellow
    }
    elseif (Test-Path ".env.production") {
        Copy-Item ".env.production" ".prod"
        Write-Host "Created .prod from .env.production" -ForegroundColor Yellow
    }
    Write-Host "✅ Now using .prod or .env.production for production" -ForegroundColor Green
    Write-Host "Database will use production credentials" -ForegroundColor Cyan
}

function Show-Status {
    Write-Host "Current environment files:" -ForegroundColor Cyan
    Get-ChildItem -Filter "*.env*" -ErrorAction SilentlyContinue | Select-Object Name
    Get-ChildItem -Filter "*.prod*" -ErrorAction SilentlyContinue | Select-Object Name
    
    Write-Host "`nEnvironment detection logic:" -ForegroundColor Cyan
    if ((Test-Path ".prod") -or (Test-Path ".env.production")) {
        Write-Host "📍 Currently configured for PRODUCTION" -ForegroundColor Red
    }
    elseif (Test-Path ".env") {
        Write-Host "📍 Currently configured for LOCAL" -ForegroundColor Green
    }
    else {
        Write-Host "⚠️ No environment files found" -ForegroundColor Yellow
    }
}

switch ($Environment) {
    "local" { Switch-ToLocal }
    "production" { Switch-ToProduction }
    "status" { Show-Status }
    default { 
        Write-Host "Usage: .\switch_env.ps1 {local|production|status}" -ForegroundColor Yellow
        Write-Host ""
        Show-Status
    }
}
