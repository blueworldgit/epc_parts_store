#!/usr/bin/env python3
"""
Test Django processing of the JASON PINK card response
"""

import os
import sys
import django
import json

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

def test_response_parsing():
    print("🔍 Testing Django Response Parsing for JASON PINK Card")
    print("=" * 60)
    
    # This is the exact response we got from Worldpay for JASON PINK's card
    worldpay_response = {
        "outcome": "authorized",
        "paymentId": "payko-FyCh2JOtLI7Ji9YD4k0",
        "commandId": "cmdwfvjr1GtbtUH2yXsN3Ykw0",
        "riskFactors": [
            {
                "type": "avs",
                "risk": "not_supplied",
                "detail": "address"
            },
            {
                "type": "avs",
                "risk": "not_supplied",
                "detail": "postcode"
            }
        ],
        "issuer": {
            "authorizationCode": "155950"
        },
        "scheme": {
            "reference": "485238410351282"
        },
        "paymentInstrument": {
            "type": "card/plain+masked",
            "card": {
                "number": {
                    "bin": "474559",
                    "last4Digits": "6822"
                },
                "countryCode": "GB",
                "expiryDate": {
                    "month": 4,
                    "year": 2028
                },
                "brand": "visa",
                "fundingType": "deferredDebit",
                "category": "commercial",
                "issuer": {
                    "name": "ALLICA BANK LIMITED"
                }
            }
        }
    }
    
    print("📊 Simulating Django parsing:")
    
    # Extract payment details like Django code does
    payment_id = worldpay_response.get('paymentId')
    print(f"✅ Payment ID: {payment_id}")
    
    # This is where the bug might be - wrong path
    authorization_code_wrong = worldpay_response.get('paymentResponse', {}).get('authorizationCode')
    print(f"❌ Authorization Code (wrong path): {authorization_code_wrong}")
    
    # This is the correct path
    authorization_code_correct = worldpay_response.get('issuer', {}).get('authorizationCode')
    print(f"✅ Authorization Code (correct path): {authorization_code_correct}")
    
    # Card scheme parsing
    card_scheme_wrong = worldpay_response.get('paymentResponse', {}).get('cardSchemeType')
    print(f"❌ Card Scheme (wrong path): {card_scheme_wrong}")
    
    card_scheme_correct = worldpay_response.get('paymentInstrument', {}).get('card', {}).get('brand')
    print(f"✅ Card Scheme (correct path): {card_scheme_correct}")
    
    # Check outcome
    outcome = worldpay_response.get('outcome')
    print(f"📊 Outcome: {outcome}")
    
    # Simulate success check
    is_authorized = outcome == 'authorized'
    print(f"🎯 Is Authorized: {is_authorized}")
    
    print(f"\n🔍 Analysis:")
    if payment_id and is_authorized:
        print("✅ Payment should be considered successful")
        print("✅ Django should redirect to thank-you page")
    else:
        print("❌ Payment would be considered failed")
        print("❌ Django would show error and redirect")
        
    print(f"\n⚠️ Potential Issues:")
    if not authorization_code_wrong:
        print("🐛 Authorization code extraction is using wrong JSON path")
    if not card_scheme_wrong:
        print("🐛 Card scheme extraction is using wrong JSON path")
        
    print(f"\n🔧 The redirect issue might be caused by:")
    print("1. Wrong JSON path for extracting payment details")
    print("2. Exception during response parsing")
    print("3. Missing fields causing validation failures")

if __name__ == "__main__":
    test_response_parsing()
