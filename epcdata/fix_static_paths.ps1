# PowerShell script to fix static file references in templates
# Remove 'motortemplate/' prefix from static file references

$templateDir = "C:\pythonstuff\vansdirect\epc_parts_store\epcdata\templates"

# Find all HTML files in the templates directory
$htmlFiles = Get-ChildItem -Path $templateDir -Filter "*.html" -Recurse

Write-Host "Found $($htmlFiles.Count) HTML files to process..."

foreach ($file in $htmlFiles) {
    Write-Host "Processing: $($file.FullName)"
    
    # Read the file content
    $content = Get-Content -Path $file.FullName -Raw
    
    # Replace all instances of 'motortemplate/uren/' with 'uren/'
    $newContent = $content -replace "motortemplate/uren/", "uren/"
    
    # Only write back if content changed
    if ($content -ne $newContent) {
        Set-Content -Path $file.FullName -Value $newContent -NoNewline
        Write-Host "  ✅ Updated: $($file.Name)"
    } else {
        Write-Host "  ⏭️ No changes needed: $($file.Name)"
    }
}

Write-Host "✅ All template files have been processed!"
Write-Host "Static file references updated from 'motortemplate/uren/' to 'uren/'"
