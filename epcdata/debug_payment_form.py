#!/usr/bin/env python3
"""
Debug the payment form submission
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
    from payment.forms import WorldpayPaymentDetailsForm
    from django.urls import reverse
    
    print("=== PAYMENT FORM DEBUG ===\n")
    
    # Test form creation
    form = WorldpayPaymentDetailsForm()
    print(f"Form fields: {list(form.fields.keys())}")
    print(f"Form choices: {form.fields['payment_method'].choices}")
    print(f"Form initial: {form.initial}")
    
    # Test form HTML
    print(f"\nForm HTML:")
    print(form.as_p())
    
    # Test form with data
    print(f"\nTesting form with data:")
    form_with_data = WorldpayPaymentDetailsForm({'payment_method': 'worldpay'})
    print(f"Form is valid: {form_with_data.is_valid()}")
    if form_with_data.errors:
        print(f"Form errors: {form_with_data.errors}")
    if form_with_data.is_valid():
        print(f"Cleaned data: {form_with_data.cleaned_data}")
    
    # Test URL resolving
    print(f"\nURL Testing:")
    try:
        payment_details_url = reverse('checkout:payment-details')
        print(f"payment-details URL: {payment_details_url}")
    except Exception as e:
        print(f"Error resolving payment-details URL: {e}")
    
    try:
        worldpay_redirect_url = reverse('payment:worldpay-redirect')
        print(f"worldpay-redirect URL: {worldpay_redirect_url}")
    except Exception as e:
        print(f"Error resolving worldpay-redirect URL: {e}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
