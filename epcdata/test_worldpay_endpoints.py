#!/usr/bin/env python3
"""
Test different Worldpay API endpoints to find the correct one
"""
import os
import sys
import django
import requests
import json
import base64
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')

try:
    django.setup()
    from django.conf import settings
    
    print("=== WORLDPAY API ENDPOINT TESTING ===\n")
    
    # Get credentials
    username = getattr(settings, 'WORLDPAY_USERNAME')
    password = getattr(settings, 'WORLDPAY_PASSWORD')
    entity_id = getattr(settings, 'WORLDPAY_ENTITY_ID')
    
    print(f"Username: {username}")
    print(f"Entity ID: {entity_id}")
    print(f"Test Mode: {getattr(settings, 'WORLDPAY_TEST_MODE')}")
    
    # Create auth header
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    auth_header = f"Basic {encoded_credentials}"
    
    # Test different possible endpoints for Worldpay Hosted Payment Pages
    test_endpoints = [
        # Current endpoint (getting 404)
        "https://try.access.worldpay.com/payment-pages/v1/sessions",
        
        # Alternative API formats
        "https://try.access.worldpay.com/sessions",
        "https://try.access.worldpay.com/v1/sessions", 
        "https://try.access.worldpay.com/payments/sessions",
        "https://try.access.worldpay.com/payments/v1/sessions",
        "https://try.access.worldpay.com/hosted/sessions",
        "https://try.access.worldpay.com/hosted/v1/sessions",
        
        # Alternative base URLs
        "https://api.worldpay.com/v1/sessions",
        "https://api.worldpay.com/payment-pages/v1/sessions",
        "https://secure.worldpay.com/v1/sessions",
        
        # Access checkout API (different from payment pages)
        "https://try.access.worldpay.com/access-checkout/sessions",
    ]
    
    # Simple test payload
    test_payload = {
        "amount": 1000,
        "currency": "GBP",
        "description": "Test payment"
    }
    
    print(f"\nTesting {len(test_endpoints)} different endpoints...\n")
    
    for i, endpoint in enumerate(test_endpoints, 1):
        print(f"{i:2d}. Testing: {endpoint}")
        
        # Try different content types
        for content_type in [
            'application/vnd.worldpay.payment_pages-v1.hal+json',
            'application/json',
            'application/vnd.worldpay.sessions-v1.hal+json'
        ]:
            
            headers = {
                'Authorization': auth_header,
                'Content-Type': content_type,
                'Accept': content_type
            }
            
            try:
                response = requests.post(
                    endpoint,
                    headers=headers,
                    json=test_payload,
                    timeout=10
                )
                
                print(f"    Content-Type: {content_type}")
                print(f"    Status: {response.status_code}")
                
                if response.status_code == 201:
                    print(f"    ✅ SUCCESS! Found working endpoint")
                    print(f"    Response: {response.text[:200]}...")
                    print(f"\n🎉 WORKING ENDPOINT FOUND:")
                    print(f"    URL: {endpoint}")
                    print(f"    Content-Type: {content_type}")
                    print(f"    Status: {response.status_code}")
                    break
                elif response.status_code == 400:
                    print(f"    ⚠️  Bad Request - Endpoint exists but payload wrong")
                    if response.text:
                        print(f"    Response: {response.text[:100]}...")
                elif response.status_code == 401:
                    print(f"    ⚠️  Unauthorized - Endpoint exists but auth wrong")
                elif response.status_code == 404:
                    print(f"    ❌ Not Found")
                else:
                    print(f"    ❓ Other: {response.text[:100]}...")
                    
            except requests.exceptions.Timeout:
                print(f"    ⏰ Timeout")
            except requests.exceptions.ConnectionError:
                print(f"    🔌 Connection Error")
            except Exception as e:
                print(f"    ❌ Error: {e}")
        
        # Break early if we found a working endpoint
        if any(response.status_code == 201 for response in []):
            break
            
        print()
    
    print("\n=== SUMMARY ===")
    print("If no endpoint returned 201 (success), the issue might be:")
    print("1. Wrong API endpoint format")
    print("2. Wrong content-type headers")
    print("3. Wrong payload format")
    print("4. Wrong authentication method")
    print("5. Test credentials not configured properly")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
