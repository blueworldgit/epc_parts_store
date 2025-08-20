#!/usr/bin/env python3
"""
Verify Worldpay Environment Switching
"""

import os
import sys
import django

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from django.conf import settings
from payment.gateway_facade import WorldpayGatewayFacade

def test_environment_switching():
    print("🔧 Testing Worldpay Environment Configuration")
    print("=" * 50)
    
    # Check environment variables
    print(f"WORLDPAY_TEST_MODE (env): {os.getenv('WORLDPAY_TEST_MODE', 'Not set')}")
    print(f"WORLDPAY_TEST_MODE (setting): {getattr(settings, 'WORLDPAY_TEST_MODE', 'Not set')}")
    print(f"WORLDPAY_GATEWAY_URL: {getattr(settings, 'WORLDPAY_GATEWAY_URL', 'Not set')}")
    print(f"WORLDPAY_USERNAME: {getattr(settings, 'WORLDPAY_USERNAME', 'Not set')}")
    print(f"WORLDPAY_ENTITY_ID: {getattr(settings, 'WORLDPAY_ENTITY_ID', 'Not set')}")
    
    print("\n🚀 Testing Gateway Facade Configuration")
    print("-" * 40)
    
    # Test facade initialization
    facade = WorldpayGatewayFacade()
    print(f"Gateway API URL: {facade.api_url}")
    print(f"Username: {facade.username}")
    print(f"Entity ID: {facade.entity_id}")
    
    # Test refund URL generation
    test_payment_id = "test-payment-123"
    base_url = facade.api_url.replace('/payments/authorizations', '')
    refund_url = f"{base_url}/payments/{test_payment_id}/refunds"
    print(f"Refund URL would be: {refund_url}")
    
    print("\n✅ Environment Configuration Check Complete")
    
    # Determine mode
    is_test_mode = getattr(settings, 'WORLDPAY_TEST_MODE', True)
    if is_test_mode:
        print("🔍 Currently in TEST mode")
        print("  - Uses: https://try.access.worldpay.com/payments/authorizations")
        print("  - Safe for testing with test cards")
    else:
        print("🔴 Currently in LIVE mode")
        print("  - Uses: https://access.worldpay.com/payments/authorizations")
        print("  - ⚠️  REAL MONEY will be processed!")
        print("  - Use real card details for testing")
    
    return facade

if __name__ == "__main__":
    facade = test_environment_switching()
