#!/usr/bin/env python3
"""
Focused Worldpay API Test - Payment Session Creation
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
    
    print("=== FOCUSED WORLDPAY API TEST ===\n")
    
    # Get credentials
    username = getattr(settings, 'WORLDPAY_USERNAME')
    password = getattr(settings, 'WORLDPAY_PASSWORD')
    entity_id = getattr(settings, 'WORLDPAY_ENTITY_ID')
    test_mode = getattr(settings, 'WORLDPAY_TEST_MODE', True)
    
    print(f"✅ Credentials loaded:")
    print(f"   Username: {username}")
    print(f"   Entity ID: {entity_id}")
    print(f"   Test Mode: {test_mode}\n")
    
    # Create auth header
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    auth_header = f"Basic {encoded_credentials}"
    
    # Use correct endpoint for test mode
    base_url = "https://try.access.worldpay.com" if test_mode else "https://access.worldpay.com"
    payment_url = f"{base_url}/payments/hosted/sessions"
    
    print(f"🎯 Testing endpoint: {payment_url}")
    
    # Create test payment payload
    test_payload = {
        "transactionReference": "TEST-001",
        "merchant": {
            "entity": entity_id
        },
        "instruction": {
            "value": {
                "currency": "GBP",
                "amount": 1000  # £10.00 in pence
            },
            "narrative": {
                "line1": "Test payment for Django Oscar cart"
            }
        },
        "customer": {
            "details": {
                "email": "test@example.com"
            }
        }
    }
    
    headers = {
        'Authorization': auth_header,
        'Content-Type': 'application/vnd.worldpay.payments-v7.hal+json',
        'Accept': 'application/vnd.worldpay.payments-v7.hal+json'
    }
    
    print(f"📦 Payload: {json.dumps(test_payload, indent=2)}")
    print(f"📋 Headers: {json.dumps({k: v if k != 'Authorization' else f'{v[:20]}...' for k, v in headers.items()}, indent=2)}\n")
    
    # Make the API call
    print("🚀 Making API call...")
    try:
        response = requests.post(
            payment_url,
            headers=headers,
            json=test_payload,
            timeout=15
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📄 Response Headers: {json.dumps(dict(response.headers), indent=2)}")
        print(f"📝 Response Body: {response.text}\n")
        
        if response.status_code == 201:
            print("✅ SUCCESS: Payment session created!")
            try:
                data = response.json()
                if '_links' in data:
                    print(f"🔗 Payment links: {json.dumps(data['_links'], indent=2)}")
            except:
                pass
        elif response.status_code == 401:
            print("❌ AUTHENTICATION ERROR")
            print("   - Check your username/password")
            print("   - Verify credentials in Worldpay dashboard")
        elif response.status_code == 403:
            print("❌ FORBIDDEN ERROR")
            print("   - Check entity ID is correct")
            print("   - Verify permissions in Worldpay dashboard")
        elif response.status_code == 400:
            print("❌ BAD REQUEST ERROR")
            print("   - Check payload format")
            print("   - Verify required fields")
        else:
            print(f"❌ UNEXPECTED ERROR: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT ERROR: Request timed out")
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR: Could not connect to Worldpay")
    except Exception as e:
        print(f"❌ REQUEST ERROR: {e}")
    
    # Test alternative endpoint format
    print("\n=== TESTING ALTERNATIVE ENDPOINT ===")
    alt_payment_url = f"{base_url}/payment-pages/v1/sessions"
    print(f"🎯 Testing alternative endpoint: {alt_payment_url}")
    
    alt_payload = {
        "amount": 1000,
        "currency": "GBP",
        "description": "Test payment",
        "customer": {
            "email": "test@example.com"
        },
        "success_url": "https://example.com/success",
        "failure_url": "https://example.com/failure",
        "cancel_url": "https://example.com/cancel"
    }
    
    alt_headers = {
        'Authorization': auth_header,
        'Content-Type': 'application/vnd.worldpay.payment_pages-v1.hal+json',
        'Accept': 'application/vnd.worldpay.payment_pages-v1.hal+json'
    }
    
    try:
        response = requests.post(
            alt_payment_url,
            headers=alt_headers,
            json=alt_payload,
            timeout=15
        )
        
        print(f"📊 Alternative Response Status: {response.status_code}")
        print(f"📝 Alternative Response Body: {response.text}\n")
        
        if response.status_code == 201:
            print("✅ SUCCESS: Alternative endpoint works!")
        
    except Exception as e:
        print(f"❌ Alternative endpoint error: {e}")

except Exception as e:
    print(f"❌ Django setup error: {e}")
    import traceback
    traceback.print_exc()
