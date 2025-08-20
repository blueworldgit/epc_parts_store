#!/usr/bin/env python3
"""
Test Live Worldpay Endpoint Connectivity
"""

import os
import sys
import django
import requests
import base64

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from django.conf import settings

def test_live_endpoint():
    print("🌍 Testing Live Worldpay Endpoint Connectivity")
    print("=" * 50)
    
    # Get configuration
    api_url = getattr(settings, 'WORLDPAY_GATEWAY_URL', '')
    username = getattr(settings, 'WORLDPAY_USERNAME', '')
    password = getattr(settings, 'WORLDPAY_PASSWORD', '')
    
    print(f"🎯 Target URL: {api_url}")
    print(f"👤 Username: {username}")
    print(f"🔑 Password: {'*' * len(password)}")
    
    # Create basic auth header
    auth_string = f"{username}:{password}"
    auth_bytes = auth_string.encode('ascii')
    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
    
    headers = {
        'Authorization': f'Basic {auth_b64}',
        'Content-Type': 'application/vnd.worldpay.payments-v6+json',
        'Accept': 'application/vnd.worldpay.payments-v6+json'
    }
    
    print("\n🔗 Testing endpoint connectivity...")
    
    try:
        # Just test connectivity with a simple GET request
        # (This will likely return 405 Method Not Allowed, but confirms connectivity)
        response = requests.get(api_url, headers=headers, timeout=10)
        
        print(f"✅ Endpoint is reachable!")
        print(f"📊 Response Status: {response.status_code}")
        print(f"📝 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 405:
            print("✅ Got 405 Method Not Allowed - This is expected for GET requests to payment endpoint")
            print("✅ This confirms the live endpoint is active and responding")
        elif response.status_code == 401:
            print("❌ Got 401 Unauthorized - Credentials may be invalid for live environment")
        elif response.status_code == 403:
            print("❌ Got 403 Forbidden - Account may not be enabled for live payments")
        else:
            print(f"ℹ️  Unexpected response code: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out - Endpoint may be unreachable")
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    print("\n📝 Notes:")
    print("  - Live endpoint requires valid live credentials")
    print("  - Test cards will NOT work with live endpoint")
    print("  - Use real card details for live testing")
    print("  - Monitor Worldpay dashboard for live transactions")

if __name__ == "__main__":
    test_live_endpoint()
