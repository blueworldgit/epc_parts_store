#!/usr/bin/env python3
"""
Comprehensive Worldpay API Test Script
Tests actual API calls, endpoints, and request formats
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
    
    print("=== WORLDPAY API COMPREHENSIVE TEST ===\n")
    
    # Get credentials
    username = getattr(settings, 'WORLDPAY_USERNAME')
    password = getattr(settings, 'WORLDPAY_PASSWORD')
    entity_id = getattr(settings, 'WORLDPAY_ENTITY_ID')
    test_mode = getattr(settings, 'WORLDPAY_TEST_MODE', True)
    
    print(f"Username: {username}")
    print(f"Password: {password[:10]}...")
    print(f"Entity ID: {entity_id}")
    print(f"Test Mode: {test_mode}\n")
    
    # 1. TEST API ENDPOINTS
    print("=== 1. TESTING API ENDPOINTS ===")
    
    # Different possible endpoints
    endpoints = [
        "https://try.access.worldpay.com/",  # Sandbox
        "https://access.worldpay.com/",      # Production
        "https://api.worldpay.com/",         # Alternative API
        "https://secure.worldpay.com/",      # Secure endpoint
    ]
    
    # Create auth header
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    auth_header = f"Basic {encoded_credentials}"
    
    print(f"Auth Header: {auth_header[:30]}...\n")
    
    # Test each endpoint
    for endpoint in endpoints:
        print(f"Testing endpoint: {endpoint}")
        try:
            response = requests.get(
                endpoint,
                headers={
                    'Authorization': auth_header,
                    'Content-Type': 'application/vnd.worldpay.payment_pages-v1.hal+json',
                    'Accept': 'application/vnd.worldpay.payment_pages-v1.hal+json'
                },
                timeout=5
            )
            print(f"  Status: {response.status_code}")
            print(f"  Headers: {dict(response.headers)}")
            if response.text:
                print(f"  Response: {response.text[:200]}...")
        except Exception as e:
            print(f"  Error: {e}")
        print()
    
    # 2. TEST ACTUAL API CALL - CREATE PAYMENT SESSION
    print("=== 2. TESTING PAYMENT SESSION CREATION ===")
    
    # Use the most likely correct endpoint based on test mode
    base_url = "https://try.access.worldpay.com" if test_mode else "https://access.worldpay.com"
    payment_url = f"{base_url}/payment-pages/v1/sessions"
    
    print(f"Using endpoint: {payment_url}")
    
    # Test payment session creation payload
    test_payload = {
        "amount": 1000,  # £10.00 in pence
        "currency": "GBP",
        "description": "Test payment",
        "customer": {
            "email": "test@example.com"
        },
        "success_url": "https://example.com/success",
        "failure_url": "https://example.com/failure",
        "cancel_url": "https://example.com/cancel"
    }
    
    print(f"Test Payload: {json.dumps(test_payload, indent=2)}")
    
    headers = {
        'Authorization': auth_header,
        'Content-Type': 'application/vnd.worldpay.payment_pages-v1.hal+json',
        'Accept': 'application/vnd.worldpay.payment_pages-v1.hal+json'
    }
    
    print(f"Headers: {json.dumps(headers, indent=2)}")
    
    try:
        response = requests.post(
            payment_url,
            headers=headers,
            json=test_payload,
            timeout=15
        )
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Headers: {json.dumps(dict(response.headers), indent=2)}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 201:
            print("✅ SUCCESS: Payment session created successfully!")
            data = response.json()
            if '_links' in data and 'payment' in data['_links']:
                print(f"Payment URL: {data['_links']['payment']['href']}")
        elif response.status_code == 401:
            print("❌ AUTHENTICATION ERROR: Check your credentials")
        elif response.status_code == 400:
            print("❌ BAD REQUEST: Check your payload format")
        elif response.status_code == 403:
            print("❌ FORBIDDEN: Check your permissions/entity ID")
        else:
            print(f"❌ UNEXPECTED ERROR: {response.status_code}")
            
    except Exception as e:
        print(f"❌ REQUEST ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    # 3. TEST REQUEST FORMAT VARIATIONS
    print("\n=== 3. TESTING REQUEST FORMAT VARIATIONS ===")
    
    # Test different content types
    content_types = [
        'application/vnd.worldpay.payment_pages-v1.hal+json',
        'application/json',
        'application/vnd.worldpay.hosted-v1+json',
        'application/hal+json'
    ]
    
    for content_type in content_types:
        print(f"\nTesting Content-Type: {content_type}")
        try:
            response = requests.post(
                payment_url,
                headers={
                    'Authorization': auth_header,
                    'Content-Type': content_type,
                    'Accept': content_type
                },
                json=test_payload,
                timeout=10
            )
            print(f"  Status: {response.status_code}")
            if response.status_code != 200:
                print(f"  Error: {response.text[:100]}...")
        except Exception as e:
            print(f"  Error: {e}")
    
    # 4. TEST MINIMAL PAYLOAD
    print("\n=== 4. TESTING MINIMAL PAYLOAD ===")
    
    minimal_payload = {
        "amount": 1000,
        "currency": "GBP"
    }
    
    print(f"Minimal Payload: {json.dumps(minimal_payload, indent=2)}")
    
    try:
        response = requests.post(
            payment_url,
            headers=headers,
            json=minimal_payload,
            timeout=30
        )
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {response.text}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    # 5. TEST ENTITY ID IN HEADERS
    print("\n=== 5. TESTING ENTITY ID IN HEADERS ===")
    
    headers_with_entity = headers.copy()
    headers_with_entity['Worldpay-Entity-Id'] = entity_id
    
    print(f"Headers with Entity ID: {json.dumps(headers_with_entity, indent=2)}")
    
    try:
        response = requests.post(
            payment_url,
            headers=headers_with_entity,
            json=test_payload,
            timeout=30
        )
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {response.text}")
        
    except Exception as e:
        print(f"Error: {e}")

except Exception as e:
    print(f"Error setting up Django: {e}")
    import traceback
    traceback.print_exc()
