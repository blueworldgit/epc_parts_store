#!/usr/bin/env python
"""
Simple test to trigger Worldpay facade initialization and show debug output
This will log the exact credentials being used when you start your server
"""

import os
import sys
import django
import logging

# Configure logging to show debug output
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)

# Add the project directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

def test_worldpay_initialization():
    """Initialize Worldpay facade to trigger debug logging"""
    print("🚀 TESTING WORLDPAY INITIALIZATION")
    print("=" * 50)
    
    try:
        from payment.gateway_facade import WorldpayGatewayFacade
        print("📦 Importing WorldpayGatewayFacade...")
        
        print("🔧 Creating facade instance (this will show debug output)...")
        facade = WorldpayGatewayFacade()
        
        print("\n✅ Facade created successfully!")
        print("🔍 Quick credential check:")
        print(f"   Username empty: {not bool(facade.username)}")
        print(f"   Password empty: {not bool(facade.password)}")
        print(f"   Entity ID empty: {not bool(facade.entity_id)}")
        print(f"   API URL empty: {not bool(facade.api_url)}")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        print(f"Full traceback:\n{traceback.format_exc()}")

if __name__ == "__main__":
    test_worldpay_initialization()
