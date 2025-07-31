#!/bin/bash

# Django Static Files Diagnostic Script
# This script will gather comprehensive information about Django static file configuration
# Run this script from your Django project root directory

echo "=========================================="
echo "Django Static Files Diagnostic Report"
echo "Generated: $(date)"
echo "=========================================="

# Check current directory
echo
echo "1. CURRENT WORKING DIRECTORY:"
echo "Current directory: $(pwd)"
echo "Directory contents:"
ls -la
echo

# Check Python and Django versions
echo "2. PYTHON & DJANGO ENVIRONMENT:"
echo "Python version: $(python --version 2>&1)"
echo "Django version:"
python -c "import django; print(django.get_version())" 2>/dev/null || echo "Django not found"
echo "Virtual environment: $VIRTUAL_ENV"
echo

# Check which settings module is being used
echo "3. DJANGO SETTINGS:"
echo "DJANGO_SETTINGS_MODULE: $DJANGO_SETTINGS_MODULE"
python manage.py shell -c "
from django.conf import settings
print('Settings module:', settings.SETTINGS_MODULE)
print('DEBUG:', settings.DEBUG)
print('STATIC_URL:', settings.STATIC_URL)
print('STATIC_ROOT:', settings.STATIC_ROOT)
print('STATICFILES_DIRS:', settings.STATICFILES_DIRS)
print('STATICFILES_FINDERS:', settings.STATICFILES_FINDERS)
print('STATICFILES_STORAGE:', settings.STATICFILES_STORAGE)
print('BASE_DIR:', settings.BASE_DIR)
" 2>/dev/null
echo

# Check WhiteNoise configuration
echo "4. WHITENOISE CONFIGURATION:"
python manage.py shell -c "
from django.conf import settings
middleware = getattr(settings, 'MIDDLEWARE', [])
print('WhiteNoise in MIDDLEWARE:', any('whitenoise' in m.lower() for m in middleware))
for i, m in enumerate(middleware):
    if 'whitenoise' in m.lower():
        print(f'  Position {i}: {m}')

# Check WhiteNoise settings
whitenoise_settings = [attr for attr in dir(settings) if attr.startswith('WHITENOISE')]
for setting in whitenoise_settings:
    print(f'{setting}: {getattr(settings, setting, \"Not set\")}')
" 2>/dev/null
echo

# Check file structure
echo "5. FILE STRUCTURE:"
echo "motortemplate directory:"
if [ -d "motortemplate" ]; then
    echo "  ✓ motortemplate exists"
    ls -la motortemplate/
    echo
    echo "  Bootstrap files in motortemplate:"
    find motortemplate/ -name "*bootstrap*" -type f 2>/dev/null
else
    echo "  ✗ motortemplate directory not found"
fi
echo

echo "staticfiles directory:"
if [ -d "staticfiles" ]; then
    echo "  ✓ staticfiles exists"
    echo "  Size: $(du -sh staticfiles/ 2>/dev/null | cut -f1)"
    echo "  Contents:"
    ls -la staticfiles/ 2>/dev/null | head -10
    echo
    echo "  Bootstrap files in staticfiles:"
    find staticfiles/ -name "*bootstrap*" -type f 2>/dev/null
else
    echo "  ✗ staticfiles directory not found"
fi
echo

# Check templates
echo "6. TEMPLATE CONFIGURATION:"
echo "templates directory:"
if [ -d "templates" ]; then
    echo "  ✓ templates exists"
    find templates/ -name "*.html" | head -10
else
    echo "  ✗ templates directory not found"
fi

echo
echo "Oscar storefront template:"
if [ -f "templates/oscar/storefront_base.html" ]; then
    echo "  ✓ templates/oscar/storefront_base.html exists"
    echo "  Bootstrap references in template:"
    grep -n "bootstrap" templates/oscar/storefront_base.html 2>/dev/null || echo "  No bootstrap references found"
else
    echo "  ✗ templates/oscar/storefront_base.html not found"
fi
echo

# Test Django static file finders
echo "7. DJANGO STATIC FILE FINDERS TEST:"
python manage.py shell -c "
from django.contrib.staticfiles import finders
import os

# Test different bootstrap paths
test_paths = [
    'motortemplate/assets/css/bootstrap.min.css',
    'motortemplate/uren/assets/css/vendor/bootstrap.min.css',
    'bootstrap.min.css'
]

for path in test_paths:
    result = finders.find(path)
    print(f'Finding \"{path}\": {result}')

