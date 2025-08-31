#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from payment.gateway_facade import WorldpayGatewayFacade
import json

print("🔍 COMPARING CARD RESPONSES TO FIND THE DIFFERENCE")
print("=" * 70)

# The two cards
cards = {
    "WORKING_CARD": {
        "cardholder_name": "S PILLAY",
        "card_number": "5555555555554444",
        "expiry_month": "01",
        "expiry_year": "2025", 
        "cvc": "123"
    },
    "PROBLEM_CARD": {
        "cardholder_name": "JASON PINK",
        "card_number": "4444333322221111",
        "expiry_month": "01",
        "expiry_year": "2025",
        "cvc": "123"
    }
}

facade = WorldpayGatewayFacade()

for card_type, card_data in cards.items():
    print(f"\n🃏 Testing {card_type}: {card_data['cardholder_name']}")
    print(f"   Card: {card_data['card_number'][:4]}****{card_data['card_number'][-4:]}")
    print("-" * 50)
    
    try:
        # Create test order data
        class MockOrder:
            def __init__(self):
                self.number = f"TEST-{card_type}"
                self.total_incl_tax = 0.20
                self.currency = 'GBP'
                
        mock_order = MockOrder()
        
        # Process payment
        result = facade.process_payment(mock_order, card_data)
        
        print(f"   Success: {result.get('success')}")
        
        if result.get('success'):
            print(f"   ✅ Payment ID: {result.get('payment_id')}")
            
            # Get the raw response to compare structure
            if 'raw_response' in result:
                raw = result['raw_response']
                print(f"   📄 Response Keys: {list(raw.keys())}")
                
                # Check specific fields that might differ
                if 'issuer' in raw:
                    issuer = raw['issuer']
                    print(f"   🏦 Issuer Keys: {list(issuer.keys())}")
                    print(f"   🔢 Auth Code: {issuer.get('authorizationCode')}")
                    print(f"   💳 Card Scheme: {issuer.get('cardScheme')}")
                
                if 'outcome' in raw:
                    outcome = raw['outcome']
                    print(f"   🎯 Outcome: {outcome}")
                    
                # Look for any differences in response structure
                response_str = json.dumps(raw, indent=2)
                print(f"   📊 Response size: {len(response_str)} characters")
                
        else:
            print(f"   ❌ Error: {result.get('error_message')}")
            
    except Exception as e:
        print(f"   💥 Exception: {str(e)}")

print(f"\n🔍 KEY QUESTIONS TO INVESTIGATE:")
print(f"   1. Do both cards return identical response structures?")
print(f"   2. Are there subtle differences in authorization codes?")
print(f"   3. Do they have different card schemes (Visa vs Mastercard)?")
print(f"   4. Are there different outcome codes or messages?")
print(f"   5. Is there a race condition or timing issue?")
