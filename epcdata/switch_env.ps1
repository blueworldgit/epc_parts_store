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
    Get-ChildItem -Filter "*.env*" -ErrorAction SilentlyContinue | ForEach-Object { Write-Host "  $($_.Name)" }
    Get-ChildItem -Filter "*.prod*" -ErrorAction SilentlyContinue | ForEach-Object { Write-Host "  $($_.Name)" }
    
    Write-Host "`nEnvironment detection logic (matches Django settings.py):" -ForegroundColor Cyan
    if (Test-Path ".prod") {
        Write-Host "📍 Currently configured for PRODUCTION (.prod file exists)" -ForegroundColor Red
    }
    elseif ((Test-Path ".env.production") -and (-not (Test-Path ".env.production.disabled"))) {
        Write-Host "📍 Currently configured for PRODUCTION (.env.production active)" -ForegroundColor Red
    }
    elseif (Test-Path ".env") {
        Write-Host "📍 Currently configured for LOCAL (.env file active)" -ForegroundColor Green
    }
    else {
        Write-Host "⚠️ No environment files found" -ForegroundColor Yellow
    }
    
    # Show which database would be used
    Write-Host "`nDatabase that will be used:" -ForegroundColor Cyan
    if (Test-Path ".prod") {
        $prodContent = Get-Content ".prod" | Where-Object { $_ -match "^DB_NAME=" }
        Write-Host "  From .prod: $prodContent" -ForegroundColor Red
    }
    elseif ((Test-Path ".env.production") -and (-not (Test-Path ".env.production.disabled"))) {
        $prodContent = Get-Content ".env.production" | Where-Object { $_ -match "^DB_NAME=" }
        Write-Host "  From .env.production: $prodContent" -ForegroundColor Red
    }
    elseif (Test-Path ".env") {
        $localContent = Get-Content ".env" | Where-Object { $_ -match "^DB_NAME=" }
        Write-Host "  From .env: $localContent" -ForegroundColor Green
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
