#!/usr/bin/env python
import os
import sys
import django

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from django.template.loader import get_template
from django.conf import settings

print("🔍 Django Template Debug")
print("=" * 50)

print(f"Template directories: {settings.TEMPLATES[0]['DIRS']}")
print()

# Check what template Django is loading for dashboard layout
try:
    template = get_template('oscar/dashboard/layout.html')
    print(f"✅ Layout template loaded from: {template.origin.name}")
    
    # Read the first few lines to see what it contains
    with open(template.origin.name, 'r') as f:
        content = f.read()
        print()
        print("First 300 characters of layout template:")
        print("-" * 40)
        print(content[:300])
        print("-" * 40)
        
        # Check if it contains Bootstrap classes
        if 'container-fluid' in content:
            print("❌ FOUND: This template contains Bootstrap container-fluid")
        else:
            print("✅ GOOD: This template does NOT contain Bootstrap container-fluid")
            
        if 'col-md-3' in content:
            print("❌ FOUND: This template contains Bootstrap col-md-3")
        else:
            print("✅ GOOD: This template does NOT contain Bootstrap col-md-3")

except Exception as e:
    print(f"❌ Error loading template: {e}")

# Also check index template
try:
    template = get_template('oscar/dashboard/index.html')
    print(f"\n✅ Index template loaded from: {template.origin.name}")
except Exception as e:
    print(f"\n❌ Error loading index template: {e}")
