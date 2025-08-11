#!/bin/bash

# =============================================================================
# VPS Django Static Files Diagnostic Script
# Created for debugging vehicle-navigation.css deployment issues
# =============================================================================

echo "=========================================="
echo "VPS DJANGO STATIC FILES DIAGNOSTIC SCRIPT"
echo "=========================================="
echo "Timestamp: $(date)"
echo "User: $(whoami)"
echo "Current Directory: $(pwd)"
echo ""

# =============================================================================
# SECTION 1: BASIC SYSTEM INFO
# =============================================================================
echo "=== SECTION 1: SYSTEM INFORMATION ==="
echo "Operating System: $(uname -a)"
echo "Python Version: $(python3 --version 2>/dev/null || echo 'Python3 not found')"
echo "Disk Space:"
df -h | head -5
echo ""

# =============================================================================
# SECTION 2: PROJECT STRUCTURE
# =============================================================================
echo "=== SECTION 2: PROJECT STRUCTURE ==="
echo "Current directory contents:"
ls -la
echo ""

echo "Checking if we're in the right directory..."
if [ -f "manage.py" ]; then
    echo "✅ Found manage.py - we're in the Django project root"
else
    echo "❌ manage.py not found - checking parent directories..."
    if [ -f "../manage.py" ]; then
        echo "Found manage.py in parent directory"
        cd ..
        echo "Changed to: $(pwd)"
    else
        echo "❌ Cannot find manage.py - this script should be run from the epcdata directory"
    fi
fi
echo ""

# =============================================================================
# SECTION 3: GIT STATUS
# =============================================================================
echo "=== SECTION 3: GIT STATUS ==="
echo "Current branch:"
git branch --show-current 2>/dev/null || echo "Not a git repository or git not available"
echo ""

echo "Git status:"
git status --porcelain 2>/dev/null || echo "Git status not available"
echo ""

echo "Last 3 commits:"
git log --oneline -3 2>/dev/null || echo "Git log not available"
echo ""

# =============================================================================
# SECTION 4: DJANGO SETTINGS
# =============================================================================
echo "=== SECTION 4: DJANGO CONFIGURATION ==="
echo "Checking Django settings..."

# Try to get Django settings without running into Unicode issues
echo "STATIC_URL:"
python3 -c "
import os, sys
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
try:
    from django.conf import settings
    print(settings.STATIC_URL)
except Exception as e:
    print(f'Error: {e}')
" 2>/dev/null || echo "Could not retrieve STATIC_URL"

echo ""

echo "STATIC_ROOT:"
python3 -c "
import os, sys
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
try:
    from django.conf import settings
    print(settings.STATIC_ROOT)
except Exception as e:
    print(f'Error: {e}')
" 2>/dev/null || echo "Could not retrieve STATIC_ROOT"

echo ""

echo "STATICFILES_DIRS:"
python3 -c "
import os, sys
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
try:
    from django.conf import settings
    print(settings.STATICFILES_DIRS)
except Exception as e:
    print(f'Error: {e}')
" 2>/dev/null || echo "Could not retrieve STATICFILES_DIRS"

echo ""

# =============================================================================
# SECTION 5: VEHICLE-NAVIGATION.CSS FILE LOCATIONS
# =============================================================================
echo "=== SECTION 5: VEHICLE-NAVIGATION.CSS FILE LOCATIONS ==="

echo "Searching for all vehicle-navigation.css files..."
find . -name "vehicle-navigation.css" -type f 2>/dev/null | while read file; do
    echo "Found: $file"
    echo "  Size: $(ls -lh "$file" | awk '{print $5}')"
    echo "  Modified: $(ls -l "$file" | awk '{print $6, $7, $8}')"
    echo "  First 5 lines:"
    head -5 "$file" | sed 's/^/    /'
    echo ""
done

# =============================================================================
# SECTION 6: STATIC FILES DIRECTORY STRUCTURE
# =============================================================================
echo "=== SECTION 6: STATIC FILES DIRECTORY STRUCTURE ==="

