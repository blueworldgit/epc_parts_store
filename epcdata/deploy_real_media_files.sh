#!/bin/bash
# Deploy Real Media and Static Files Script
# This script removes temporary test files and ensures proper Django static/media files are served

echo "🚀 Deploying real Django media and static files..."
echo "=================================================="

# Navigate to project directory
cd /home/maxis/epc_parts_store/epcdata

# Remove temporary test files we created during debugging
echo "🧹 Cleaning up temporary test files..."
rm -f media/header-styles-parent-fixed.css.bak
rm -f media/breadcrumb-van-interior.jpg.bak
echo "✅ Temporary files cleaned up"

# Pull latest changes from repository
echo "📥 Pulling latest code changes..."
git pull origin newservervans

# Activate virtual environment
echo "📦 Activating virtual environment..."
source ../env/bin/activate

# Collect static files (this ensures all CSS, JS, images from apps are collected)
echo "📊 Collecting static files..."
python manage.py collectstatic --noinput --clear

# Check that key files exist
echo "🔍 Verifying static files..."
echo "Bootstrap CSS: $(ls -la staticfiles/uren/assets/css/vendor/bootstrap.min.css 2>/dev/null || echo 'MISSING')"
echo "Oscar CSS: $(ls -la staticfiles/oscar/css/ 2>/dev/null | wc -l) files"
echo "Motor template: $(ls -la staticfiles/motortemplate/ 2>/dev/null | wc -l) files"

echo "🔍 Verifying media files..."
echo "Media directory contents:"
ls -la media/ | head -10

# Test Django media serving
echo "🧪 Testing Django media file serving..."
if python manage.py shell -c "
from django.test.client import Client
c = Client()
response = c.get('/media/header-styles-parent-fixed.css')
print(f'Django media response: {response.status_code}')
if response.status_code == 200:
    print('✅ Django can serve media files')
else:
    print('❌ Django cannot serve media files')
"; then
    echo "Django test completed"
fi

# Fix file permissions for Nginx
echo "🔧 Fixing file permissions for Nginx..."
sudo chown -R www-data:www-data media/
sudo chmod -R 755 media/
sudo chown -R www-data:www-data staticfiles/
sudo chmod -R 755 staticfiles/

# Test actual file access
echo "🧪 Testing file access..."
echo "Testing real CSS file:"
curl -I http://vanparts-direct.co.uk/media/header-styles-parent-fixed.css

echo "Testing static Bootstrap CSS:"
curl -I http://vanparts-direct.co.uk/static/uren/assets/css/vendor/bootstrap.min.css

echo "Testing Oscar static files:"
curl -I http://vanparts-direct.co.uk/static/oscar/css/oscar.css

# Restart services
echo "🔄 Restarting services..."
sudo systemctl reload nginx
sudo systemctl status nginx | head -5

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📋 Summary:"
echo "- Real Django static files collected and served from /static/"
echo "- Real Django media files served from /media/"
echo "- File permissions fixed for Nginx"
echo "- Services restarted"
echo ""
echo "🧪 Test URLs:"
echo "- Main site: http://vanparts-direct.co.uk/"
echo "- Catalogue: http://vanparts-direct.co.uk/catalogue/"
echo "- Media file: http://vanparts-direct.co.uk/media/header-styles-parent-fixed.css"
echo "- Static file: http://vanparts-direct.co.uk/static/uren/assets/css/vendor/bootstrap.min.css"