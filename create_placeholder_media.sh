#!/bin/bash
# Create placeholder media files to stop 404 errors

PROJECT_DIR="/home/maxis/epc_parts_store/epcdata"
MEDIA_DIR="$PROJECT_DIR/media"

echo "🛠️ Creating placeholder media files..."

# Create directories
mkdir -p "$MEDIA_DIR/images"

# Create placeholder CSS file
cat > "$MEDIA_DIR/header-styles-parent-fixed.css" << 'EOF'
/* Placeholder CSS file for vanparts-direct.co.uk */
/* This file was automatically generated to prevent 404 errors */

.header-placeholder {
    /* Add your header styles here */
    background-color: #f8f9fa;
    padding: 10px;
    border-bottom: 1px solid #dee2e6;
}

/* Add more styles as needed */
EOF

# Create a simple placeholder image (1x1 pixel transparent PNG)
# This creates a base64 encoded 1x1 transparent PNG
echo "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAFJNhR7mQAAAABJRU5ErkJggg==" | base64 -d > "$MEDIA_DIR/images/breadcrumb-van-interior.jpg"

echo "✅ Created placeholder files:"
echo "   - $MEDIA_DIR/header-styles-parent-fixed.css"
echo "   - $MEDIA_DIR/images/breadcrumb-van-interior.jpg"

echo ""
echo "🔧 Next steps:"
echo "1. Replace placeholder files with actual content"
echo "2. Check where these files are referenced in templates"
echo "3. Consider moving CSS to static files instead of media"

# Set proper permissions
chmod 644 "$MEDIA_DIR/header-styles-parent-fixed.css"
chmod 644 "$MEDIA_DIR/images/breadcrumb-van-interior.jpg"

echo "✅ Set file permissions"