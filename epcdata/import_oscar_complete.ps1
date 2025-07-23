# import_oscar_complete.ps1
# Complete import process: Parts -> Pricing -> Oscar
# Usage: .\import_oscar_complete.ps1 <parts_folder> <pricing_folder> [options]
# Example: .\import_oscar_complete.ps1 "C:\data\parts" "C:\data\pricing" -Serial "LSH14C4C5NA129710" -DryRun

param (
    [Parameter(Mandatory=$true)]
    [string]$PartsFolder,
    
    [Parameter(Mandatory=$true)]
    [string]$PricingFolder,
    
    [string]$Serial,
    [switch]$DryRun,
    [switch]$Verbose,
    [switch]$SkipParts,
    [switch]$SkipPricing,
    [switch]$SkipOscar
)

$ErrorActionPreference = "Stop"
$projectRoot = "C:\pythonstuff\parts_store\epcstore\epcdata"

Write-Host "=== EPC Motor Parts - Complete Oscar Import ===" -ForegroundColor Green
Write-Host "Parts Folder: $PartsFolder"
Write-Host "Pricing Folder: $PricingFolder"
if ($Serial) { Write-Host "Serial Filter: $Serial" }
if ($DryRun) { Write-Host "Mode: DRY RUN (no changes will be made)" -ForegroundColor Yellow }
Write-Host ""

# Function to check if folder exists
function Test-FolderExists {
    param([string]$Path, [string]$Description)
    
    if (-not (Test-Path $Path)) {
        Write-Host "ERROR: $Description folder not found: $Path" -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ Found $Description folder: $Path" -ForegroundColor Green
}

# Function to activate virtual environment
function Invoke-VirtualEnv {
    $envPath = "C:\pythonstuff\parts_store\env\Scripts\Activate.ps1"
    if (Test-Path $envPath) {
        Write-Host "✓ Activating virtual environment..." -ForegroundColor Green
        & $envPath
    } else {
        Write-Host "ERROR: Virtual environment not found at $envPath" -ForegroundColor Red
        exit 1
    }
}

# Function to run Python script with error handling
function Invoke-PythonScript {
    param(
        [string]$ScriptPath,
        [string]$Arguments,
        [string]$Description
    )
    
    Write-Host "--- $Description ---" -ForegroundColor Blue
    Write-Host "Running: python $ScriptPath $Arguments"
    
    if ($DryRun -and $Description -eq "Oscar Import") {
        $Arguments += " --dry-run"
    }
    
    if ($Verbose) {
        $Arguments += " --verbose"
    }
    
    try {
        if ($Arguments) {
            $process = Start-Process -FilePath "python" -ArgumentList "$ScriptPath $Arguments" -Wait -PassThru -NoNewWindow
        } else {
            $process = Start-Process -FilePath "python" -ArgumentList $ScriptPath -Wait -PassThru -NoNewWindow
        }
        
        if ($process.ExitCode -eq 0) {
            Write-Host "✓ $Description completed successfully" -ForegroundColor Green
        } else {
            Write-Host "✗ $Description failed with exit code: $($process.ExitCode)" -ForegroundColor Red
            exit $process.ExitCode
        }
    } catch {
        Write-Host "✗ $Description failed: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
    Write-Host ""
}

# Main execution
try {
    # Validate inputs
    Test-FolderExists $PartsFolder "Parts"
    Test-FolderExists $PricingFolder "Pricing"
    
    # Change to project directory
    Set-Location $projectRoot
    
    # Activate virtual environment
    Invoke-VirtualEnv
    
    # Step 1: Import Parts and Categories
    if (-not $SkipParts) {
        $partsArgs = "`"$PartsFolder`""
        Invoke-PythonScript "scrapeandpush.py" $partsArgs "Parts Import"
    } else {
        Write-Host "--- Skipping Parts Import ---" -ForegroundColor Yellow
    }
    
    # Step 2: Import Pricing Data
    if (-not $SkipPricing) {
        $pricingArgs = "`"$PricingFolder`""
        Invoke-PythonScript "loadprices.py" $pricingArgs "Pricing Import"
    } else {
        Write-Host "--- Skipping Pricing Import ---" -ForegroundColor Yellow
    }
    
    # Step 3: Import to Oscar
    if (-not $SkipOscar) {
        $oscarArgs = ""
        if ($Serial) {
            $oscarArgs = "--serial `"$Serial`""
        }
        Invoke-PythonScript "import_to_oscar.py" $oscarArgs "Oscar Import"
    } else {
        Write-Host "--- Skipping Oscar Import ---" -ForegroundColor Yellow
    }
    
    Write-Host "=== Import Process Complete ===" -ForegroundColor Green
    
    if (-not $DryRun) {
        Write-Host ""
        Write-Host "Your Oscar shop is now populated with:"
        Write-Host "• Categories based on Serial -> Parent -> Child hierarchy"
        Write-Host "• Products with part numbers, descriptions, and attributes"
        Write-Host "• Stock records with pricing and inventory"
        Write-Host "• SVG diagrams stored as product attributes"
        Write-Host ""
        Write-Host "You can now access your Oscar dashboard to manage the products."
    } else {
        Write-Host ""
        Write-Host "DRY RUN completed. Review the logs to see what would be imported."
    }

} catch {
    Write-Host "FATAL ERROR: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
