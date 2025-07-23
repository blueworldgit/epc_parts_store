#!/usr/bin/env python3
"""
Template debugging script
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
sys.path.append(str(Path(__file__).parent))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

def debug_templates():
    """Debug template loading"""
    print("=== Template Debug ===\n")
    
    from django.conf import settings
    from django.template.loader import get_template
    from django.template import TemplateDoesNotExist
    
    print(f"Template directories: {settings.TEMPLATES[0]['DIRS']}")
    print(f"APP_DIRS: {settings.TEMPLATES[0]['APP_DIRS']}")
    
    # Try to load the dashboard index template
    templates_to_try = [
        'dashboard/index.html',
        'oscar/dashboard/index.html',
        'dashboard/layout.html',
        'oscar/layout.html',
        'oscar/dashboard/layout.html'
    ]
    
    for template_name in templates_to_try:
        try:
            template = get_template(template_name)
            print(f"✓ Found template: {template_name}")
            print(f"  Template origin: {template.origin}")
            print(f"  Template source: {template.source[:200]}...")
            break
        except TemplateDoesNotExist as e:
            print(f"✗ Template not found: {template_name}")
    
    # Check installed apps for Oscar
    oscar_apps = [app for app in settings.INSTALLED_APPS if 'oscar' in app]
    print(f"\nOscar apps installed: {len(oscar_apps)}")
    
    # Try to locate dashboard templates in Oscar package
    try:
        import oscar.apps.dashboard
        dashboard_path = Path(oscar.apps.dashboard.__file__).parent
        template_dirs = list(dashboard_path.rglob('templates'))
        print(f"\nOscar dashboard template directories found:")
        for template_dir in template_dirs:
            print(f"  {template_dir}")
            if template_dir.exists():
                templates = list(template_dir.rglob('*.html'))
                print(f"    Templates: {len(templates)}")
                for template in templates[:5]:  # Show first 5
                    print(f"      - {template.name}")
    except Exception as e:
        print(f"Error finding Oscar templates: {e}")

if __name__ == '__main__':
    debug_templates()
