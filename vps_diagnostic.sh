#!/bin/bash

# =============================================================================
# VPS Static Files Diagnostic Script
# =============================================================================
# Run this script in your epcdata folder on the VPS
# Usage: chmod +x vps_diagnostic.sh && ./vps_diagnostic.sh > diagnostic_results.txt 2>&1

echo "==============================================================================="
echo "VPS STATIC FILES DIAGNOSTIC SCRIPT"
echo "==============================================================================="
echo "Timestamp: $(date)"
echo "Current directory: $(pwd)"
echo "User: $(whoami)"
echo ""

# =============================================================================
# 1. ENVIRONMENT CHECK
# =============================================================================
echo "1. ENVIRONMENT CHECK"
echo "==================="
echo "Python version:"
python3 --version
echo ""

echo "Django installation:"
python3 -c "import django; print(f'Django version: {django.get_version()}')" 2>/dev/null || echo "Django not found or error importing"
echo ""

echo "Current working directory contents:"
ls -la
echo ""

# =============================================================================
# 2. DJANGO PROJECT STRUCTURE
# =============================================================================
echo "2. DJANGO PROJECT STRUCTURE"
echo "============================"
echo "Checking if this is the correct Django project directory:"
if [ -f "manage.py" ]; then
    echo "✓ manage.py found"
else
    echo "✗ manage.py NOT found - are you in the right directory?"
fi

if [ -d "epcdata" ]; then
    echo "✓ epcdata directory found"
else
    echo "✗ epcdata directory NOT found"
fi

if [ -f "epcdata/settings.py" ]; then
    echo "✓ settings.py found"
else
    echo "✗ settings.py NOT found"
fi
echo ""

# =============================================================================
# 3. GIT STATUS
# =============================================================================
echo "3. GIT STATUS"
echo "============="
echo "Git branch:"
git branch --show-current 2>/dev/null || echo "Not in a git repository or git not available"

echo ""
echo "Git status:"
git status --porcelain 2>/dev/null || echo "Git status not available"

echo ""
echo "Latest commit:"
git log -1 --oneline 2>/dev/null || echo "Git log not available"
echo ""

# =============================================================================
# 4. VEHICLE NAVIGATION CSS FILES CHECK
# =============================================================================
echo "4. VEHICLE NAVIGATION CSS FILES CHECK"
echo "======================================"
echo "Checking for vehicle-navigation.css files in various locations:"
echo ""

# Check source files
echo "Source files:"
if [ -f "motortemplate/uren/assets/css/vehicle-navigation.css" ]; then
    echo "✓ motortemplate/uren/assets/css/vehicle-navigation.css EXISTS"
    echo "  File size: $(stat -c%s motortemplate/uren/assets/css/vehicle-navigation.css 2>/dev/null || echo 'unknown') bytes"
    echo "  Modified: $(stat -c%y motortemplate/uren/assets/css/vehicle-navigation.css 2>/dev/null || echo 'unknown')"
else
    echo "✗ motortemplate/uren/assets/css/vehicle-navigation.css MISSING"
fi

if [ -f "motortemplate/assets/css/vehicle-navigation.css" ]; then
    echo "✓ motortemplate/assets/css/vehicle-navigation.css EXISTS"
    echo "  File size: $(stat -c%s motortemplate/assets/css/vehicle-navigation.css 2>/dev/null || echo 'unknown') bytes"
else
    echo "✗ motortemplate/assets/css/vehicle-navigation.css MISSING"
fi

echo ""
echo "Static files:"
if [ -f "staticfiles/css/vehicle-navigation.css" ]; then
    echo "✓ staticfiles/css/vehicle-navigation.css EXISTS"
    echo "  File size: $(stat -c%s staticfiles/css/vehicle-navigation.css 2>/dev/null || echo 'unknown') bytes"
    echo "  Modified: $(stat -c%y staticfiles/css/vehicle-navigation.css 2>/dev/null || echo 'unknown')"
else
    echo "✗ staticfiles/css/vehicle-navigation.css MISSING"
fi

if [ -f "staticfiles/motortemplate/uren/assets/css/vehicle-navigation.css" ]; then
    echo "✓ staticfiles/motortemplate/uren/assets/css/vehicle-navigation.css EXISTS"
    echo "  File size: $(stat -c%s staticfiles/motortemplate/uren/assets/css/vehicle-navigation.css 2>/dev/null || echo 'unknown') bytes"
    echo "  Modified: $(stat -c%y staticfiles/motortemplate/uren/assets/css/vehicle-navigation.css 2>/dev/null || echo 'unknown')"
else
    echo "✗ staticfiles/motortemplate/uren/assets/css/vehicle-navigation.css MISSING"
fi
echo ""

# =============================================================================
# 5. CSS CONTENT ANALYSIS
# =============================================================================
echo "5. CSS CONTENT ANALYSIS"
echo "========================"
echo "Checking for custom-category_col styles in CSS files:"
echo ""

for file in "motortemplate/uren/assets/css/vehicle-navigation.css" "staticfiles/css/vehicle-navigation.css" "staticfiles/motortemplate/uren/assets/css/vehicle-navigation.css"; do
    if [ -f "$file" ]; then
        echo "File: $file"
        echo "Contains custom-category_col:"
        grep -n "custom-category_col" "$file" 2>/dev/null || echo "  No custom-category_col found"
        echo "Contains flex: 0 0 17%:"
        grep -n "flex: 0 0 17%" "$file" 2>/dev/null || echo "  No flex: 0 0 17% found"
        echo "Contains flex: 0 0 25%:"
        grep -n "flex: 0 0 25%" "$file" 2>/dev/null || echo "  No flex: 0 0 25% found"
        echo ""
    fi
done

