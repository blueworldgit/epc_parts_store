#!/bin/bash
# Force Load Original Motor Template Assets Script
# This script forces Django to load the correct original motor template files

echo "🎯 Force Loading Original Motor Template Assets..."
echo "================================================="

cd /home/maxis/epc_parts_store/epcdata

# Step 1: Clear all static files and force fresh collection
echo "🧹 Step 1: Clearing all static files..."
rm -rf staticfiles/*
echo "✅ Cleared staticfiles directory"

# Step 2: Force collect static files to get original assets
echo "📊 Step 2: Force collecting static files from original sources..."
python manage.py collectstatic --noinput --clear --verbosity=2

# Step 3: Check what was actually collected
echo "🔍 Step 3: Verifying collected static files..."
echo "Bootstrap CSS location:"
find staticfiles/ -name "bootstrap.min.css" -type f

echo ""
echo "Main style CSS location:"
find staticfiles/ -name "style.css" -type f

echo ""
echo "Motor template structure:"
if [ -d "staticfiles/uren" ]; then
    echo "✅ staticfiles/uren/ exists"
    ls -la staticfiles/uren/assets/css/vendor/ 2>/dev/null || echo "❌ No vendor CSS files"
else
    echo "❌ staticfiles/uren/ missing"
fi

if [ -d "staticfiles/motortemplate" ]; then
    echo "✅ staticfiles/motortemplate/ exists"
    ls -la staticfiles/motortemplate/uren/assets/css/vendor/ 2>/dev/null || echo "❌ No motortemplate vendor CSS"
else
    echo "❌ staticfiles/motortemplate/ missing"
fi

# Step 4: Test which path actually works
echo ""
echo "🧪 Step 4: Testing static file URLs..."
echo "Testing /static/uren/assets/css/vendor/bootstrap.min.css:"
curl -I http://vanparts-direct.co.uk/static/uren/assets/css/vendor/bootstrap.min.css 2>/dev/null | head -1

echo "Testing /static/motortemplate/uren/assets/css/vendor/bootstrap.min.css:"
curl -I http://vanparts-direct.co.uk/static/motortemplate/uren/assets/css/vendor/bootstrap.min.css 2>/dev/null | head -1

# Step 5: Check template static references
echo ""
echo "🔍 Step 5: Checking template static file references..."
echo "Current template references:"
grep -n "{% static" templates/oscar/storefront_base.html | head -10

# Step 6: Fix file permissions
echo ""
echo "🔧 Step 6: Fixing file permissions..."
sudo chown -R www-data:www-data staticfiles/
sudo chmod -R 755 staticfiles/

# Step 7: Clear browser cache by adding version parameter
echo ""
echo "🔄 Step 7: Force browser cache refresh..."
echo "Adding cache-busting parameter to CSS files..."

# Create a timestamp for cache busting
TIMESTAMP=$(date +%s)

# Test final result
echo ""
echo "🧪 Final Test: Testing with cache-bust parameter..."
echo "Bootstrap with cache-bust: http://vanparts-direct.co.uk/static/uren/assets/css/vendor/bootstrap.min.css?v=$TIMESTAMP"
curl -I "http://vanparts-direct.co.uk/static/uren/assets/css/vendor/bootstrap.min.css?v=$TIMESTAMP" 2>/dev/null | head -1

echo ""
echo "✅ Force load complete!"
echo ""
echo "📋 Summary of static file locations found:"
find staticfiles/ -name "*.css" | grep -E "(bootstrap|style)" | head -10
echo ""
echo "🌐 Test your site now: http://vanparts-direct.co.uk/"
echo "   The original motor template styling should now load correctly!"
echo ""
echo "💡 If still showing placeholders, try hard refresh: Ctrl+F5"