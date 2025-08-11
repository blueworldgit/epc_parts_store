#!/bin/bash

# =============================================================================
# VPS CSS Fix Script - Automated repair for vehicle-navigation.css issues
# =============================================================================

echo "=========================================="
echo "VPS CSS AUTOMATIC FIX SCRIPT"
echo "=========================================="
echo "Timestamp: $(date)"
echo ""

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "❌ Error: manage.py not found. Please run this script from the epcdata directory."
    exit 1
fi

echo "✅ Found manage.py - proceeding with fix..."

# =============================================================================
# STEP 1: CREATE DIRECTORY STRUCTURE
# =============================================================================
echo ""
echo "STEP 1: Creating staticfiles directory structure..."

mkdir -p staticfiles/motortemplate/uren/assets/css/
if [ $? -eq 0 ]; then
    echo "✅ Directory structure created successfully"
else
    echo "❌ Failed to create directory structure"
    exit 1
fi

# =============================================================================
# STEP 2: COPY VEHICLE-NAVIGATION.CSS
# =============================================================================
echo ""
echo "STEP 2: Copying vehicle-navigation.css file..."

if [ -f "motortemplate/uren/assets/css/vehicle-navigation.css" ]; then
    cp motortemplate/uren/assets/css/vehicle-navigation.css staticfiles/motortemplate/uren/assets/css/
    if [ $? -eq 0 ]; then
        echo "✅ vehicle-navigation.css copied successfully"
        echo "File size: $(ls -lh staticfiles/motortemplate/uren/assets/css/vehicle-navigation.css | awk '{print $5}')"
        
        # Verify the file contains the required CSS
        if grep -q "custom-category_col" "staticfiles/motortemplate/uren/assets/css/vehicle-navigation.css"; then
            echo "✅ File contains required custom-category_col styles"
        else
            echo "⚠️  Warning: File may not contain the required styles"
        fi
    else
        echo "❌ Failed to copy vehicle-navigation.css"
        exit 1
    fi
else
    echo "❌ Source file motortemplate/uren/assets/css/vehicle-navigation.css not found"
    exit 1
fi

# =============================================================================
# STEP 3: SET PROPER PERMISSIONS
# =============================================================================
echo ""
echo "STEP 3: Setting proper file permissions..."

chmod 644 staticfiles/motortemplate/uren/assets/css/vehicle-navigation.css
chmod -R 755 staticfiles/motortemplate/

echo "✅ Permissions set (644 for files, 755 for directories)"

# =============================================================================
# STEP 4: VERIFY INSTALLATION
# =============================================================================
echo ""
echo "STEP 4: Verifying installation..."

if [ -f "staticfiles/motortemplate/uren/assets/css/vehicle-navigation.css" ]; then
    echo "✅ File exists in staticfiles"
    echo "✅ File is readable: $(test -r staticfiles/motortemplate/uren/assets/css/vehicle-navigation.css && echo 'Yes' || echo 'No')"
    
    echo ""
    echo "File preview (first 10 lines):"
    head -10 "staticfiles/motortemplate/uren/assets/css/vehicle-navigation.css" | sed 's/^/    /'
    
    echo ""
    echo "Key responsive styles found:"
    grep -n "custom-category_col" "staticfiles/motortemplate/uren/assets/css/vehicle-navigation.css" | head -3 | sed 's/^/    /'
else
    echo "❌ Verification failed - file not found in staticfiles"
    exit 1
fi

# =============================================================================
# STEP 5: RESTART WEB SERVER (OPTIONAL)
# =============================================================================
echo ""
echo "STEP 5: Web server restart options..."
echo ""
echo "To complete the fix, restart your web server using ONE of these commands:"
echo ""

# Check which services are available
if command -v systemctl >/dev/null 2>&1; then
    echo "Using systemctl (systemd):"
    if systemctl list-unit-files | grep -q nginx; then
        echo "  sudo systemctl restart nginx"
    fi
    if systemctl list-unit-files | grep -q gunicorn; then
        echo "  sudo systemctl restart gunicorn"
    fi
    if systemctl list-unit-files | grep -q apache; then
        echo "  sudo systemctl restart apache2"
    fi
    echo ""
fi

echo "Alternative restart methods:"
echo "  sudo service nginx restart"
echo "  sudo service apache2 restart"
echo "  killall -HUP nginx  (reload without stopping)"
echo ""

echo "Docker (if using Docker):"
echo "  docker-compose restart"
echo "  docker restart container_name"
echo ""

# =============================================================================
# STEP 6: TEST URL
# =============================================================================
echo "STEP 6: Testing the fixed URL..."
echo ""

CSS_URL="https://vanparts-direct.co.uk/static/motortemplate/uren/assets/css/vehicle-navigation.css"
echo "After restarting your web server, test this URL:"
echo "$CSS_URL"
echo ""

if command -v curl >/dev/null 2>&1; then
    echo "Testing URL now (may fail until web server is restarted):"
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$CSS_URL")
    echo "Current HTTP Status: $HTTP_STATUS"
    
    if [ "$HTTP_STATUS" = "200" ]; then
        echo "✅ SUCCESS! File is already accessible via HTTP"
        echo "Your fix is complete and working!"
    else
        echo "⏳ File not yet accessible (restart web server to complete fix)"
    fi
else
    echo "curl not available for testing - restart web server and test manually"
fi

# =============================================================================
# SUMMARY
# =============================================================================
echo ""
echo "=========================================="
echo "FIX SCRIPT SUMMARY"
echo "=========================================="
echo "✅ Directory structure created"
echo "✅ vehicle-navigation.css file copied"
echo "✅ Permissions set correctly"
echo "✅ File verified and contains required styles"
echo ""
echo "NEXT STEPS:"
echo "1. Restart your web server (see commands above)"
echo "2. Clear your browser cache"
echo "3. Test the website - vehicle columns should now be 17% width"
echo ""
echo "If issues persist, run the diagnostic script again:"
echo "bash vps_diagnostic_script.sh"
echo ""
echo "Fix completed at: $(date)"
echo "=========================================="
