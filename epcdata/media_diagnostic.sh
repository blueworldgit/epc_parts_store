#!/bin/bash

echo "=========================================="
echo "DJANGO MEDIA FILES DIAGNOSTIC SCRIPT"
echo "=========================================="
echo "Timestamp: $(date)"
echo "User: $(whoami)"
echo "Current Directory: $(pwd)"
echo ""

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "❌ ERROR: manage.py not found in current directory"
    echo "Please run this script from the epcdata directory"
    exit 1
fi

echo "✅ Found manage.py - we're in the correct Django project directory"
echo ""

echo "=== SECTION 1: DJANGO MEDIA SETTINGS ==="
# Activate virtual environment if it exists
if [ -f "../env/bin/activate" ]; then
    source ../env/bin/activate
fi

echo "MEDIA_URL:"
python manage.py shell -c "from django.conf import settings; print(settings.MEDIA_URL)" 2>/dev/null || echo "Error getting MEDIA_URL"

echo "MEDIA_ROOT:"
python manage.py shell -c "from django.conf import settings; print(settings.MEDIA_ROOT)" 2>/dev/null || echo "Error getting MEDIA_ROOT"

echo ""

echo "=== SECTION 2: MEDIA DIRECTORY ANALYSIS ==="
echo "Checking media directory structure..."

MEDIA_ROOT=$(python manage.py shell -c "from django.conf import settings; print(settings.MEDIA_ROOT)" 2>/dev/null)
if [ -n "$MEDIA_ROOT" ] && [ -d "$MEDIA_ROOT" ]; then
    echo "✅ MEDIA_ROOT directory exists: $MEDIA_ROOT"
    echo "Total size: $(du -sh "$MEDIA_ROOT" 2>/dev/null | cut -f1)"
    
    echo ""
    echo "Media directory contents:"
    ls -la "$MEDIA_ROOT" 2>/dev/null | head -10
    
    echo ""
    echo "Looking for cache directory:"
    if [ -d "$MEDIA_ROOT/cache" ]; then
        echo "✅ Cache directory exists"
        echo "Cache size: $(du -sh "$MEDIA_ROOT/cache" 2>/dev/null | cut -f1)"
        echo "Sample cache files:"
        find "$MEDIA_ROOT/cache" -name "*.jpg" -o -name "*.png" | head -5
    else
        echo "❌ Cache directory not found"
    fi
    
    echo ""
    echo "Looking for uploaded images:"
    find "$MEDIA_ROOT" -name "*.jpg" -o -name "*.png" | head -10
    
else
    echo "❌ MEDIA_ROOT directory not found or not accessible"
fi

echo ""

echo "=== SECTION 3: NGINX MEDIA CONFIGURATION ==="
echo "Checking nginx configuration for media files..."

if [ -f "/etc/nginx/sites-available/default" ]; then
    echo "Nginx default site configuration:"
    grep -A5 -B5 "media" /etc/nginx/sites-available/default 2>/dev/null || echo "No media configuration found in default site"
fi

if [ -f "/etc/nginx/sites-enabled/default" ]; then
    echo ""
    echo "Nginx enabled site configuration:"
    grep -A5 -B5 "media" /etc/nginx/sites-enabled/default 2>/dev/null || echo "No media configuration found in enabled site"
fi

# Look for any nginx conf files
echo ""
echo "Looking for nginx configurations with media settings:"
find /etc/nginx -name "*.conf" -exec grep -l "media" {} \; 2>/dev/null | while read conf_file; do
    echo "Found media config in: $conf_file"
    grep -A3 -B3 "media" "$conf_file" 2>/dev/null
done

echo ""

echo "=== SECTION 4: FILE PERMISSIONS ==="
echo "Checking file permissions for media files..."

if [ -n "$MEDIA_ROOT" ] && [ -d "$MEDIA_ROOT" ]; then
    echo "Media root permissions:"
    ls -ld "$MEDIA_ROOT"
    
    if [ -d "$MEDIA_ROOT/cache" ]; then
        echo "Cache directory permissions:"
        ls -ld "$MEDIA_ROOT/cache"
        
        echo "Sample cache file permissions:"
        find "$MEDIA_ROOT/cache" -type f | head -3 | xargs ls -l 2>/dev/null
    fi
