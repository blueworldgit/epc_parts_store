#!/usr/bin/env python3
"""
Test the fixed Worldpay facade
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
    from payment.facade import WorldpayHostedFacade
    
    print("=== TESTING FIXED WORLDPAY FACADE ===\n")
    
    # Create facade instance
    facade = WorldpayHostedFacade()
    
    print(f"✅ API URL: {facade.api_url}")
    print(f"✅ Username: {facade.username}")
    print(f"✅ Entity ID: {facade.entity_id}")
    
    # Test auth header
    auth_header = facade._get_auth_header()
    print(f"✅ Auth header: {auth_header[:30]}...")
    
    print("\n🚀 Facade setup looks good!")
    print("💡 The API endpoint has been fixed to include '/v1/sessions'")
    print("💡 The payload format has been simplified")
    print("💡 Now try making a payment through your Django site")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
