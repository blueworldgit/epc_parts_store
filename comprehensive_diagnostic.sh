#!/bin/bash
# Comprehensive Django + Nginx + Media Files Diagnostic Script
# This will show us everything needed to debug the media serving issue

echo "🔍 COMPREHENSIVE VANPARTS-DIRECT DIAGNOSTIC"
echo "==========================================="
echo "Date: $(date)"
echo "User: $(whoami)"
echo "Server: $(hostname) ($(hostname -I | awk '{print $1}'))"
echo ""

# 1. DJANGO PROCESS STATUS
echo "🐍 DJANGO PROCESS STATUS"
echo "======================="
DJANGO_PIDS=$(pgrep -f "manage.py runserver")
if [ -n "$DJANGO_PIDS" ]; then
    echo "✅ Django processes running:"
    ps aux | grep "manage.py runserver" | grep -v grep
    echo ""
    echo "Django listening ports:"
    netstat -tlnp 2>/dev/null | grep -E ":8000|:80" | grep -v grep
else
    echo "❌ No Django processes found"
fi
echo ""

# 2. NGINX STATUS AND CONFIGURATION
echo "🌐 NGINX STATUS AND CONFIGURATION"
echo "================================"
if command -v nginx >/dev/null 2>&1; then
    echo "✅ Nginx installed"
    echo "Version: $(nginx -v 2>&1)"
    echo ""
    
    echo "Nginx service status:"
    systemctl is-active nginx 2>/dev/null || echo "Service status unknown"
    echo ""
    
    echo "Nginx processes:"
    ps aux | grep nginx | grep -v grep || echo "No nginx processes"
    echo ""
    
    echo "Nginx listening ports:"
    netstat -tlnp 2>/dev/null | grep nginx || echo "No nginx ports found"
    echo ""
    
    echo "Nginx configuration test:"
    nginx -t 2>&1
    echo ""
    
    echo "Sites enabled:"
    ls -la /etc/nginx/sites-enabled/ 2>/dev/null || echo "No sites-enabled directory"
    echo ""
    
    echo "Active Nginx configuration for vanparts-direct:"
    if [ -f "/etc/nginx/sites-enabled/vanparts-direct.co.uk" ]; then
        echo "✅ vanparts-direct.co.uk site is enabled"
        echo "Configuration content:"
        echo "----------------------------------------"
        cat /etc/nginx/sites-enabled/vanparts-direct.co.uk
        echo "----------------------------------------"
    else
        echo "❌ vanparts-direct.co.uk site not found in sites-enabled"
        echo "Available sites:"
        ls -la /etc/nginx/sites-available/ 2>/dev/null | grep vanparts || echo "No vanparts sites found"
    fi
    echo ""
    
    echo "Nginx error log (last 10 lines):"
    tail -10 /var/log/nginx/error.log 2>/dev/null || echo "No nginx error log found"
    echo ""
    
    echo "Vanparts-direct error log (last 10 lines):"
    tail -10 /var/log/nginx/vanparts-direct.error.log 2>/dev/null || echo "No vanparts-direct error log found"
    echo ""
    
else
    echo "❌ Nginx not installed"
fi

# 3. DJANGO CONFIGURATION ANALYSIS
echo "⚙️ DJANGO CONFIGURATION ANALYSIS"
echo "================================"
PROJECT_DIR="/home/maxis/epc_parts_store/epcdata"
cd "$PROJECT_DIR" || exit 1

echo "Current directory: $(pwd)"
echo "Django settings analysis:"

export DJANGO_ENV=production
python manage.py shell -c "
from django.conf import settings
from django.urls import get_resolver
import sys
import os

print('=== DJANGO SETTINGS ===')
print(f'DEBUG: {settings.DEBUG}')
print(f'MEDIA_URL: {settings.MEDIA_URL}')
print(f'MEDIA_ROOT: {settings.MEDIA_ROOT}')
print(f'STATIC_URL: {settings.STATIC_URL}')
print(f'STATIC_ROOT: {settings.STATIC_ROOT}')
print(f'STATICFILES_DIRS: {settings.STATICFILES_DIRS}')
print(f'ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}')
print()

print('=== ENVIRONMENT ===')
print(f'DJANGO_ENV: {os.environ.get(\"DJANGO_ENV\", \"NOT SET\")}')
print(f'sys.argv: {sys.argv}')
print(f'runserver in sys.argv: {\"runserver\" in sys.argv}')
print()

print('=== URL PATTERNS ANALYSIS ===')
resolver = get_resolver()
print(f'Total URL patterns: {len(resolver.url_patterns)}')

# Check for media patterns
media_patterns = []
static_patterns = []
for pattern in resolver.url_patterns:
    pattern_str = str(pattern.pattern)
    if 'media' in pattern_str.lower():
        media_patterns.append(pattern_str)
    if 'static' in pattern_str.lower():
        static_patterns.append(pattern_str)

print(f'Media URL patterns found: {len(media_patterns)}')
for p in media_patterns:
    print(f'  {p}')

print(f'Static URL patterns found: {len(static_patterns)}')
for p in static_patterns:
    print(f'  {p}')

if not media_patterns:
    print('❌ NO MEDIA URL PATTERNS FOUND - This is the problem!')
    print('First 5 URL patterns:')
    for i, pattern in enumerate(resolver.url_patterns[:5]):
        print(f'  {i+1}. {pattern.pattern}')
"

echo ""