fi

echo ""

echo "=== SECTION 5: SORL-THUMBNAIL SETTINGS ==="
echo "Checking sorl-thumbnail configuration..."

echo "THUMBNAIL_ENGINE:"
python manage.py shell -c "
try:
    from django.conf import settings
    print(getattr(settings, 'THUMBNAIL_ENGINE', 'Not set'))
except Exception as e:
    print(f'Error: {e}')
" 2>/dev/null

echo "THUMBNAIL_KEY_PREFIX:"
python manage.py shell -c "
try:
    from django.conf import settings
    print(getattr(settings, 'THUMBNAIL_KEY_PREFIX', 'Not set'))
except Exception as e:
    print(f'Error: {e}')
" 2>/dev/null

echo "THUMBNAIL_FORMAT:"
python manage.py shell -c "
try:
    from django.conf import settings
    print(getattr(settings, 'THUMBNAIL_FORMAT', 'Not set'))
except Exception as e:
    print(f'Error: {e}')
" 2>/dev/null

echo ""

echo "=== SECTION 6: URL CONFIGURATION ==="
echo "Checking URL patterns for media serving..."

echo "Checking main urls.py for media patterns:"
find . -name "urls.py" | xargs grep -l "media" | while read url_file; do
    echo "Found media URLs in: $url_file"
    grep -A2 -B2 "media" "$url_file"
    echo ""
done

echo ""

echo "=== SECTION 7: SPECIFIC IMAGE TEST ==="
echo "Testing the specific broken image..."

BROKEN_IMAGE_PATH="/media/cache/bc/07/bc0729419b53eb2d0651e42b837daf02.jpg"
echo "Looking for: $BROKEN_IMAGE_PATH"

if [ -n "$MEDIA_ROOT" ]; then
    FULL_PATH="$MEDIA_ROOT${BROKEN_IMAGE_PATH#/media}"
    echo "Full filesystem path: $FULL_PATH"
    
    if [ -f "$FULL_PATH" ]; then
        echo "✅ File exists on filesystem"
        ls -l "$FULL_PATH"
    else
        echo "❌ File does not exist on filesystem"
        
        echo "Looking for similar files:"
        dirname_path=$(dirname "$FULL_PATH")
        if [ -d "$dirname_path" ]; then
            echo "Directory contents:"
            ls -la "$dirname_path"
        else
            echo "Directory does not exist: $dirname_path"
        fi
    fi
fi

echo ""

echo "=== SECTION 8: DJANGO DEBUG INFO ==="
echo "Getting Django debug information..."

echo "DEBUG setting:"
python manage.py shell -c "from django.conf import settings; print(settings.DEBUG)" 2>/dev/null || echo "Error getting DEBUG"

echo "ALLOWED_HOSTS:"
python manage.py shell -c "from django.conf import settings; print(settings.ALLOWED_HOSTS)" 2>/dev/null || echo "Error getting ALLOWED_HOSTS"

echo ""

echo "=== SECTION 9: RECOMMENDATIONS ==="
echo "Based on the diagnostic results:"
echo ""
echo "Common media file issues and solutions:"
echo "1. Nginx not configured to serve media files"
echo "2. Incorrect MEDIA_ROOT or MEDIA_URL settings"
echo "3. File permissions preventing web server access"
echo "4. Missing sorl-thumbnail cache generation"
echo "5. URL patterns not including media serving"
echo ""
echo "To fix media serving:"
echo "1. Check nginx configuration has proper media location block"
echo "2. Ensure MEDIA_ROOT directory exists and is writable"
echo "3. Run: python manage.py thumbnail clear_delete_all"
echo "4. Run: python manage.py thumbnail cleanup"
echo "5. Restart nginx: sudo systemctl restart nginx"

echo ""
echo "=========================================="
echo "END OF MEDIA FILES DIAGNOSTIC SCRIPT"
echo "=========================================="
