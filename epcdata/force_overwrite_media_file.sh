#!/bin/bash
# Force Overwrite Media File with Correct Version
# This will replace the placeholder with the real CSS file

echo "🔄 Force Overwriting header-styles-parent-fixed.css with correct version"
echo "======================================================================="

cd /home/maxis/epc_parts_store/epcdata

# Step 1: Show current wrong file
echo "📋 Step 1: Current WRONG file on server..."
echo "File size: $(wc -c < media/header-styles-parent-fixed.css) bytes"
echo "Content (first 3 lines):"
head -3 media/header-styles-parent-fixed.css
echo "Last modified: $(stat -c %y media/header-styles-parent-fixed.css)"

# Step 2: Force git to overwrite local changes
echo ""
echo "🔄 Step 2: Force git to overwrite the file..."
git checkout HEAD -- media/header-styles-parent-fixed.css
echo "✅ Git checkout completed"

# Step 3: Check if file changed
echo ""
echo "📋 Step 3: File after git checkout..."
echo "File size: $(wc -c < media/header-styles-parent-fixed.css) bytes"
echo "Content (first 3 lines):"
head -3 media/header-styles-parent-fixed.css
echo "Last modified: $(stat -c %y media/header-styles-parent-fixed.css)"

# Step 4: If still wrong, force pull and reset
if head -1 media/header-styles-parent-fixed.css | grep -q "Van Parts Direct"; then
    echo ""
    echo "⚠️  File still wrong, doing hard reset..."
    git fetch origin newservervans
    git reset --hard origin/newservervans
    echo "✅ Hard reset completed"
    
    echo ""
    echo "📋 File after hard reset..."
    echo "File size: $(wc -c < media/header-styles-parent-fixed.css) bytes"
    echo "Content (first 3 lines):"
    head -3 media/header-styles-parent-fixed.css
fi

# Step 5: Fix permissions
echo ""
echo "🔧 Step 5: Fixing file permissions..."
sudo chown www-data:www-data media/header-styles-parent-fixed.css
sudo chmod 644 media/header-styles-parent-fixed.css

# Step 6: Test the correct file content
echo ""
echo "🧪 Step 6: Testing file content..."
FIRST_LINE=$(head -1 media/header-styles-parent-fixed.css)
if echo "$FIRST_LINE" | grep -q "Themify Ultra Header Styles"; then
    echo "✅ SUCCESS: File now has correct content!"
    echo "✅ File starts with: $FIRST_LINE"
    echo "✅ File size: $(wc -c < media/header-styles-parent-fixed.css) bytes"
else
    echo "❌ FAILED: File still has wrong content"
    echo "❌ File starts with: $FIRST_LINE"
fi

# Step 7: Test HTTP response
echo ""
echo "🌐 Step 7: Testing HTTP response..."
echo "Testing: http://vanparts-direct.co.uk/media/header-styles-parent-fixed.css"
HTTP_RESPONSE=$(curl -s http://vanparts-direct.co.uk/media/header-styles-parent-fixed.css | head -1)
echo "HTTP response first line: $HTTP_RESPONSE"

if echo "$HTTP_RESPONSE" | grep -q "Themify Ultra Header Styles"; then
    echo "✅ SUCCESS: HTTP serves correct file!"
else
    echo "❌ HTTP still serves wrong file"
    echo "🔄 Restarting Nginx..."
    sudo systemctl reload nginx
    sleep 2
    HTTP_RESPONSE2=$(curl -s http://vanparts-direct.co.uk/media/header-styles-parent-fixed.css | head -1)
    echo "HTTP response after reload: $HTTP_RESPONSE2"
fi

echo ""
echo "✅ Force overwrite complete!"
echo ""
echo "📋 Final Status:"
echo "- Local file: $(wc -c < media/header-styles-parent-fixed.css) bytes"
echo "- Should start with: 'Themify Ultra Header Styles'"
echo "- Test URL: http://vanparts-direct.co.uk/media/header-styles-parent-fixed.css"