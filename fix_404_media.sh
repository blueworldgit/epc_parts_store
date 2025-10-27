#!/bin/bash
# Quick fix for the 404 media file errors
# Run this immediately to stop the 404 errors while testing on :8000

PROJECT_DIR="/home/maxis/epc_parts_store/epcdata"

echo "🛠️ QUICK FIX FOR MEDIA FILE 404 ERRORS"
echo "======================================"

cd "$PROJECT_DIR" || exit 1

# Create media directories
mkdir -p media/images

# Fix the missing CSS file
cat > media/header-styles-parent-fixed.css << 'EOF'
/* Van Parts Direct Header Styles */
/* Temporary placeholder to fix 404 error */

.site-header {
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    color: white;
    padding: 15px 0;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.header-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 15px;
}

.site-logo {
    font-size: 28px;
    font-weight: bold;
    color: white;
    text-decoration: none;
}

.main-navigation {
    margin-top: 15px;
}

.main-navigation a {
    color: #e8f4f8;
    text-decoration: none;
    margin-right: 25px;
    font-weight: 500;
    transition: color 0.3s ease;
}

.main-navigation a:hover {
    color: #ffffff;
}

/* Breadcrumb styling */
.breadcrumb-section {
    background: #f8f9fa;
    padding: 20px 0;
    border-bottom: 1px solid #dee2e6;
}

.breadcrumb {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 15px;
    font-size: 14px;
}

.breadcrumb a {
    color: #007bff;
    text-decoration: none;
}

.breadcrumb a:hover {
    text-decoration: underline;
}
EOF

# Create a simple placeholder image using base64 encoded 1x1 pixel
# This creates a small blue square that won't cause 404 errors
echo "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==" | base64 -d > media/images/breadcrumb-van-interior.jpg

# Set proper permissions
chmod 644 media/header-styles-parent-fixed.css
chmod 644 media/images/breadcrumb-van-interior.jpg
chown maxis:maxis media/header-styles-parent-fixed.css
chown maxis:maxis media/images/breadcrumb-van-interior.jpg

echo "✅ Created placeholder files:"
echo "   - media/header-styles-parent-fixed.css"
echo "   - media/images/breadcrumb-van-interior.jpg"

echo ""
echo "🔄 Now restart your Django server:"
echo "cd $PROJECT_DIR"
echo "export DJANGO_ENV=production"
echo "python manage.py runserver 0.0.0.0:8000"
echo ""
echo "The 404 errors for these files should now be resolved!"

# Verify files were created
echo ""
echo "📋 Verification:"
if [ -f "media/header-styles-parent-fixed.css" ]; then
    echo "✅ CSS file created ($(stat -c%s media/header-styles-parent-fixed.css) bytes)"
else
    echo "❌ CSS file creation failed"
fi

if [ -f "media/images/breadcrumb-van-interior.jpg" ]; then
    echo "✅ Image file created ($(stat -c%s media/images/breadcrumb-van-interior.jpg) bytes)"
else
    echo "❌ Image file creation failed"
fi