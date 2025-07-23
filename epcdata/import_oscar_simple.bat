@echo off
REM Simple batch script for Oscar import
REM Usage: import_oscar_simple.bat <parts_folder> <pricing_folder>

if "%~2"=="" (
    echo Usage: %0 ^<parts_folder^> ^<pricing_folder^>
    echo Example: %0 "C:\data\parts" "C:\data\pricing"
    exit /b 1
)

set PARTS_FOLDER=%~1
set PRICING_FOLDER=%~2
set PROJECT_ROOT=C:\pythonstuff\parts_store\epcstore\epcdata

echo === EPC Motor Parts - Oscar Import ===
echo Parts Folder: %PARTS_FOLDER%
echo Pricing Folder: %PRICING_FOLDER%
echo.

REM Check if folders exist
if not exist "%PARTS_FOLDER%" (
    echo ERROR: Parts folder not found: %PARTS_FOLDER%
    exit /b 1
)

if not exist "%PRICING_FOLDER%" (
    echo ERROR: Pricing folder not found: %PRICING_FOLDER%
    exit /b 1
)

REM Change to project directory
cd /d "%PROJECT_ROOT%"

REM Activate virtual environment
call "C:\pythonstuff\parts_store\env\Scripts\activate.bat"

REM Step 1: Import Parts
echo --- Importing Parts ---
python scrapeandpush.py "%PARTS_FOLDER%"
if %errorlevel% neq 0 (
    echo ERROR: Parts import failed
    exit /b %errorlevel%
)

REM Step 2: Import Pricing
echo --- Importing Pricing ---
python loadprices.py "%PRICING_FOLDER%"
if %errorlevel% neq 0 (
    echo ERROR: Pricing import failed
    exit /b %errorlevel%
)

REM Step 3: Import to Oscar
echo --- Importing to Oscar ---
python import_to_oscar.py
if %errorlevel% neq 0 (
    echo ERROR: Oscar import failed
    exit /b %errorlevel%
)

echo.
echo === Import Complete ===
echo Your Oscar shop is now populated with products and categories!
