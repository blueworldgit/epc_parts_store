#!/usr/bin/env python3
"""
Test Live Worldpay Credentials with Test Cards
This will verify that live credentials properly reject test cards
"""

import os
import sys
import django
import requests
import base64
import json
from datetime import datetime

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from django.conf import settings

def test_live_credentials_with_test_cards():
    print("🧪 Testing Live Worldpay Credentials with Test Cards")
    print("=" * 60)
    
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
    print(f"🔑 Password: {'*' * len(password)}")
    
    # Create Basic Auth
    auth_string = f"{username}:{password}"
    auth_bytes = auth_string.encode('ascii')
    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
    
    headers = {
        'Authorization': f'Basic {auth_b64}',
        'Content-Type': 'application/vnd.worldpay.payments-v6+json',
        'Accept': 'application/vnd.worldpay.payments-v6+json'
    }
    
    # Test different test cards that should be REJECTED
    test_cards = [
        {
            'name': 'Visa Test Card',
            'number': '4444333322221111',
            'description': 'Standard Worldpay test card'
        },
        {
            'name': 'Mastercard Test Card', 
            'number': '5555444433221111',
            'description': 'Mastercard test card'
        },
        {
            'name': 'Another Visa Test',
            'number': '4111111111111111', 
            'description': 'Common test card number'
        }
    ]
    
    print(f"\n🚀 Testing {len(test_cards)} test cards against live endpoint...")
    print(f"💰 Amount: £1.00")
    print(f"📍 Expected Result: All test cards should be REJECTED\n")
    
    for i, card in enumerate(test_cards, 1):
        print(f"Test {i}/3: {card['name']} ({card['description']})")
        print(f"💳 Card Number: {card['number']}")
        
        # Test payment payload
        payload = {
            "transactionReference": f"LIVE-TEST-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{i}",
            "merchant": {
                "entity": entity_id
            },
            "instruction": {
                "narrative": {
                    "line1": f"Live credential test - {card['name']}"
                },
                "value": {
                    "currency": "GBP",
                    "amount": 100  # £1.00
                },
                "paymentInstrument": {
                    "type": "card/plain",
                    "cardNumber": card['number'],
                    "expiryDate": {
                        "month": 12,
                        "year": 2025
                    },
                    "cardHolderName": "Test Cardholder",
                    "cvc": "123"
                }
            }
        }
        
        try:
            response = requests.post(
                api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            print(f"📊 Response Status: {response.status_code}")
            
            if response.content:
                try:
                    response_data = response.json()
                    print(f"📝 Response: {json.dumps(response_data, indent=2)}")
                except:
                    print(f"📝 Response (raw): {response.text}")
            
            # Analysis
            if response.status_code == 201:
                print("❌ PROBLEM: Test card was ACCEPTED!")
                print("   This suggests credentials are still in test mode")
            elif response.status_code == 400:
                if response.content:
                    try:
                        error_data = response.json()
                        if 'validation' in str(error_data).lower() or 'invalid' in str(error_data).lower():
                            print("✅ EXPECTED: Test card was REJECTED!")
                            print("   Live credentials working correctly")
                        else:
                            print("❓ UNCLEAR: 400 error but unknown reason")
                    except:
                        print("✅ LIKELY REJECTED: 400 error (card validation failed)")
                else:
                    print("✅ EXPECTED: Test card was REJECTED (400 Bad Request)")
            elif response.status_code == 401:
                print("❌ AUTHENTICATION: Invalid credentials")
            elif response.status_code == 403:
                print("❌ FORBIDDEN: Account not enabled for live payments")
            else:
                print(f"❓ UNEXPECTED: Status {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
        
        print("-" * 40)
    
    print("\n🔍 Summary:")
    print("✅ If all test cards were REJECTED: Live credentials are working correctly")
    print("❌ If any test cards were ACCEPTED: Credentials may still be in test mode")
    print("📞 If authentication failed: Contact Worldpay for correct live credentials")

if __name__ == "__main__":
    test_live_credentials_with_test_cards()
