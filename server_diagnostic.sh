#!/bin/bash
# Comprehensive server diagnostic script for vanparts-direct.co.uk
# This will analyze file structure and generate nginx configuration data

set -e

echo "🔍 VANPARTS-DIRECT.CO.UK SERVER DIAGNOSTIC"
echo "=========================================="
echo "Date: $(date)"
echo "User: $(whoami)"
echo "Hostname: $(hostname)"
echo "IP Address: $(hostname -I | awk '{print $1}')"
echo ""

# Project paths
PROJECT_DIR="/home/maxis/epc_parts_store/epcdata"
echo "📁 PROJECT STRUCTURE ANALYSIS"
echo "=============================="
echo "Project Directory: $PROJECT_DIR"

# Check if project exists
if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ Project directory not found!"
    echo "Looking for alternative locations..."
    find /home -name "epcdata" -type d 2>/dev/null | head -5
    exit 1
fi

echo "✅ Project directory exists"
cd "$PROJECT_DIR"
echo "Current working directory: $(pwd)"
echo ""

# Python environment
echo "🐍 PYTHON ENVIRONMENT"
echo "===================="
echo "Python version: $(python3 --version 2>/dev/null || echo 'Python3 not found')"
echo "Virtual env check:"
if [ -d "env" ]; then
    echo "✅ Virtual environment exists at: $PROJECT_DIR/env"
    echo "Python executable: $PROJECT_DIR/env/bin/python"
    echo "Pip packages installed:"
    $PROJECT_DIR/env/bin/pip list | grep -E "(Django|oscar|gunicorn|whitenoise)" || echo "No Django packages found"
else
    echo "❌ Virtual environment not found"
fi
echo ""

# Django settings analysis
echo "⚙️ DJANGO CONFIGURATION"
echo "======================="
echo "Settings file: $PROJECT_DIR/epcdata/settings.py"
if [ -f "$PROJECT_DIR/epcdata/settings.py" ]; then
    echo "✅ Settings file exists"
    
    # Extract key settings
    echo ""
    echo "Key Django Settings:"
    echo "-------------------"
    
    # Check DEBUG setting
    DEBUG_LINE=$(grep -n "DEBUG.*=" epcdata/settings.py | head -1)
    echo "DEBUG: $DEBUG_LINE"
    
    # Check STATIC settings
    echo ""
    echo "Static Files Configuration:"
    grep -n "STATIC_" epcdata/settings.py | head -5
    
    echo ""
    echo "Media Files Configuration:"
    grep -n "MEDIA_" epcdata/settings.py | head -5
    
    echo ""
    echo "Allowed Hosts:"
    grep -n "ALLOWED_HOSTS" epcdata/settings.py | head -3
    
else
    echo "❌ Settings file not found"
fi
echo ""

# Environment files
echo "🌍 ENVIRONMENT FILES"
echo "==================="
for env_file in .env .env.production .prod; do
    if [ -f "$env_file" ]; then
        echo "✅ $env_file exists"
        echo "   Size: $(stat -c%s "$env_file") bytes"
        echo "   Modified: $(stat -c%y "$env_file")"
        echo "   Key variables:"
        grep -E "^(DEBUG|ALLOWED_HOSTS|DB_|STATIC_|MEDIA_)" "$env_file" 2>/dev/null | head -5 || echo "   No key variables found"
    else
        echo "❌ $env_file not found"
    fi
done
echo ""

# Directory structure analysis
echo "📂 DIRECTORY STRUCTURE"
echo "====================="

# Static files
echo "Static Files Analysis:"
echo "---------------------"
STATIC_ROOT="$PROJECT_DIR/staticfiles"
STATIC_DIRS="$PROJECT_DIR/motortemplate"

echo "STATIC_ROOT (collected files): $STATIC_ROOT"
if [ -d "$STATIC_ROOT" ]; then
    echo "✅ staticfiles directory exists"
    echo "   Size: $(du -sh "$STATIC_ROOT" 2>/dev/null | cut -f1)"
    echo "   File count: $(find "$STATIC_ROOT" -type f | wc -l)"
    echo "   Top-level contents:"
    ls -la "$STATIC_ROOT" | head -10
else
    echo "❌ staticfiles directory not found"
fi

echo ""
echo "STATICFILES_DIRS (source files): $STATIC_DIRS"
if [ -d "$STATIC_DIRS" ]; then
    echo "✅ motortemplate directory exists"
    echo "   Size: $(du -sh "$STATIC_DIRS" 2>/dev/null | cut -f1)"
    echo "   Structure:"
    find "$STATIC_DIRS" -type d | head -10
    echo "   CSS files:"
    find "$STATIC_DIRS" -name "*.css" | head -5
    echo "   JS files:"
    find "$STATIC_DIRS" -name "*.js" | head -5
    echo "   Image files:"
    find "$STATIC_DIRS" -name "*.jpg" -o -name "*.png" -o -name "*.gif" | head -5