# 4. FILE SYSTEM ANALYSIS
echo "📁 FILE SYSTEM ANALYSIS"
echo "======================"
echo "Media directory analysis:"
MEDIA_DIR="/home/maxis/epc_parts_store/epcdata/media"
if [ -d "$MEDIA_DIR" ]; then
    echo "✅ Media directory exists: $MEDIA_DIR"
    echo "Permissions: $(ls -ld "$MEDIA_DIR")"
    echo "Contents:"
    ls -la "$MEDIA_DIR"
    
    echo ""
    echo "Specific files check:"
    for file in "header-styles-parent-fixed.css" "images/breadcrumb-van-interior.jpg"; do
        full_path="$MEDIA_DIR/$file"
        if [ -f "$full_path" ]; then
            echo "✅ $file exists"
            echo "   Path: $full_path"
            echo "   Size: $(stat -c%s "$full_path") bytes"
            echo "   Permissions: $(ls -la "$full_path")"
            echo "   File type: $(file "$full_path")"
        else
            echo "❌ $file missing from $full_path"
        fi
    done
else
    echo "❌ Media directory missing: $MEDIA_DIR"
fi

echo ""
echo "Static files analysis:"
STATIC_DIR="/home/maxis/epc_parts_store/epcdata/staticfiles"
if [ -d "$STATIC_DIR" ]; then
    echo "✅ Static directory exists: $STATIC_DIR"
    echo "Size: $(du -sh "$STATIC_DIR" | cut -f1)"
    echo "File count: $(find "$STATIC_DIR" -type f | wc -l)"
else
    echo "❌ Static directory missing: $STATIC_DIR"
fi

echo ""

# 5. NETWORK CONNECTIVITY TESTS
echo "🌐 NETWORK CONNECTIVITY TESTS"
echo "============================="
echo "Testing Django direct access:"
if [ -n "$DJANGO_PIDS" ]; then
    echo "Django root page:"
    curl -I http://127.0.0.1:8000/ 2>/dev/null | head -5 || echo "Failed to connect to Django"
    
    echo ""
    echo "Django media file test:"
    curl -I http://127.0.0.1:8000/media/header-styles-parent-fixed.css 2>/dev/null | head -5 || echo "Failed to get media file from Django"
    
    echo ""
    echo "Django media directory test:"
    curl -I http://127.0.0.1:8000/media/ 2>/dev/null | head -5 || echo "Failed to access media directory"
else
    echo "❌ Django not running - skipping direct tests"
fi

echo ""
echo "Testing Nginx proxy access:"
echo "External domain test:"
curl -I http://vanparts-direct.co.uk/ 2>/dev/null | head -5 || echo "Failed to connect via domain"

echo ""
echo "External media file test:"
curl -I http://vanparts-direct.co.uk/media/header-styles-parent-fixed.css 2>/dev/null | head -5 || echo "Failed to get media file via domain"

echo ""

# 6. LOG ANALYSIS
echo "📝 LOG ANALYSIS" 
echo "==============="
echo "Django access log (last 10 requests):"
if [ -f "django.log" ]; then
    tail -10 django.log | grep -E "GET|POST|HEAD" || echo "No recent requests in django.log"
elif [ -n "$DJANGO_PIDS" ]; then
    echo "Django running but no log file found (probably stdout)"
else
    echo "No Django log available"
fi

echo ""
echo "System log for Django (last 5 lines):"
journalctl -u vanparts-direct --no-pager -n 5 2>/dev/null || echo "No systemd service logs"

echo ""

# 7. TEMPLATE ANALYSIS
echo "📝 TEMPLATE ANALYSIS"
echo "==================="
echo "Templates referencing media files:"
find templates/ -name "*.html" -exec grep -l "media/" {} \; 2>/dev/null | while read template; do
    echo "File: $template"
    grep -n "media/" "$template" | head -3
    echo ""
done

echo ""

# 8. QUICK TESTS AND FIXES
echo "🧪 QUICK TESTS AND FIXES"
echo "======================="
echo "File permissions check:"
echo "Media directory: $(ls -ld "$MEDIA_DIR" 2>/dev/null | awk '{print $1, $3, $4}')"
echo "Django user: $(whoami)"
echo "Django groups: $(groups)"

echo ""
echo "Disk space:"
df -h "$PROJECT_DIR" | tail -1

echo ""
echo "Process ownership:"
if [ -n "$DJANGO_PIDS" ]; then
    ps -o pid,user,group,command -p $DJANGO_PIDS
fi

echo ""

# 9. SUGGESTED FIXES
echo "🛠️ SUGGESTED IMMEDIATE FIXES"
echo "==========================="
echo ""
echo "1. If Django has no media URL patterns:"
echo "   - Check urls.py media serving configuration"
echo "   - Verify static() import and usage"
echo ""
echo "2. If files exist but return 404:"
echo "   - Check Django URL routing"
echo "   - Verify MEDIA_URL and MEDIA_ROOT settings"
echo ""  
echo "3. If Nginx is blocking media requests:"
echo "   - Check nginx configuration for /media/ location"
echo "   - Verify proxy_pass settings"
echo ""
echo "4. Quick test command:"
echo "   python manage.py runserver 0.0.0.0:8000"
echo "   (then test http://SERVER_IP:8000/media/header-styles-parent-fixed.css)"
echo ""

echo "📋 DIAGNOSTIC COMPLETE"
echo "====================="
echo "Analysis completed at $(date)"