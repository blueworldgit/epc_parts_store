#!/usr/bin/env python3
"""
Test Live Worldpay API with Real Card
Testing with real card details to verify live processing
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

def test_real_card():
    print("🧪 Testing Live Worldpay API with REAL CARD")
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
    
    # Real card payment payload
    payload = {
        "transactionReference": "REAL-CARD-TEST-001",
        "merchant": {
            "entity": entity_id
        },
        "instruction": {
            "narrative": {
                "line1": "Real card test payment"
            },
            "value": {
                "currency": "GBP",
                "amount": 75  # £0.75
            },
            "paymentInstrument": {
                "type": "card/plain",
                "cardNumber": "5284973561659800",  # Real card number
                "cardExpiryDate": {
                    "month": 3,
                    "year": 2030
                },
                "cardHolderName": "S PILLAY",
                "cvc": "347"
            }
        }
    }
    
    print(f"\n🚀 Testing REAL CARD payment:")
    print(f"💳 Card Number: 5284-9735-6165-9800")
    print(f"📅 Expiry: 03/2030")
    print(f"👤 Cardholder: S PILLAY")
    print(f"💰 Amount: £0.75")
    print(f"🔗 Endpoint: {api_url}")
    
    try:
        print(f"\n⏳ Processing payment...")
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
                
                # Analyze the response
                print(f"\n🔍 Analysis:")
                if response.status_code == 201:
                    outcome = response_data.get('outcome', 'unknown')
                    if outcome == 'authorized':
                        print("✅ SUCCESS: Real card payment was AUTHORIZED!")
                        print("   Live mode is working correctly")
                        print("   Real money will be charged")
                    elif outcome == 'refused':
                        code = response_data.get('code', 'unknown')
                        description = response_data.get('description', 'No description')
                        print(f"❌ REFUSED: Payment declined")
                        print(f"   Code: {code}")
                        print(f"   Reason: {description}")
                        print("   This could be due to:")
                        print("   - Insufficient funds")
                        print("   - Card issuer decline")
                        print("   - Card restrictions")
                    else:
                        print(f"⚠️  UNEXPECTED: Outcome = {outcome}")
                elif response.status_code == 400:
                    print("❌ BAD REQUEST: Invalid payment data")
                elif response.status_code == 401:
                    print("❌ UNAUTHORIZED: Invalid credentials")
                elif response.status_code == 403:
                    print("❌ FORBIDDEN: Account not enabled for live payments")
                else:
                    print(f"❓ UNEXPECTED: Status {response.status_code}")
            except json.JSONDecodeError:
                print(f"📝 Response Body (raw): {response.text}")
        else:
            print("📝 No response content")
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out - Check network connection")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    
    print(f"\n📋 Summary:")
    print("✅ If AUTHORIZED: Live mode working, real payments processed")
    print("❌ If REFUSED: Check card details or account limits")
    print("🔒 If UNAUTHORIZED: Check live credentials with Worldpay")
    print("⚠️  If FORBIDDEN: Account may need live activation")

if __name__ == "__main__":
    test_real_card()
