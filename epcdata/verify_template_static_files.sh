#!/bin/bash
# Verify Real Static Files in Templates Script
# This script checks what static files your Django templates are actually trying to load

echo "🔍 Analyzing Django Templates for Static File References"
echo "======================================================="

cd /home/maxis/epc_parts_store/epcdata

# Check Oscar base templates
echo "1. OSCAR BASE TEMPLATES:"
if [ -f "templates/oscar/base.html" ]; then
    echo "✅ Custom Oscar base template found"
    echo "Static file references:"
    grep -n "{% load static %}\|{% static " templates/oscar/base.html | head -10
else
    echo "Using default Oscar templates"
fi

# Check custom templates
echo ""
echo "2. CUSTOM TEMPLATES:"
find templates/ -name "*.html" 2>/dev/null | while read template; do
    echo "Template: $template"
    grep -n "{% static \|/static/\|/media/" "$template" | head -3
    echo "---"
done

# Check what static files are actually being referenced
echo ""
echo "3. STATIC FILE REFERENCES IN ALL TEMPLATES:"
echo "CSS files referenced:"
find templates/ -name "*.html" -exec grep -l "\.css" {} \; 2>/dev/null | while read file; do
    echo "In $file:"
    grep -o "{% static '[^']*\.css' %}\|/static/[^\"']*\.css\|/media/[^\"']*\.css" "$file" | head -5
done

echo ""
echo "4. CHECKING OSCAR DEFAULT TEMPLATES:"
python manage.py shell -c "
import oscar
import os
oscar_path = oscar.__path__[0]
templates_path = os.path.join(oscar_path, 'templates')
print(f'Oscar templates path: {templates_path}')

# Check if Oscar base template exists
base_template = os.path.join(templates_path, 'oscar', 'base.html')
if os.path.exists(base_template):
    print('✅ Oscar base template found')
    with open(base_template, 'r') as f:
        content = f.read()
        if 'bootstrap' in content.lower():
            print('✅ Bootstrap references found in Oscar base')
        else:
            print('⚠️ No Bootstrap references in Oscar base')
else:
    print('❌ Oscar base template not found')
"

# Check what templates Django is actually using
echo ""
echo "5. TEMPLATE DEBUGGING:"
python manage.py shell -c "
from django.conf import settings
print('Template directories:')
for template_config in settings.TEMPLATES:
    for template_dir in template_config.get('DIRS', []):
        print(f'  - {template_dir}')
"

echo ""
echo "6. STATIC FILES THAT SHOULD BE LOADED:"
echo "Based on collected staticfiles, these should be available:"
echo "Bootstrap: /static/uren/assets/css/vendor/bootstrap.min.css"
echo "Oscar CSS: /static/oscar/css/"
echo "Motor template: /static/motortemplate/"

ls -la staticfiles/uren/assets/css/vendor/ | grep -E "\.(css|js)$" | head -5
echo "..."

echo ""
echo "✅ Template analysis complete!"
echo "The key is ensuring your templates reference files that exist in staticfiles/"