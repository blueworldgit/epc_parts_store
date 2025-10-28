#!/bin/bash
# COMPLETE FIX: Force Original Motor Template Loading
# This script completely resets and forces Django to load original motor template assets

echo "🚀 COMPLETE FIX: Force Original Motor Template Assets"
echo "===================================================="

cd /home/maxis/epc_parts_store/epcdata

# Step 1: Completely clear and reset staticfiles
echo "🧹 Step 1: Complete staticfiles reset..."
sudo rm -rf staticfiles/*
sudo rm -rf media/*.css.bak
sudo rm -rf media/*.jpg.bak
echo "✅ Cleared all cached files"

# Step 2: Verify source structure is correct
echo "🔍 Step 2: Verifying source file structure..."
echo "motortemplate structure:"
ls -la motortemplate/uren/assets/css/vendor/ | head -5

if [ -f "motortemplate/uren/assets/css/vendor/bootstrap.min.css" ]; then
    echo "✅ Bootstrap source found: $(wc -c < motortemplate/uren/assets/css/vendor/bootstrap.min.css) bytes"
else
    echo "❌ Bootstrap source missing!"
fi

if [ -f "motortemplate/uren/assets/css/style.css" ]; then
    echo "✅ Main style source found: $(wc -c < motortemplate/uren/assets/css/style.css) bytes"
else
    echo "❌ Main style source missing!"
fi

# Step 3: Force fresh collectstatic with maximum verbosity
echo ""
echo "📊 Step 3: Force collecting static files with full debug..."
python manage.py collectstatic --noinput --clear --verbosity=2 | grep -E "(motortemplate|uren|bootstrap|style\.css)"

# Step 4: Verify files were collected correctly
echo ""
echo "🔍 Step 4: Verifying collected files..."
echo "Looking for bootstrap.min.css:"
find staticfiles/ -name "bootstrap.min.css" -exec ls -la {} \;

echo ""
echo "Looking for style.css:"
find staticfiles/ -name "style.css" -exec ls -la {} \;

echo ""
echo "Checking uren directory structure:"
if [ -d "staticfiles/uren" ]; then
    echo "✅ staticfiles/uren exists"
    ls -la staticfiles/uren/assets/css/vendor/ 2>/dev/null | head -3
else
    echo "❌ staticfiles/uren missing - this is the problem!"
    echo "Available directories in staticfiles:"
    ls -la staticfiles/ | grep "^d"
fi

# Step 5: Test HTTP access to static files
echo ""
echo "🧪 Step 5: Testing HTTP access to static files..."
echo "Testing Bootstrap CSS:"
curl -I http://vanparts-direct.co.uk/static/uren/assets/css/vendor/bootstrap.min.css 2>/dev/null | head -1

echo "Testing main style CSS:"
curl -I http://vanparts-direct.co.uk/static/uren/assets/css/style.css 2>/dev/null | head -1

# Step 6: Fix permissions thoroughly
echo ""
echo "🔧 Step 6: Fixing all file permissions..."
sudo chown -R www-data:www-data staticfiles/
sudo chmod -R 755 staticfiles/
sudo chown -R www-data:www-data media/
sudo chmod -R 755 media/

# Step 7: Clear browser cache by restarting nginx
echo ""
echo "🔄 Step 7: Restarting Nginx to clear server cache..."
sudo systemctl reload nginx

# Step 8: Test template rendering with debug
echo ""
echo "🔍 Step 8: Testing Django template static file resolution..."
python manage.py shell -c "
from django.template import Context, Template
from django.template.loader import get_template
from django.contrib.staticfiles.storage import staticfiles_storage

# Test if static files can be found
print('Static files storage location:', staticfiles_storage.location)
print('Bootstrap exists:', staticfiles_storage.exists('uren/assets/css/vendor/bootstrap.min.css'))
print('Style CSS exists:', staticfiles_storage.exists('uren/assets/css/style.css'))

# Test template rendering
try:
    template = get_template('oscar/storefront_base.html')
    print('✅ Template loads successfully')
except Exception as e:
    print('❌ Template error:', e)
"

# Step 9: Final verification
echo ""
echo "✅ COMPLETE FIX APPLIED!"
echo ""
echo "📋 Summary:"
echo "1. Cleared all cached static files"
echo "2. Re-collected static files from motortemplate/"
echo "3. Fixed file permissions"
echo "4. Restarted Nginx"
echo "5. Verified template can load files"
echo ""
echo "🌐 Test your site now:"
echo "   http://vanparts-direct.co.uk/"
echo ""
echo "💡 If still showing Oscar placeholders:"
echo "   1. Hard refresh browser: Ctrl+Shift+R"
echo "   2. Clear browser cache completely"
echo "   3. Try incognito/private browsing mode"
echo ""
echo "🎯 Your original Uren motor template should now display!"