else
    echo "❌ motortemplate directory not found"
fi

echo ""
echo "Media Files Analysis:"
echo "--------------------"
MEDIA_ROOT="$PROJECT_DIR/media"
echo "MEDIA_ROOT: $MEDIA_ROOT"
if [ -d "$MEDIA_ROOT" ]; then
    echo "✅ media directory exists"
    echo "   Size: $(du -sh "$MEDIA_ROOT" 2>/dev/null | cut -f1)"
    echo "   Contents:"
    find "$MEDIA_ROOT" -type f | head -10
else
    echo "❌ media directory not found"
    echo "Creating media directory..."
    mkdir -p "$MEDIA_ROOT"
    echo "✅ Created media directory"
fi

echo ""

# Check for missing files from errors
echo "🔍 MISSING FILES CHECK"
echo "====================="
MISSING_FILES=(
    "media/header-styles-parent-fixed.css"
    "media/images/breadcrumb-van-interior.jpg"
)

for file in "${MISSING_FILES[@]}"; do
    FULL_PATH="$PROJECT_DIR/$file"
    if [ -f "$FULL_PATH" ]; then
        echo "✅ $file exists"
    else
        echo "❌ $file missing"
        echo "   Expected at: $FULL_PATH"
        
        # Check if it exists elsewhere
        echo "   Searching for $(basename "$file")..."
        find "$PROJECT_DIR" -name "$(basename "$file")" 2>/dev/null | head -3
    fi
done

echo ""

# Templates analysis
echo "📝 TEMPLATES ANALYSIS"
echo "===================="
TEMPLATES_DIR="$PROJECT_DIR/templates"
if [ -d "$TEMPLATES_DIR" ]; then
    echo "✅ Templates directory exists: $TEMPLATES_DIR"
    echo "   Template files:"
    find "$TEMPLATES_DIR" -name "*.html" | head -10
else
    echo "❌ Templates directory not found"
fi

echo ""

# Database check
echo "🗄️ DATABASE CHECK"
echo "================="
echo "PostgreSQL service status:"
systemctl is-active postgresql 2>/dev/null || echo "PostgreSQL service status unknown"
echo "Database connection test:"
if command -v psql >/dev/null 2>&1; then
    echo "✅ psql command available"
else
    echo "❌ psql command not found"
fi

echo ""

# Web server check
echo "🌐 WEB SERVER ANALYSIS"
echo "====================="
echo "Nginx status:"
systemctl is-active nginx 2>/dev/null || echo "Nginx not installed/running"

if command -v nginx >/dev/null 2>&1; then
    echo "✅ Nginx installed"
    echo "   Version: $(nginx -v 2>&1)"
    echo "   Configuration test: $(nginx -t 2>&1 | head -2)"
    echo "   Sites enabled:"
    ls -la /etc/nginx/sites-enabled/ 2>/dev/null || echo "   No sites enabled directory"
else
    echo "❌ Nginx not installed"
fi

echo ""
echo "Current ports in use:"
netstat -tlnp 2>/dev/null | grep -E ":(80|443|8000|8080)" || echo "No relevant ports found"

echo ""

# SSL certificates check
echo "🔒 SSL CERTIFICATES"
echo "=================="
if command -v certbot >/dev/null 2>&1; then
    echo "✅ Certbot installed"
    echo "   Certificates:"
    certbot certificates 2>/dev/null || echo "   No certificates or permission denied"
else
    echo "❌ Certbot not installed"
fi

echo ""

# Generate nginx configuration data
echo "📋 NGINX CONFIGURATION DATA"
echo "==========================="
echo "Based on the analysis above, here's the data for nginx configuration:"
echo ""
echo "PROJECT_ROOT=$PROJECT_DIR"
echo "STATIC_ROOT=$STATIC_ROOT"
echo "MEDIA_ROOT=$MEDIA_ROOT"
echo "USER=$(whoami)"
echo "GROUP=$(id -gn)"
echo ""

# System resource check
echo "💻 SYSTEM RESOURCES"
echo "=================="
echo "Disk usage:"
df -h "$PROJECT_DIR" 2>/dev/null || df -h /
echo ""
echo "Memory usage:"
free -h
echo ""
echo "CPU info:"
nproc
echo ""

echo "🎯 DIAGNOSTIC COMPLETE"
echo "====================="
echo "Next steps:"
echo "1. Review the missing files and fix paths"
echo "2. Run 'python manage.py collectstatic' if staticfiles missing"
echo "3. Create missing media files or update templates"
echo "4. Use the configuration data above to generate nginx config"