# =============================================================================
# 6. DJANGO SETTINGS CHECK
# =============================================================================
echo "6. DJANGO SETTINGS CHECK"
echo "========================="
echo "Attempting to read Django settings..."

# Try to get Django settings
python3 -c "
import os
import sys
import django
from django.conf import settings

# Add current directory to Python path
sys.path.insert(0, '.')
sys.path.insert(0, './epcdata')

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')

try:
    django.setup()
    print('✓ Django setup successful')
    print(f'DEBUG = {settings.DEBUG}')
    print(f'STATIC_URL = {settings.STATIC_URL}')
    print(f'STATIC_ROOT = {settings.STATIC_ROOT}')
    print('STATICFILES_DIRS:')
    for i, dir in enumerate(getattr(settings, 'STATICFILES_DIRS', [])):
        print(f'  {i+1}. {dir}')
    if not hasattr(settings, 'STATICFILES_DIRS') or not settings.STATICFILES_DIRS:
        print('  No STATICFILES_DIRS configured')
except Exception as e:
    print(f'✗ Django setup failed: {e}')
" 2>/dev/null || echo "Failed to read Django settings"

echo ""

# =============================================================================
# 7. STATIC FILES DIRECTORY STRUCTURE
# =============================================================================
echo "7. STATIC FILES DIRECTORY STRUCTURE"
echo "===================================="
echo "Staticfiles directory structure:"

if [ -d "staticfiles" ]; then
    echo "staticfiles/ directory contents:"
    find staticfiles -name "*.css" -type f | head -20 | while read file; do
        echo "  $file ($(stat -c%s "$file" 2>/dev/null || echo '?') bytes)"
    done
    
    echo ""
    echo "Total CSS files in staticfiles:"
    find staticfiles -name "*.css" -type f | wc -l
else
    echo "✗ staticfiles directory does not exist"
fi
echo ""

# =============================================================================
# 8. WEB SERVER STATIC FILES TEST
# =============================================================================
echo "8. WEB SERVER STATIC FILES TEST"
echo "================================"
echo "Testing if static files are being served correctly:"

# Test local access to static files
echo "Testing local file access:"
for file in "staticfiles/css/vehicle-navigation.css" "staticfiles/motortemplate/uren/assets/css/vehicle-navigation.css"; do
    if [ -f "$file" ]; then
        echo "✓ $file is accessible locally"
    else
        echo "✗ $file is NOT accessible locally"
    fi
done

echo ""
echo "Testing HTTP access to static files:"
for url in "/static/css/vehicle-navigation.css" "/static/motortemplate/uren/assets/css/vehicle-navigation.css"; do
    echo "Testing: $url"
    response=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost$url" 2>/dev/null || echo "curl_failed")
    if [ "$response" = "200" ]; then
        echo "✓ $url returns HTTP 200"
    elif [ "$response" = "curl_failed" ]; then
        echo "? Cannot test $url (curl failed or server not running on localhost)"
    else
        echo "✗ $url returns HTTP $response"
    fi
done
echo ""

# =============================================================================
# 9. COLLECTSTATIC TEST
# =============================================================================
echo "9. COLLECTSTATIC TEST"
echo "====================="
echo "Testing collectstatic command:"

python3 manage.py collectstatic --dry-run --verbosity=2 2>/dev/null | grep -i "vehicle-navigation" || echo "No vehicle-navigation files found in collectstatic dry-run"
echo ""

# =============================================================================
# 10. PERMISSIONS CHECK
# =============================================================================
echo "10. PERMISSIONS CHECK"
echo "======================"
echo "Checking file and directory permissions:"

for path in "." "staticfiles" "motortemplate" "motortemplate/uren" "motortemplate/uren/assets" "motortemplate/uren/assets/css"; do
    if [ -e "$path" ]; then
        echo "$path: $(stat -c '%A %U:%G' "$path" 2>/dev/null || echo 'permission check failed')"
    fi
done
echo ""

# =============================================================================
# 11. DISK SPACE CHECK
# =============================================================================
echo "11. DISK SPACE CHECK"
echo "===================="
echo "Available disk space:"
df -h . 2>/dev/null || echo "Disk space check failed"
echo ""

# =============================================================================
# 12. PROCESS CHECK
# =============================================================================
echo "12. PROCESS CHECK"
echo "=================="
echo "Web server processes:"
ps aux | grep -E "(nginx|apache|gunicorn|uwsgi)" | grep -v grep || echo "No web server processes found"
echo ""

# =============================================================================
# 13. SUMMARY AND RECOMMENDATIONS
# =============================================================================
echo "13. SUMMARY AND RECOMMENDATIONS"
echo "================================"
echo "Key findings:"

# Check if critical file exists
if [ -f "staticfiles/motortemplate/uren/assets/css/vehicle-navigation.css" ]; then
    echo "✓ Critical CSS file exists in staticfiles"
else
    echo "✗ CRITICAL: vehicle-navigation.css missing from staticfiles/motortemplate/uren/assets/css/"
    echo "  RECOMMENDATION: Copy the file manually:"
    echo "  cp motortemplate/uren/assets/css/vehicle-navigation.css staticfiles/motortemplate/uren/assets/css/"
fi

# Check if source file exists
if [ -f "motortemplate/uren/assets/css/vehicle-navigation.css" ]; then
    echo "✓ Source CSS file exists"
else
    echo "✗ CRITICAL: Source vehicle-navigation.css file is missing"
    echo "  RECOMMENDATION: Run 'git pull origin updatedversion' to get latest files"
fi

echo ""
echo "==============================================================================="
echo "DIAGNOSTIC COMPLETE"
echo "==============================================================================="
echo "Please copy the entire output and provide it for analysis."
echo "Timestamp: $(date)"
