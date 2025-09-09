#!/usr/bin/env python
"""
Quick test script for order confirmation emails
"""

import os
import django
from pathlib import Path

# Setup Django environment
BASE_DIR = Path(__file__).resolve().parent
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')

import sys
sys.path.append(str(BASE_DIR))

django.setup()

def test_order_confirmation():
    """Test the order confirmation email system"""
    print("🧪 Testing Order Confirmation Email System")
    print("=" * 50)
    
    # Test that signals are properly loaded
    from django.apps import apps
    try:
        epcdata_config = apps.get_app_config('epcdata')
        print("✅ EpcData app configuration loaded")
    except Exception as e:
        print(f"❌ EpcData app configuration error: {e}")
        return
    
    # Test that order_emails module can be imported
    try:
        from epcdata import order_emails
        print("✅ Order emails module imported successfully")
    except Exception as e:
        print(f"❌ Order emails module error: {e}")
        return
    
    # Test that templates exist
    import os
    template_path = BASE_DIR / 'templates' / 'oscar' / 'emails'
    if template_path.exists():
        templates = list(template_path.glob('*.txt')) + list(template_path.glob('*.html'))
        print(f"✅ Found {len(templates)} email templates")
        for template in templates:
            print(f"   📄 {template.name}")
    else:
        print("❌ Email templates directory not found")
        return
    
    # Test email settings
    from django.conf import settings
    print(f"✅ EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"✅ OSCAR_FROM_EMAIL: {getattr(settings, 'OSCAR_FROM_EMAIL', 'Not set')}")
    print(f"✅ DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    
    print("\n" + "=" * 50)
    print("🎉 Order confirmation system ready!")
    print("\nTo test with a real order:")
    print("1. Run: python manage.py test_order_email")
    print("2. Or place a test order through the website")
    print("3. Check your email at info@rapidfit.co.uk")

if __name__ == "__main__":
    test_order_confirmation()