if [ -d "staticfiles" ]; then
    echo "✅ staticfiles directory exists"
    echo "staticfiles directory size: $(du -sh staticfiles 2>/dev/null | cut -f1)"
    echo ""
    
    echo "staticfiles top-level contents:"
    ls -la staticfiles/ 2>/dev/null || echo "Cannot list staticfiles directory"
    echo ""
    
    echo "Checking for motortemplate in staticfiles:"
    if [ -d "staticfiles/motortemplate" ]; then
        echo "✅ staticfiles/motortemplate exists"
        ls -la staticfiles/motortemplate/ 2>/dev/null
        echo ""
        
        echo "Checking staticfiles/motortemplate/uren/assets/css/:"
        if [ -d "staticfiles/motortemplate/uren/assets/css" ]; then
            echo "✅ CSS directory exists"
            ls -la staticfiles/motortemplate/uren/assets/css/ 2>/dev/null
            echo ""
            
            if [ -f "staticfiles/motortemplate/uren/assets/css/vehicle-navigation.css" ]; then
                echo "✅ vehicle-navigation.css exists in staticfiles!"
                echo "File size: $(ls -lh staticfiles/motortemplate/uren/assets/css/vehicle-navigation.css | awk '{print $5}')"
                echo "First 10 lines:"
                head -10 "staticfiles/motortemplate/uren/assets/css/vehicle-navigation.css" | sed 's/^/    /'
            else
                echo "❌ vehicle-navigation.css NOT found in staticfiles CSS directory"
            fi
        else
            echo "❌ staticfiles/motortemplate/uren/assets/css directory does not exist"
        fi
    else
        echo "❌ staticfiles/motortemplate does not exist"
    fi
    
    echo ""
    echo "Checking for basic vehicle-navigation.css in staticfiles/css/:"
    if [ -f "staticfiles/css/vehicle-navigation.css" ]; then
        echo "✅ Found staticfiles/css/vehicle-navigation.css"
        echo "File size: $(ls -lh staticfiles/css/vehicle-navigation.css | awk '{print $5}')"
        echo "Contains custom-category_col:"
        grep -n "custom-category_col" "staticfiles/css/vehicle-navigation.css" || echo "  No custom-category_col found"
    else
        echo "❌ staticfiles/css/vehicle-navigation.css not found"
    fi
else
    echo "❌ staticfiles directory does not exist"
fi

echo ""

# =============================================================================
# SECTION 7: SOURCE FILES CHECK
# =============================================================================
echo "=== SECTION 7: SOURCE FILES CHECK ==="

echo "Checking source motortemplate directory:"
if [ -d "motortemplate" ]; then
    echo "✅ motortemplate directory exists"
    
    if [ -f "motortemplate/uren/assets/css/vehicle-navigation.css" ]; then
        echo "✅ Source vehicle-navigation.css exists"
        echo "File size: $(ls -lh motortemplate/uren/assets/css/vehicle-navigation.css | awk '{print $5}')"
        echo "Contains custom-category_col lines:"
        grep -n "custom-category_col" "motortemplate/uren/assets/css/vehicle-navigation.css" | head -5
        echo ""
        echo "File content preview (first 20 lines):"
        head -20 "motortemplate/uren/assets/css/vehicle-navigation.css" | sed 's/^/    /'
    else
        echo "❌ Source vehicle-navigation.css not found"
    fi
else
    echo "❌ motortemplate directory does not exist"
fi

echo ""

# =============================================================================
# SECTION 8: WEB SERVER FILE ACCESS TEST
# =============================================================================
echo "=== SECTION 8: WEB SERVER FILE ACCESS TEST ==="

echo "Testing file permissions:"
if [ -f "staticfiles/motortemplate/uren/assets/css/vehicle-navigation.css" ]; then
    echo "Permissions for vehicle-navigation.css:"
    ls -l "staticfiles/motortemplate/uren/assets/css/vehicle-navigation.css"
    
    echo "Directory permissions:"
    ls -ld staticfiles/
    ls -ld staticfiles/motortemplate/ 2>/dev/null || echo "motortemplate dir not accessible"
    ls -ld staticfiles/motortemplate/uren/ 2>/dev/null || echo "uren dir not accessible"
    ls -ld staticfiles/motortemplate/uren/assets/ 2>/dev/null || echo "assets dir not accessible"
    ls -ld staticfiles/motortemplate/uren/assets/css/ 2>/dev/null || echo "css dir not accessible"
else
    echo "Vehicle-navigation.css not found in staticfiles, checking basic version:"
    if [ -f "staticfiles/css/vehicle-navigation.css" ]; then
        ls -l "staticfiles/css/vehicle-navigation.css"
    else
        echo "No vehicle-navigation.css found in staticfiles"
    fi
fi

echo ""

# =============================================================================
# SECTION 9: NETWORK CONNECTIVITY TEST
# =============================================================================
echo "=== SECTION 9: NETWORK CONNECTIVITY TEST ==="

echo "Testing if we can reach the CSS file via HTTP:"
CSS_URL="https://vanparts-direct.co.uk/static/motortemplate/uren/assets/css/vehicle-navigation.css"
echo "Testing URL: $CSS_URL"

