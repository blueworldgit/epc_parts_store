#!/usr/bin/env python3
"""
Debug Worldpay Configuration at Runtime
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

def debug_runtime_config():
    print("🔍 RUNTIME WORLDPAY CONFIGURATION DEBUG")
    print("=" * 60)
    
    print("1. Environment Variables (Raw):")
    print(f"   WORLDPAY_TEST_MODE = '{os.getenv('WORLDPAY_TEST_MODE', 'NOT SET')}'")
    print(f"   WORLDPAY_GATEWAY_URL = '{os.getenv('WORLDPAY_GATEWAY_URL', 'NOT SET')}'")
    
    print("\n2. Django Settings:")
    print(f"   WORLDPAY_TEST_MODE = {getattr(settings, 'WORLDPAY_TEST_MODE', 'NOT SET')}")
    print(f"   WORLDPAY_GATEWAY_URL = '{getattr(settings, 'WORLDPAY_GATEWAY_URL', 'NOT SET')}'")
    
    print("\n3. Gateway Facade Configuration:")
    facade = WorldpayGatewayFacade()
    print(f"   facade.api_url = '{facade.api_url}'")
    
    print("\n4. Expected URLs:")
    print(f"   Test URL: https://try.access.worldpay.com/payments/authorizations")
    print(f"   Live URL: https://access.worldpay.com/payments/authorizations")
    
    print("\n5. Analysis:")
    test_mode_env = os.getenv('WORLDPAY_TEST_MODE', 'True').lower() == 'true'
    test_mode_setting = getattr(settings, 'WORLDPAY_TEST_MODE', True)
    
    print(f"   Environment test mode: {test_mode_env}")
    print(f"   Settings test mode: {test_mode_setting}")
    
    if facade.api_url == 'https://try.access.worldpay.com/payments/authorizations':
        print("   🟡 Currently using TEST endpoint")
    elif facade.api_url == 'https://access.worldpay.com/payments/authorizations':
        print("   🔴 Currently using LIVE endpoint")
    else:
        print(f"   ❓ Unknown endpoint: {facade.api_url}")

if __name__ == "__main__":
    debug_runtime_config()
