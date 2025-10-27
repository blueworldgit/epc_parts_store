#!/bin/bash
# Script to check media files and directories on the server
# Run this on your VPS server

echo "🔍 Checking media file structure..."

PROJECT_DIR="/home/maxis/epc_parts_store/epcdata"

echo "📁 PROJECT_DIR: $PROJECT_DIR"
echo "📁 MEDIA_ROOT should be: $PROJECT_DIR/media"

# Check if media directory exists
if [ -d "$PROJECT_DIR/media" ]; then
    echo "✅ Media directory exists"
    echo "📂 Contents of media directory:"
    ls -la "$PROJECT_DIR/media/"
    
    # Check for specific missing files
    echo ""
    echo "🔍 Checking for specific missing files:"
    
    if [ -f "$PROJECT_DIR/media/header-styles-parent-fixed.css" ]; then
        echo "✅ header-styles-parent-fixed.css exists"
    else
        echo "❌ header-styles-parent-fixed.css missing"
    fi
    
    if [ -d "$PROJECT_DIR/media/images" ]; then
        echo "✅ images directory exists"
        if [ -f "$PROJECT_DIR/media/images/breadcrumb-van-interior.jpg" ]; then
            echo "✅ breadcrumb-van-interior.jpg exists"
        else
            echo "❌ breadcrumb-van-interior.jpg missing"
        fi
    else
        echo "❌ images directory missing"
    fi
    
else
    echo "❌ Media directory does not exist, creating it..."
    mkdir -p "$PROJECT_DIR/media"
    mkdir -p "$PROJECT_DIR/media/images"
    echo "✅ Created media directories"
fi

# Check static files too
echo ""
echo "📁 Checking static files..."
if [ -d "$PROJECT_DIR/staticfiles" ]; then
    echo "✅ staticfiles directory exists"
else
    echo "❌ staticfiles directory missing - you may need to run 'python manage.py collectstatic'"
fi

# Check motortemplate directory
echo ""
echo "📁 Checking motortemplate directory..."
if [ -d "$PROJECT_DIR/motortemplate" ]; then
    echo "✅ motortemplate directory exists"
    echo "📂 Contents:"
    find "$PROJECT_DIR/motortemplate" -name "*.css" -o -name "*.jpg" -o -name "*.png" | head -10
else
    echo "❌ motortemplate directory missing"
fi

echo ""
echo "🔧 To fix missing media files, you can:"
echo "1. Copy files from your local development to server"
echo "2. Create placeholder files for testing"
echo "3. Update templates to use correct paths"