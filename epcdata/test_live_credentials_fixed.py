#!/usr/bin/env python3
"""
Fixed Test Script for Live Worldpay API with Correct Schema
Tests if live credentials properly reject test cards
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

def test_live_credentials_with_fixed_schema():
    print("🚀 Testing Live Worldpay API with Corrected Schema")
    print("=" * 60)
    
    # Get current configuration
    api_url = getattr(settings, 'WORLDPAY_GATEWAY_URL', '')
    username = getattr(settings, 'WORLDPAY_USERNAME', '')
    password = getattr(settings, 'WORLDPAY_PASSWORD', '')
    entity_id = getattr(settings, 'WORLDPAY_ENTITY_ID', '')
    
    print(f"🎯 API URL: {api_url}")
    print(f"👤 Username: {username}")
    print(f"🆔 Entity ID: {entity_id}")
    
    # Create Basic Auth
    auth_string = f"{username}:{password}"
    auth_bytes = auth_string.encode('ascii')
    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
    
    headers = {
        'Authorization': f'Basic {auth_b64}',
        'Content-Type': 'application/vnd.worldpay.payments-v6+json',
        'Accept': 'application/vnd.worldpay.payments-v6+json'
    }
    
    # Test cards to verify rejection
    test_cards = [
        {
            "name": "Visa Test Card (Standard Worldpay test card)",
            "number": "4444333322221111",
            "expected": "REJECTED - Test card should not work with live credentials"
        },
        {
            "name": "Mastercard Test Card", 
            "number": "5555444433221111",
            "expected": "REJECTED - Test card should not work with live credentials"
        },
        {
            "name": "Another Visa Test",
            "number": "4111111111111111", 
            "expected": "REJECTED - Test card should not work with live credentials"
        }
    ]
    
    print(f"\n🔍 Testing {len(test_cards)} test cards against live endpoint...")
    print(f"💰 Amount: £1.00")
    print(f"📍 Expected Result: All test cards should be REJECTED by live API")
    print()
    
    for i, card in enumerate(test_cards, 1):
        print(f"Test {i}/{len(test_cards)}: {card['name']}")
        print(f"💳 Card Number: {card['number']}")
        
        # Corrected payload with proper schema
        payload = {
            "transactionReference": f"LIVE-TEST-{i:03d}",
            "merchant": {
                "entity": entity_id
            },
            "instruction": {
                "narrative": {
                    "line1": "Test Payment"  # Fixed: Within 1-24 characters
                },
                "value": {
                    "currency": "GBP",
                    "amount": 100  # £1.00 in pence
                },
                "paymentInstrument": {
                    "type": "card/plain",
                    "cardNumber": card['number'],
                    "cardExpiryDate": {  # Fixed: Correct field name
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
            
            # Analysis of results
            if response.status_code == 201:
                print("❌ PROBLEM: Test card was ACCEPTED by live endpoint!")
                print("   This suggests credentials may still be test credentials")
                print("   or the account is in sandbox mode")
            elif response.status_code == 400:
                error_data = response.json() if response.content else {}
                error_name = error_data.get('errorName', '')
                if 'bodyDoesNotMatchSchema' in error_name:
                    print("⚠️  Schema validation error - fixing...")
                elif 'cardNumber' in str(error_data) or 'invalid' in str(error_data).lower():
                    print("✅ EXPECTED: Test card was REJECTED by live endpoint")
                    print("   Live credentials are working correctly!")
                else:
                    print("🔍 400 Error - need to analyze response")
            elif response.status_code == 401:
                print("❌ AUTHENTICATION FAILED: Invalid live credentials")
                print("   Check with Worldpay that credentials are correct")
            elif response.status_code == 403:
                print("❌ FORBIDDEN: Account may not be enabled for live payments")
                print("   Contact Worldpay to activate live payment processing")
            else:
                print(f"❓ UNEXPECTED: Status {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
        
        print("-" * 40)
    
    print("\n🔍 Summary:")
    print("✅ If test cards show 'invalid card' or similar: Live credentials working!")
    print("❌ If test cards are processed successfully: Still using test credentials") 
    print("🔧 If schema errors: API format issues (not credential issues)")
    print("📞 If auth errors: Contact Worldpay for correct live credentials")

if __name__ == "__main__":
    test_live_credentials_with_fixed_schema()
