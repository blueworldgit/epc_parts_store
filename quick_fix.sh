#!/bin/bash
# Quick fix script for common Django/media file issues
# Run this after the diagnostic script

PROJECT_DIR="/home/maxis/epc_parts_store/epcdata"

echo "🛠️ QUICK FIXES FOR VANPARTS-DIRECT.CO.UK"
echo "========================================"

# Ensure we're in the right directory
cd "$PROJECT_DIR" || exit 1

# 1. Create missing directories
echo "📁 Creating missing directories..."
mkdir -p media/images
mkdir -p staticfiles
mkdir -p logs
echo "✅ Directories created"

# 2. Create placeholder files for 404 errors
echo "📄 Creating placeholder files..."

# Placeholder CSS
cat > media/header-styles-parent-fixed.css << 'EOF'
/* Placeholder header styles for vanparts-direct.co.uk */
/* Replace this with your actual header styles */

.header-container {
    background-color: #f8f9fa;
    padding: 15px 0;
    border-bottom: 1px solid #dee2e6;
}

.header-logo {
    font-size: 24px;
    font-weight: bold;
    color: #333;
}

.header-nav {
    margin-top: 10px;
}

.header-nav a {
    margin-right: 20px;
    text-decoration: none;
    color: #007bff;
}

.header-nav a:hover {
    text-decoration: underline;
}

/* Add your actual header styles here */
EOF

# Create a simple 1x1 pixel image as placeholder (using ImageMagick if available)
if command -v convert >/dev/null 2>&1; then
    convert -size 1200x300 xc:lightblue -fill navy -pointsize 72 -gravity center \
            -annotate +0+0 "Van Interior\nPlaceholder" media/images/breadcrumb-van-interior.jpg
    echo "✅ Created breadcrumb image with ImageMagick"
else
    # Create a simple text file as placeholder if ImageMagick not available
    echo "This is a placeholder for breadcrumb-van-interior.jpg" > media/images/breadcrumb-van-interior.jpg
    echo "✅ Created text placeholder (install ImageMagick for proper image)"
fi

# 3. Set proper permissions
echo "🔐 Setting file permissions..."
chown -R $(whoami):$(whoami) media/
chmod -R 644 media/
chmod 755 media/ media/images/
echo "✅ Permissions set"

# 4. Collect static files
echo "📦 Collecting static files..."
if [ -d "env/bin" ]; then
    export DJANGO_ENV=production
    ./env/bin/python manage.py collectstatic --noinput
    echo "✅ Static files collected"
else
    echo "❌ Virtual environment not found, skipping collectstatic"
fi

# 5. Test Django configuration
echo "🧪 Testing Django configuration..."
if [ -d "env/bin" ]; then
    export DJANGO_ENV=production
    ./env/bin/python manage.py check --deploy
    echo "✅ Django check completed"
else
    echo "❌ Skipping Django check (no virtual environment)"
fi

echo ""
echo "🎉 Quick fixes completed!"
echo "You can now run the server with:"
echo "cd $PROJECT_DIR"
echo "export DJANGO_ENV=production"
echo "./env/bin/python manage.py runserver 0.0.0.0:8000"