# List all finders and their locations
print()
print('Available finders:')
for finder in finders.get_finders():
    print(f'  {finder.__class__.__name__}')
    if hasattr(finder, 'locations'):
        for prefix, location in finder.locations:
            print(f'    Location: {location} (prefix: \"{prefix}\")')
            if os.path.exists(location):
                print(f'      ✓ Path exists')
                # List first few files
                try:
                    files = os.listdir(location)[:5]
                    print(f'      Sample files: {files}')
                except:
                    print(f'      Cannot list directory contents')
            else:
                print(f'      ✗ Path does not exist')
" 2>/dev/null
echo

# Test collectstatic dry run
echo "8. COLLECTSTATIC DRY RUN:"
echo "Running collectstatic --dry-run to see what files would be collected..."
python manage.py collectstatic --dry-run --noinput --verbosity=2 2>&1 | head -20
echo "... (output truncated)"
echo

# Check for motortemplate files specifically
echo "9. MOTORTEMPLATE FILES IN COLLECTSTATIC:"
python manage.py collectstatic --dry-run --noinput --verbosity=2 2>&1 | grep -i motortemplate || echo "No motortemplate files found in collectstatic output"
echo

# Test URL patterns
echo "10. URL CONFIGURATION:"
python manage.py shell -c "
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
import sys

print('STATIC_URL:', settings.STATIC_URL)
print('STATIC_ROOT:', settings.STATIC_ROOT)

# Check if static URLs are configured
try:
    from django.urls import reverse
    print('URL configuration appears to be working')
except Exception as e:
    print('URL configuration error:', e)
" 2>/dev/null
echo

# Test actual HTTP requests to static files
echo "11. HTTP STATIC FILE TESTS:"
echo "Testing static file URLs (if server is running)..."

# Check if server is running on common ports
for port in 8000 8080 80; do
    if nc -z localhost $port 2>/dev/null; then
        echo "Server detected on port $port"
        
        # Test bootstrap file
        echo "Testing: http://localhost:$port/static/motortemplate/assets/css/bootstrap.min.css"
        curl -I "http://localhost:$port/static/motortemplate/assets/css/bootstrap.min.css" 2>/dev/null | head -1 || echo "Request failed"
        
        echo "Testing: http://localhost:$port/static/bootstrap.min.css"
        curl -I "http://localhost:$port/static/bootstrap.min.css" 2>/dev/null | head -1 || echo "Request failed"
        break
    fi
done
echo

# File permissions check
echo "12. FILE PERMISSIONS:"
echo "Checking permissions on key directories and files..."

for path in motortemplate staticfiles templates; do
    if [ -e "$path" ]; then
        echo "$path permissions: $(ls -ld $path)"
    fi
done

if [ -f "motortemplate/assets/css/bootstrap.min.css" ]; then
    echo "Bootstrap file permissions: $(ls -l motortemplate/assets/css/bootstrap.min.css)"
fi

if [ -f "staticfiles/bootstrap.min.css" ]; then
    echo "Staticfiles bootstrap permissions: $(ls -l staticfiles/bootstrap.min.css)"
fi
echo

# Environment variables
echo "13. ENVIRONMENT VARIABLES:"
echo "DEBUG: $DEBUG"
echo "DJANGO_SETTINGS_MODULE: $DJANGO_SETTINGS_MODULE"
env | grep -E "(DJANGO|STATIC|WHITENOISE)" | sort
echo

# Process information
echo "14. RUNNING PROCESSES:"
echo "Django processes:"
ps aux | grep -E "(manage.py|python.*runserver)" | grep -v grep || echo "No Django processes found"
echo

# Disk space
echo "15. DISK SPACE:"
echo "Available disk space:"
df -h . 2>/dev/null
echo

# Final recommendations
echo "16. DIAGNOSTIC SUMMARY:"
echo "Key files to check:"
echo "  - motortemplate/assets/css/bootstrap.min.css: $([ -f 'motortemplate/assets/css/bootstrap.min.css' ] && echo '✓ EXISTS' || echo '✗ MISSING')"
echo "  - staticfiles/bootstrap.min.css: $([ -f 'staticfiles/bootstrap.min.css' ] && echo '✓ EXISTS' || echo '✗ MISSING')"
echo "  - templates/oscar/storefront_base.html: $([ -f 'templates/oscar/storefront_base.html' ] && echo '✓ EXISTS' || echo '✗ MISSING')"

echo
echo "=========================================="
echo "Diagnostic Complete"
echo "Please share this entire output for analysis"
echo "=========================================="
