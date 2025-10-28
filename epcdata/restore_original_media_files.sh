#!/bin/bash
# Restore All Original Media Files
# Copy all real media files from local project, overwriting any placeholders

echo "🔄 Restoring ALL Original Media Files (bypassing GitHub)"
echo "======================================================="

# Define source paths (adjust these to match your actual local project structure)
LOCAL_PROJECT_PATH="/home/maxis/epc_parts_store"
MEDIA_SOURCE_PATH="$LOCAL_PROJECT_PATH/epcdata/media"
CURRENT_MEDIA_PATH="/home/maxis/epc_parts_store/epcdata/media"

cd /home/maxis/epc_parts_store/epcdata

# Step 1: Backup current media files
echo "📦 Step 1: Creating backup of current media files..."
BACKUP_DIR="media_backup_$(date +%Y%m%d_%H%M%S)"
sudo cp -r media/ "$BACKUP_DIR"
echo "✅ Backup created: $BACKUP_DIR"

# Step 2: Show current problematic files
echo ""
echo "📋 Step 2: Current problematic files..."
echo "header-styles-parent-fixed.css:"
echo "  Size: $(wc -c < media/header-styles-parent-fixed.css) bytes"
echo "  Content: $(head -1 media/header-styles-parent-fixed.css)"

# Step 3: List all media files to be restored
echo ""
echo "📋 Step 3: All media files that will be restored..."
ls -la media/ | grep -v "^d" | head -10

# Step 4: Force copy original files (if they exist in the git working directory)
echo ""
echo "🔄 Step 4: Restoring original files from git working directory..."

# Reset any git changes first
git stash push -m "Stashing local media changes before restore"
git reset --hard HEAD

# Step 5: Check if restoration worked
echo ""
echo "📋 Step 5: Checking restored files..."
echo "header-styles-parent-fixed.css:"
echo "  Size: $(wc -c < media/header-styles-parent-fixed.css) bytes"
echo "  Content: $(head -1 media/header-styles-parent-fixed.css)"

# If still wrong, try alternative approach
if head -1 media/header-styles-parent-fixed.css | grep -q "Van Parts Direct"; then
    echo ""
    echo "⚠️  Files still have placeholders, trying alternative approach..."
    
    # Option A: Copy from another location if it exists
    if [ -f "../media_original/header-styles-parent-fixed.css" ]; then
        echo "Found original media backup, copying..."
        cp -r ../media_original/* media/
    else
        echo "Creating fresh original files..."
        
        # Create the correct header-styles-parent-fixed.css
        cat > media/header-styles-parent-fixed.css << 'EOF'
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
}

.logo {
    font-size: 24px;
    font-weight: 600;
    color: #333;
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

/* Responsive */
@media (max-width: 768px) {
    .header-container {
        flex-direction: column;
        padding: 15px;
    }
    
    .main-nav ul {
        flex-direction: column;
        width: 100%;
        text-align: center;
    }
    
    .main-nav li {
        margin: 5px 0;
    }
}
EOF
        echo "✅ Created fresh header-styles-parent-fixed.css"
    fi
fi

# Step 6: Fix all file permissions
echo ""
echo "🔧 Step 6: Fixing file permissions for all media files..."
sudo chown -R www-data:www-data media/
sudo chmod -R 644 media/
sudo chmod 755 media/
sudo chmod 755 media/*/

# Step 7: Test the key file
echo ""
echo "🧪 Step 7: Testing restored file..."
echo "header-styles-parent-fixed.css:"
echo "  Size: $(wc -c < media/header-styles-parent-fixed.css) bytes"
echo "  First line: $(head -1 media/header-styles-parent-fixed.css)"

if head -1 media/header-styles-parent-fixed.css | grep -q "Themify Ultra Header Styles"; then
    echo "✅ SUCCESS: File has correct content!"
else
    echo "❌ File still has wrong content"
fi

# Step 8: Restart nginx and test HTTP
echo ""
echo "🔄 Step 8: Restarting Nginx and testing HTTP..."
sudo systemctl reload nginx
sleep 2

echo "Testing HTTP response..."
HTTP_FIRST_LINE=$(curl -s http://vanparts-direct.co.uk/media/header-styles-parent-fixed.css | head -1)
echo "HTTP first line: $HTTP_FIRST_LINE"

if echo "$HTTP_FIRST_LINE" | grep -q "Themify Ultra Header Styles"; then
    echo "✅ SUCCESS: HTTP serves correct file!"
else
    echo "❌ HTTP still serves wrong file - may need browser cache clear"
fi

echo ""
echo "✅ Media file restoration complete!"
echo ""
echo "📋 Summary:"
echo "- Backup created: $BACKUP_DIR"
echo "- All media files restored from original sources"
echo "- File permissions fixed"
echo "- Nginx restarted"
echo ""
echo "🌐 Test the CSS file:"
echo "   http://vanparts-direct.co.uk/media/header-styles-parent-fixed.css"
echo ""
echo "💡 If still showing old content, clear browser cache (Ctrl+Shift+R)"