if command -v curl >/dev/null 2>&1; then
    echo "Using curl to test..."
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$CSS_URL")
    echo "HTTP Status: $HTTP_STATUS"
    
    if [ "$HTTP_STATUS" = "200" ]; then
        echo "✅ File is accessible via HTTP"
        echo "First few lines of the remote file:"
        curl -s "$CSS_URL" | head -10 | sed 's/^/    /'
    else
        echo "❌ File not accessible via HTTP (Status: $HTTP_STATUS)"
        
        # Test the fallback CSS file
        FALLBACK_URL="https://vanparts-direct.co.uk/static/css/vehicle-navigation.css"
        echo "Testing fallback URL: $FALLBACK_URL"
        FALLBACK_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$FALLBACK_URL")
        echo "Fallback HTTP Status: $FALLBACK_STATUS"
        
        if [ "$FALLBACK_STATUS" = "200" ]; then
            echo "✅ Fallback file is accessible"
            echo "Checking if fallback contains custom-category_col:"
            curl -s "$FALLBACK_URL" | grep -n "custom-category_col" | head -3 | sed 's/^/    /' || echo "    No custom-category_col found in fallback"
        fi
    fi
elif command -v wget >/dev/null 2>&1; then
    echo "Using wget to test..."
    if wget --spider -q "$CSS_URL" 2>/dev/null; then
        echo "✅ File is accessible via HTTP"
        echo "First few lines of the remote file:"
        wget -qO- "$CSS_URL" | head -10 | sed 's/^/    /'
    else
        echo "❌ File not accessible via HTTP"
    fi
else
    echo "Neither curl nor wget available for HTTP testing"
fi

echo ""

# =============================================================================
# SECTION 10: PROCESS AND SERVICE STATUS
# =============================================================================
echo "=== SECTION 10: PROCESS AND SERVICE STATUS ==="

echo "Checking for running web servers:"
echo "Nginx processes:"
ps aux | grep nginx | grep -v grep | sed 's/^/    /' || echo "    No nginx processes found"

echo "Gunicorn processes:"
ps aux | grep gunicorn | grep -v grep | sed 's/^/    /' || echo "    No gunicorn processes found"

echo "Apache processes:"
ps aux | grep apache | grep -v grep | sed 's/^/    /' || echo "    No apache processes found"

echo ""

echo "Checking systemd services (if available):"
if command -v systemctl >/dev/null 2>&1; then
    echo "Nginx service status:"
    systemctl is-active nginx 2>/dev/null || echo "    Nginx service not found or not active"
    
    echo "Gunicorn service status:"
    systemctl is-active gunicorn 2>/dev/null || echo "    Gunicorn service not found or not active"
    
    # Try to find any django-related services
    echo "Django-related services:"
    systemctl list-units --type=service | grep -i django | sed 's/^/    /' || echo "    No Django services found"
else
    echo "systemctl not available"
fi

echo ""

# =============================================================================
# SECTION 11: RECOMMENDED ACTIONS
# =============================================================================
echo "=== SECTION 11: RECOMMENDED ACTIONS ==="

echo "Based on the diagnostic results:"
echo ""

if [ ! -f "staticfiles/motortemplate/uren/assets/css/vehicle-navigation.css" ]; then
    echo "❌ ISSUE: vehicle-navigation.css missing from staticfiles"
    echo "   SOLUTION: Copy the file manually:"
    echo "   mkdir -p staticfiles/motortemplate/uren/assets/css/"
    echo "   cp motortemplate/uren/assets/css/vehicle-navigation.css staticfiles/motortemplate/uren/assets/css/"
    echo ""
fi

if [ -f "staticfiles/css/vehicle-navigation.css" ]; then
    if ! grep -q "custom-category_col" "staticfiles/css/vehicle-navigation.css" 2>/dev/null; then
        echo "❌ ISSUE: Basic vehicle-navigation.css missing responsive styles"
        echo "   The file exists but doesn't contain the critical .custom-category_col styles"
        echo ""
    fi
fi

echo "Standard post-deployment steps:"
echo "1. Ensure files are copied to staticfiles directory"
echo "2. Check file permissions (should be readable by web server)"
echo "3. Restart web server services"
echo "4. Clear browser cache"
echo ""

# =============================================================================
# SECTION 12: SUMMARY
# =============================================================================
echo "=== SECTION 12: DIAGNOSTIC SUMMARY ==="
echo "Diagnostic completed at: $(date)"
echo "Key findings will be summarized above in the recommended actions section."
echo ""
echo "Please copy this entire output and provide it for analysis."
echo "=========================================="
echo "END OF DIAGNOSTIC SCRIPT"
echo "=========================================="
