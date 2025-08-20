#!/usr/bin/env python3
"""
Test URL resolution
"""
import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')

try:
    django.setup()
    from django.urls import reverse, resolve
    from django.test import RequestFactory
    
    print("=== URL TESTING ===")
    
    # Test URL resolution
    try:
        url = reverse('checkout:payment-details')
        print(f"✅ checkout:payment-details resolves to: {url}")
        
        # Test URL resolver
        resolver = resolve(url)
        print(f"✅ URL resolves to view: {resolver.func}")
        print(f"✅ View class: {resolver.func.view_class}")
    except Exception as e:
        print(f"❌ Error resolving checkout:payment-details: {e}")
    
    try:
        url = reverse('payment:worldpay-redirect')
        print(f"✅ payment:worldpay-redirect resolves to: {url}")
    except Exception as e:
        print(f"❌ Error resolving payment:worldpay-redirect: {e}")
    
    # Test form creation
    try:
        from payment.forms import WorldpayPaymentDetailsForm
        form = WorldpayPaymentDetailsForm()
        print(f"✅ Form created successfully")
        print(f"✅ Form fields: {list(form.fields.keys())}")
        
        # Test form with data
        form_data = {'payment_method': 'worldpay'}
        bound_form = WorldpayPaymentDetailsForm(form_data)
        print(f"✅ Form bound: {bound_form.is_bound}")
        print(f"✅ Form valid: {bound_form.is_valid()}")
        if not bound_form.is_valid():
            print(f"❌ Form errors: {bound_form.errors}")
    except Exception as e:
        print(f"❌ Error with form: {e}")
    
    print("\n=== SUMMARY ===")
    print("If all URLs resolve correctly, the issue might be:")
    print("1. Template form action URL")
    print("2. CSRF token issues")
    print("3. Form field name mismatch")
    print("4. View logic issues")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Save test results to file since terminal output isn't working
with open('url_test_results.txt', 'w') as f:
    f.write("URL test completed - check this file for results\n")
