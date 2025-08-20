#!/usr/bin/env python3
"""
Test Live Worldpay API with Test Card
This will help us understand why test cards are still working
"""

import os
import sys
import django
import requests
import base64
import json
from decimal import Decimal

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from django.conf import settings

def test_live_api_with_test_card():
    print("🧪 Testing Live Worldpay API with Test Card")
    print("=" * 50)
    
    # Get current configuration
    api_url = getattr(settings, 'WORLDPAY_GATEWAY_URL', '')
    username = getattr(settings, 'WORLDPAY_USERNAME', '')
    password = getattr(settings, 'WORLDPAY_PASSWORD', '')
    entity_id = getattr(settings, 'WORLDPAY_ENTITY_ID', '')
    test_mode = getattr(settings, 'WORLDPAY_TEST_MODE', True)
    
    print(f"🎯 API URL: {api_url}")
    print(f"👤 Username: {username}")
    print(f"🆔 Entity ID: {entity_id}")
    print(f"🔧 Test Mode Setting: {test_mode}")
    
    # Create Basic Auth
    auth_string = f"{username}:{password}"
    auth_bytes = auth_string.encode('ascii')
    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
    
    headers = {
        'Authorization': f'Basic {auth_b64}',
        'Content-Type': 'application/vnd.worldpay.payments-v6+json',
        'Accept': 'application/vnd.worldpay.payments-v6+json'
    }
    
    # Test payment payload with a known test card
    payload = {
        "transactionReference": "TEST-LIVE-API-001",
        "merchant": {
            "entity": entity_id
        },
        "instruction": {
            "narrative": {
                "line1": "Test payment to verify live API behavior"
            },
            "value": {
                "currency": "GBP",
                "amount": 100  # £1.00
            },
            "paymentInstrument": {
                "type": "card/plain",
                "cardNumber": "4444333322221111",  # Known test card
                "expiryDate": {
                    "month": 12,
                    "year": 2025
                },
                "cardHolderName": "Test Cardholder",
                "cvc": "123"
            }
        }
    }
    
    print(f"\n🚀 Sending test card payment to: {api_url}")
    print(f"💳 Card: 4444333322221111 (Known test card)")
    print(f"💰 Amount: £1.00")
    
    try:
        response = requests.post(
            api_url,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"\n📊 Response Status: {response.status_code}")
        print(f"📡 Response Headers: {dict(response.headers)}")
        
        if response.content:
            try:
                response_data = response.json()
                print(f"📝 Response Body: {json.dumps(response_data, indent=2)}")
            except:
                print(f"📝 Response Body (raw): {response.text}")
        
        # Analysis
        print(f"\n🔍 Analysis:")
        if response.status_code == 201:
            print("❌ PROBLEM: Test card was ACCEPTED by live endpoint!")
            print("   This suggests:")
            print("   - Credentials may still be test credentials")
            print("   - Account may be in sandbox mode")
            print("   - Live endpoint may be configured incorrectly")
        elif response.status_code == 400:
            print("✅ EXPECTED: Test card was REJECTED by live endpoint")
            print("   This is the correct behavior for live mode")
        elif response.status_code == 401:
            print("❌ AUTHENTICATION: Invalid credentials for live endpoint")
        elif response.status_code == 403:
            print("❌ FORBIDDEN: Account not enabled for live payments")
        else:
            print(f"❓ UNEXPECTED: Status {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_live_api_with_test_card()
