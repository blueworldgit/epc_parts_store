#!/bin/bash
# Media Files Troubleshooting Script for vanparts-direct.co.uk
# This will show us exactly what's happening with media files

echo "🔍 MEDIA FILES TROUBLESHOOTING REPORT"
echo "===================================="
echo "Date: $(date)"
echo "User: $(whoami)"
echo "Current directory: $(pwd)"
echo ""

# 1. Check project structure
echo "📁 PROJECT STRUCTURE"
echo "==================="
PROJECT_DIR="/home/maxis/epc_parts_store/epcdata"
echo "Project directory: $PROJECT_DIR"

if [ -d "$PROJECT_DIR" ]; then
    echo "✅ Project directory exists"
    cd "$PROJECT_DIR" || exit 1
    echo "Current working directory: $(pwd)"
else
    echo "❌ Project directory not found!"
    exit 1
fi

# 2. Check Django settings for media configuration
echo ""
echo "⚙️ DJANGO MEDIA CONFIGURATION"
echo "============================="
if [ -f "epcdata/settings.py" ]; then
    echo "Django MEDIA settings from settings.py:"
    grep -n "MEDIA_" epcdata/settings.py | head -10
else
    echo "❌ settings.py not found"
fi

echo ""
echo "Environment variables:"
echo "DJANGO_ENV = ${DJANGO_ENV:-'NOT SET'}"

# 3. Check media directory structure
echo ""
echo "📂 MEDIA DIRECTORY ANALYSIS"
echo "=========================="
MEDIA_DIR="$PROJECT_DIR/media"
echo "Expected MEDIA_ROOT: $MEDIA_DIR"

if [ -d "$MEDIA_DIR" ]; then
    echo "✅ Media directory exists"
    echo "Directory permissions: $(ls -ld "$MEDIA_DIR")"
    echo "Directory size: $(du -sh "$MEDIA_DIR" 2>/dev/null | cut -f1)"
    
    echo ""
    echo "Media directory contents:"
    ls -la "$MEDIA_DIR"
    
    echo ""
    echo "All files in media directory (recursive):"
    find "$MEDIA_DIR" -type f -exec ls -la {} \; 2>/dev/null
    
else
    echo "❌ Media directory does not exist"
    echo "Creating media directory..."
    mkdir -p "$MEDIA_DIR"
    echo "✅ Created media directory"
fi

# 4. Check for the specific missing files
echo ""
echo "🔍 MISSING FILES CHECK"
echo "====================="
MISSING_FILES=(
    "header-styles-parent-fixed.css"
    "images/breadcrumb-van-interior.jpg"
)

for file in "${MISSING_FILES[@]}"; do
    FULL_PATH="$MEDIA_DIR/$file"
    echo "Checking: $file"
    echo "  Expected path: $FULL_PATH"
    
    if [ -f "$FULL_PATH" ]; then
        echo "  ✅ File exists"
        echo "  File info: $(ls -la "$FULL_PATH")"
        echo "  File size: $(stat -c%s "$FULL_PATH") bytes"
        echo "  File type: $(file "$FULL_PATH")"
    else
        echo "  ❌ File missing"
        
        # Search for the file elsewhere
        echo "  Searching for $(basename "$file") in project..."
        find "$PROJECT_DIR" -name "$(basename "$file")" -type f 2>/dev/null | head -5
        
        # Check parent directory
        PARENT_DIR=$(dirname "$FULL_PATH")
        if [ ! -d "$PARENT_DIR" ]; then
            echo "  ❌ Parent directory missing: $PARENT_DIR"
        else
            echo "  ✅ Parent directory exists: $PARENT_DIR"
        fi
    fi
    echo ""
done

# 5. Check static files directory for comparison
echo ""
echo "📦 STATIC FILES COMPARISON"
echo "========================="
STATIC_DIR="$PROJECT_DIR/staticfiles"
if [ -d "$STATIC_DIR" ]; then
    echo "✅ Static files directory exists: $STATIC_DIR"
    echo "Static directory size: $(du -sh "$STATIC_DIR" 2>/dev/null | cut -f1)"
    echo "Static files count: $(find "$STATIC_DIR" -type f | wc -l)"
