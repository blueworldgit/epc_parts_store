#!/bin/bash
# Fix Single Media File: header-styles-parent-fixed.css
# Focus on getting the correct CSS file loaded instead of placeholder

echo "🎯 Fixing Single Media File: header-styles-parent-fixed.css"
echo "=========================================================="

cd /home/maxis/epc_parts_store/epcdata

# Step 1: Check current file status
echo "📋 Step 1: Current file status..."
if [ -f "media/header-styles-parent-fixed.css" ]; then
    echo "✅ File exists: $(wc -c < media/header-styles-parent-fixed.css) bytes"
    echo "First few lines of current file:"
    head -3 media/header-styles-parent-fixed.css
else
    echo "❌ File missing!"
fi

# Step 2: Test current HTTP response 
echo ""
echo "🧪 Step 2: Testing current HTTP response..."
echo "Testing: http://vanparts-direct.co.uk/media/header-styles-parent-fixed.css"
RESPONSE=$(curl -I http://vanparts-direct.co.uk/media/header-styles-parent-fixed.css 2>/dev/null)
echo "$RESPONSE" | head -3

HTTP_STATUS=$(echo "$RESPONSE" | head -1 | grep -o "200\|404\|403\|500")
CONTENT_LENGTH=$(echo "$RESPONSE" | grep -i "content-length" | cut -d' ' -f2 | tr -d '\r')

echo "HTTP Status: $HTTP_STATUS"
echo "Content Length: $CONTENT_LENGTH bytes"

# Step 3: Pull latest version from repository
echo ""
echo "📥 Step 3: Pulling latest version from repository..."
git pull origin newservervans

# Step 4: Check if file changed after pull
echo ""
echo "📋 Step 4: File status after git pull..."
if [ -f "media/header-styles-parent-fixed.css" ]; then
    NEW_SIZE=$(wc -c < media/header-styles-parent-fixed.css)
    echo "✅ File size now: $NEW_SIZE bytes"
    echo "File modified: $(stat -c %y media/header-styles-parent-fixed.css)"
else
    echo "❌ File still missing after pull!"
fi

# Step 5: Fix file permissions specifically for this file
echo ""
echo "🔧 Step 5: Fixing file permissions..."
sudo chown www-data:www-data media/header-styles-parent-fixed.css
sudo chmod 644 media/header-styles-parent-fixed.css
echo "File permissions:"
ls -la media/header-styles-parent-fixed.css

# Step 6: Test HTTP response again
echo ""
echo "🧪 Step 6: Testing HTTP response after fixes..."
echo "Testing: http://vanparts-direct.co.uk/media/header-styles-parent-fixed.css"
RESPONSE2=$(curl -I http://vanparts-direct.co.uk/media/header-styles-parent-fixed.css 2>/dev/null)
echo "$RESPONSE2" | head -3

HTTP_STATUS2=$(echo "$RESPONSE2" | head -1 | grep -o "200\|404\|403\|500")
CONTENT_LENGTH2=$(echo "$RESPONSE2" | grep -i "content-length" | cut -d' ' -f2 | tr -d '\r')

echo "HTTP Status: $HTTP_STATUS2"
echo "Content Length: $CONTENT_LENGTH2 bytes"

# Step 7: Test actual CSS content
echo ""
echo "🎨 Step 7: Testing actual CSS content..."
echo "First 3 lines of CSS via HTTP:"
curl -s http://vanparts-direct.co.uk/media/header-styles-parent-fixed.css 2>/dev/null | head -3

# Step 8: Clear any Nginx cache
echo ""
echo "🔄 Step 8: Clearing Nginx cache..."
sudo systemctl reload nginx

# Step 9: Final test with cache busting
echo ""
echo "🧪 Step 9: Final test with cache-busting parameter..."
TIMESTAMP=$(date +%s)
echo "Testing with cache-bust: http://vanparts-direct.co.uk/media/header-styles-parent-fixed.css?v=$TIMESTAMP"
curl -I "http://vanparts-direct.co.uk/media/header-styles-parent-fixed.css?v=$TIMESTAMP" 2>/dev/null | head -1

echo ""
echo "✅ Single file fix complete!"
echo ""
echo "📋 Summary:"
echo "- File size: $(wc -c < media/header-styles-parent-fixed.css 2>/dev/null || echo 'ERROR') bytes"
echo "- Permissions: $(ls -la media/header-styles-parent-fixed.css | awk '{print $1, $3, $4}')"
echo "- HTTP Status: $HTTP_STATUS2"
echo ""
echo "🌐 Test the CSS file directly:"
echo "   http://vanparts-direct.co.uk/media/header-styles-parent-fixed.css"
echo ""
echo "💡 If still showing wrong content, try:"
echo "   1. Hard refresh: Ctrl+Shift+R"
echo "   2. Clear browser cache"
echo "   3. Try incognito mode"