#!/bin/bash

echo "=========================================="
echo "EPCDATA DJANGO DIAGNOSTIC SCRIPT"
echo "=========================================="
echo "Timestamp: $(date)"
echo "User: $(whoami)"
echo "Current Directory: $(pwd)"
echo ""

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "❌ ERROR: manage.py not found in current directory"
    echo "Please run this script from the epcdata directory"
    exit 1
fi

echo "✅ Found manage.py - we're in the correct Django project directory"
echo ""

echo "=== SECTION 1: DJANGO ENVIRONMENT SETUP ==="
# Activate virtual environment if it exists
if [ -f "../env/bin/activate" ]; then
    echo "Activating virtual environment..."
    source ../env/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found at ../env/bin/activate"
fi

echo "Python version: $(python --version 2>&1)"
echo "Python executable: $(which python)"
echo ""

echo "=== SECTION 2: DJANGO SETTINGS ==="
echo "Checking Django settings..."

echo "STATIC_URL:"
python manage.py shell -c "from django.conf import settings; print(settings.STATIC_URL)" 2>/dev/null || echo "Error getting STATIC_URL"

echo "STATIC_ROOT:"
python manage.py shell -c "from django.conf import settings; print(settings.STATIC_ROOT)" 2>/dev/null || echo "Error getting STATIC_ROOT"

echo "STATICFILES_DIRS:"
python manage.py shell -c "from django.conf import settings; print(settings.STATICFILES_DIRS)" 2>/dev/null || echo "Error getting STATICFILES_DIRS"

echo "TEMPLATES configuration:"
python manage.py shell -c "
from django.conf import settings
import pprint
for i, template in enumerate(settings.TEMPLATES):
    print(f'Template Engine {i+1}:')
    print(f'  BACKEND: {template.get(\"BACKEND\", \"Not set\")}')
    print(f'  DIRS: {template.get(\"DIRS\", [])}')
    print(f'  APP_DIRS: {template.get(\"APP_DIRS\", False)}')
" 2>/dev/null || echo "Error getting TEMPLATES"

echo ""

echo "=== SECTION 3: TEMPLATE FILE ANALYSIS ==="
echo "Checking storefront_base.html template..."

TEMPLATE_FILE="templates/oscar/storefront_base.html"
if [ -f "$TEMPLATE_FILE" ]; then
    echo "✅ Found template file: $TEMPLATE_FILE"
    echo "File size: $(du -h "$TEMPLATE_FILE" | cut -f1)"
    echo "Last modified: $(stat -c %y "$TEMPLATE_FILE")"
    echo ""
    
    echo "Searching for vehicle-navigation.css references in template:"
    grep -n "vehicle-navigation" "$TEMPLATE_FILE" || echo "No vehicle-navigation references found"
    echo ""
    
    echo "Template lines around CSS loading:"
    grep -n -B3 -A3 "\.css" "$TEMPLATE_FILE" | head -20
else
    echo "❌ Template file not found: $TEMPLATE_FILE"
fi

echo ""

echo "=== SECTION 4: STATIC FILES ANALYSIS ==="
echo "Checking static files setup..."

echo "Contents of staticfiles directory:"
if [ -d "staticfiles" ]; then
    echo "✅ staticfiles directory exists"
    echo "Total size: $(du -sh staticfiles | cut -f1)"
    
    echo ""
    echo "Looking for vehicle-navigation.css in staticfiles:"
    find staticfiles -name "vehicle-navigation.css" -type f | while read file; do
        echo "Found: $file"
        echo "  Size: $(du -h "$file" | cut -f1)"
        echo "  Modified: $(stat -c %y "$file")"
        echo "  First 3 lines:"
        head -3 "$file" | sed 's/^/    /'
        echo ""
    done
else
    echo "❌ staticfiles directory not found"
    echo "Running collectstatic might be needed"
fi

echo ""

echo "=== SECTION 5: SOURCE TEMPLATE DIRECTORIES ==="
echo "Checking source template directories..."

echo "Contents of templates/oscar/:"
if [ -d "templates/oscar" ]; then
    ls -la templates/oscar/ | grep -E "(storefront|base)"
else
    echo "❌ templates/oscar directory not found"
fi

echo ""
echo "Looking for any storefront_base.html files:"
find . -name "storefront_base.html" -type f | while read file; do
    echo "Found: $file"
    echo "  Size: $(du -h "$file" | cut -f1)"
    echo "  Modified: $(stat -c %y "$file")"
done

echo ""

echo "=== SECTION 6: MOTORTEMPLATE ANALYSIS ==="
echo "Checking motortemplate structure..."

if [ -d "motortemplate" ]; then
    echo "✅ motortemplate directory exists"
    
    echo "vehicle-navigation.css in motortemplate:"
    find motortemplate -name "vehicle-navigation.css" -type f | while read file; do
        echo "Found: $file"
        echo "  Size: $(du -h "$file" | cut -f1)"
        echo "  Modified: $(stat -c %y "$file")"
        echo "  First 5 lines:"
        head -5 "$file" | sed 's/^/    /'
        echo ""
    done
else
    echo "❌ motortemplate directory not found"
fi

echo ""

echo "=== SECTION 7: COLLECTSTATIC TEST ==="
echo "Testing collectstatic (dry run)..."
python manage.py collectstatic --dry-run --noinput 2>&1 | head -10

echo ""

echo "=== SECTION 8: URL MAPPING TEST ==="
echo "Testing Django URL resolution..."
python manage.py shell -c "
from django.template.loader import get_template
from django.template import Context
try:
    template = get_template('oscar/storefront_base.html')
    print('✅ Template loads successfully')
    
    # Try to render a small part to see if static files resolve
    from django.template import Template, Context
    test_template = Template('{% load static %}{% static \"motortemplate/uren/assets/css/vehicle-navigation.css\" %}')
    static_url = test_template.render(Context({}))
    print(f'Static URL resolves to: {static_url}')
except Exception as e:
    print(f'❌ Template error: {e}')
" 2>/dev/null || echo "Error testing template loading"

echo ""

echo "=== SECTION 9: BROWSER CACHE ANALYSIS ==="
echo "HTTP Headers check for CSS file:"
curl -I "https://vanparts-direct.co.uk/static/motortemplate/uren/assets/css/vehicle-navigation.css" 2>/dev/null | head -10

echo ""

echo "=== SECTION 10: CURRENT GIT STATUS ==="
echo "Git status in epcdata directory:"
git status --porcelain 2>/dev/null || echo "Not a git repository or git not available"

echo ""
echo "Latest commits affecting templates:"
git log --oneline -5 --grep="template\|css\|vehicle" 2>/dev/null || echo "Git log not available"

echo ""

echo "=== SECTION 11: FINAL RECOMMENDATIONS ==="
echo "Based on the diagnostic results:"
echo ""
echo "If template changes aren't taking effect:"
echo "1. Check if the correct template file is being loaded"
echo "2. Verify Django template caching is not interfering"
echo "3. Ensure static files are properly collected"
echo "4. Check browser cache and force refresh"
echo "5. Verify web server is serving the updated files"

echo ""
echo "To force template refresh:"
echo "python manage.py collectstatic --clear --noinput"
echo "sudo systemctl restart epcdata.service"

echo ""
echo "=========================================="
echo "END OF EPCDATA DIAGNOSTIC SCRIPT"
echo "=========================================="