else
    echo "❌ Static files directory missing"
fi

# Check motortemplate directory
MOTORTEMPLATE_DIR="$PROJECT_DIR/motortemplate"
if [ -d "$MOTORTEMPLATE_DIR" ]; then
    echo "✅ Motortemplate directory exists: $MOTORTEMPLATE_DIR"
    echo "Searching for CSS files in motortemplate:"
    find "$MOTORTEMPLATE_DIR" -name "*.css" | head -10
    echo "Searching for image files in motortemplate:"
    find "$MOTORTEMPLATE_DIR" -name "*.jpg" -o -name "*.png" -o -name "*.gif" | head -10
else
    echo "❌ Motortemplate directory missing"
fi

# 6. Check where these files might be referenced
echo ""
echo "🔍 TEMPLATE ANALYSIS"
echo "=================="
echo "Searching for references to the missing files in templates:"

if [ -d "templates" ]; then
    echo "References to 'header-styles-parent-fixed.css':"
    grep -r "header-styles-parent-fixed.css" templates/ 2>/dev/null || echo "  No references found"
    
    echo "References to 'breadcrumb-van-interior.jpg':"
    grep -r "breadcrumb-van-interior.jpg" templates/ 2>/dev/null || echo "  No references found"
    
    echo "All media/ references in templates:"
    grep -r "/media/" templates/ 2>/dev/null | head -10 || echo "  No media references found"
else
    echo "❌ Templates directory not found"
fi

# 7. Check Django's current media serving
echo ""
echo "🌐 DJANGO MEDIA SERVING TEST"
echo "============================"
echo "Testing if Django can serve media files..."

# Check if Django is running
DJANGO_PID=$(pgrep -f "manage.py runserver")
if [ -n "$DJANGO_PID" ]; then
    echo "✅ Django is running (PID: $DJANGO_PID)"
    echo "Testing media URL access..."
    
    # Test media directory access
    curl -I http://127.0.0.1:8000/media/ 2>/dev/null && echo "✅ /media/ accessible" || echo "❌ /media/ not accessible"
    
    # Test specific missing files
    for file in "${MISSING_FILES[@]}"; do
        echo "Testing /media/$file..."
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:8000/media/$file")
        echo "  HTTP response: $HTTP_CODE"
    done
else
    echo "❌ Django is not running"
fi

# 8. Check file permissions and ownership
echo ""
echo "🔐 PERMISSIONS CHECK"
echo "=================="
echo "Media directory ownership and permissions:"
ls -la "$(dirname "$MEDIA_DIR")" | grep "$(basename "$MEDIA_DIR")"

if [ -d "$MEDIA_DIR" ]; then
    echo "Contents permissions:"
    ls -la "$MEDIA_DIR"
fi

# 9. Disk space check
echo ""
echo "💾 DISK SPACE"
echo "============="
df -h "$PROJECT_DIR"

# 10. Generate fix suggestions
echo ""
echo "🛠️ SUGGESTED FIXES"
echo "=================="
echo "Based on the analysis above:"
echo ""
echo "1. If files are missing from media/ directory:"
echo "   - Copy actual files from your development environment"
echo "   - Or create placeholder files for testing"
echo ""
echo "2. If files exist but aren't accessible:"
echo "   - Check Django settings for MEDIA_URL and MEDIA_ROOT"
echo "   - Verify Django is serving media files in development"
echo "   - Check Nginx configuration for media file serving"
echo ""
echo "3. If templates reference wrong paths:"
echo "   - Update template references to use proper {% static %} or {{ MEDIA_URL }}"
echo ""
echo "4. Common commands to fix issues:"
echo "   mkdir -p media/images"
echo "   chown -R maxis:maxis media/"
echo "   chmod -R 644 media/"
echo "   find media/ -type d -exec chmod 755 {} \\;"
echo ""

echo "📋 TROUBLESHOOTING COMPLETE"
echo "=========================="
echo "Review the output above to identify the root cause."