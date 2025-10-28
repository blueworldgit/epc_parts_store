#!/bin/bash
# Simple Direct Fix for header-styles-parent-fixed.css
# Use sudo to overwrite the file directly

echo "🎯 Simple Direct Fix: header-styles-parent-fixed.css"
echo "=================================================="

cd /home/maxis/epc_parts_store/epcdata

# Step 1: Show current wrong file
echo "📋 Current WRONG file:"
echo "Size: $(wc -c < media/header-styles-parent-fixed.css) bytes"
echo "Content: $(head -1 media/header-styles-parent-fixed.css)"

# Step 2: Use sudo to directly overwrite the file with correct content
echo ""
echo "🔄 Creating correct file with sudo..."
sudo tee media/header-styles-parent-fixed.css > /dev/null << 'EOF'
/* Themify Ultra Header Styles - Matching Parent Site */

/* Reset */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

/* Base Typography matching parent site */
body {
    font-family: 'Poppins', 'Public Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    font-size: 14px;
    line-height: 1.6;
    color: #333;
    background-color: #fff;
}

/* Themify utility classes from parent site */
.tf_box {
    box-sizing: border-box;
}

.tf_clearfix::after {
    content: "";
    display: table;
    clear: both;
}

.tf_clear {
    clear: both;
}

.tf_hide {
    display: none !important;
}

.tf_inline_b {
    display: inline-block;
}

.tf_vmiddle {
    vertical-align: middle;
}

.tf_overflow {
    overflow: hidden;
}

/* Header Styles */
.site-header {
    background: #fff;
    border-bottom: 1px solid #e1e1e1;
    padding: 10px 0;
}

.header-container {
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 15px;
}

.logo {
    font-size: 24px;
    font-weight: 600;
    color: #333;
    text-decoration: none;
}

.main-nav ul {
    display: flex;
    list-style: none;
    margin: 0;
    padding: 0;
}

.main-nav li {
    margin: 0 20px;
}

.main-nav a {
    color: #333;
    text-decoration: none;
    font-weight: 500;
    padding: 10px 0;
    transition: color 0.3s ease;
}

.main-nav a:hover {
    color: #007cba;
}

/* Van Parts Specific Styles */
.van-parts-header {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.parts-search {
    max-width: 400px;
    width: 100%;
    margin: 0 20px;
}

.parts-search input {
    width: 100%;
    padding: 10px 15px;
    border: 1px solid #ddd;
    border-radius: 25px;
    font-size: 14px;
}

.cart-icon {
    position: relative;
    color: #333;
    font-size: 20px;
}

.cart-count {
    position: absolute;
    top: -8px;
    right: -8px;
    background: #e74c3c;
    color: white;
    border-radius: 50%;
    width: 18px;
    height: 18px;
    font-size: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
}

/* Responsive Design */
@media (max-width: 768px) {
    .header-container {
        flex-direction: column;
        padding: 15px;
    }
    
    .main-nav ul {
        flex-direction: column;
        width: 100%;
        text-align: center;
        margin-top: 15px;
    }
    
    .main-nav li {
        margin: 5px 0;
    }
    
    .parts-search {
        margin: 15px 0;
        max-width: 100%;
    }
}

/* Category Navigation */
.category-nav {
    background: #2c3e50;
    padding: 0;
}

.category-nav ul {
    display: flex;
    list-style: none;
    margin: 0;
    padding: 0;
    max-width: 1200px;
    margin: 0 auto;
}

.category-nav li {
    flex: 1;
}

.category-nav a {
    display: block;
    color: white;
    text-decoration: none;
    padding: 15px 20px;
    text-align: center;
    transition: background-color 0.3s ease;
}

.category-nav a:hover {
    background-color: #34495e;
}

/* Breadcrumb */
.breadcrumb {
    background: #ecf0f1;
    padding: 10px 0;
}

.breadcrumb-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 15px;
}

.breadcrumb ol {
    display: flex;
    list-style: none;
    margin: 0;
    padding: 0;
}

.breadcrumb li {
    margin-right: 10px;
}

.breadcrumb li:after {
    content: "/";
    margin-left: 10px;
    color: #7f8c8d;
}

.breadcrumb li:last-child:after {
    display: none;
}

.breadcrumb a {
    color: #3498db;
    text-decoration: none;
}

.breadcrumb a:hover {
    text-decoration: underline;
}
EOF

echo "✅ File created with sudo"

# Step 3: Set correct permissions
echo ""
echo "🔧 Setting correct permissions..."
sudo chown www-data:www-data media/header-styles-parent-fixed.css
sudo chmod 644 media/header-styles-parent-fixed.css

# Step 4: Verify the fix
echo ""
echo "🧪 Verifying the fix..."
echo "New size: $(wc -c < media/header-styles-parent-fixed.css) bytes"
echo "New content: $(head -1 media/header-styles-parent-fixed.css)"

if head -1 media/header-styles-parent-fixed.css | grep -q "Themify Ultra Header Styles"; then
    echo "✅ SUCCESS: File now has correct content!"
else
    echo "❌ FAILED: File content still wrong"
fi

# Step 5: Test HTTP response
echo ""
echo "🌐 Testing HTTP response..."
sudo systemctl reload nginx
sleep 2

HTTP_RESPONSE=$(curl -s "http://vanparts-direct.co.uk/media/header-styles-parent-fixed.css?v=$(date +%s)" | head -1)
echo "HTTP first line: $HTTP_RESPONSE"

if echo "$HTTP_RESPONSE" | grep -q "Themify Ultra Header Styles"; then
    echo "✅ SUCCESS: HTTP serves correct file!"
else
    echo "⚠️ HTTP may still serve cached version - try hard refresh in browser"
fi

echo ""
echo "✅ Simple fix complete!"
echo ""
echo "📋 Final Status:"
echo "- File size: $(wc -c < media/header-styles-parent-fixed.css) bytes"
echo "- File owner: $(ls -la media/header-styles-parent-fixed.css | awk '{print $3, $4}')"
echo "- Content starts with: $(head -1 media/header-styles-parent-fixed.css)"
echo ""
echo "🌐 Test URL: http://vanparts-direct.co.uk/media/header-styles-parent-fixed.css"
echo "💡 Use Ctrl+Shift+R to force refresh if still showing old content"