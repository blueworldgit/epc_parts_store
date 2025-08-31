#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from payment.gateway_facade import WorldpayGatewayFacade
from oscar.apps.order.models import Order
import requests

print("🔍 DEBUGGING: Why payment_result['success'] gives different results for different cards")
print("=" * 80)

# Test with a real recent order to understand the pattern
try:
    # Get the most recent order
    recent_order = Order.objects.latest('date_placed')
    print(f"📋 Testing with recent order: {recent_order.number}")
    print(f"   Email: {recent_order.user.email if recent_order.user else recent_order.guest_email}")
    
    # Test both cards with the same order
    cards = {
        "YOUR_CARD": {
            "cardholder_name": "S PILLAY",
            "card_number": "5555555555554444",
            "expiry_month": "01",
            "expiry_year": "2025", 
            "cvc": "123"
        },
        "JASON_PINK": {
            "cardholder_name": "JASON PINK", 
            "card_number": "4444333322221111",
            "expiry_month": "01",
            "expiry_year": "2025",
            "cvc": "123"
        }
    }
    
    facade = WorldpayGatewayFacade()
    
    for card_name, card_data in cards.items():
        print(f"\n🃏 Testing {card_name} ({card_data['card_number'][:4]}****{card_data['card_number'][-4:]})")
        print("-" * 60)
        
        try:
            # Mock the payment call to see what facade returns
            # We'll track the key decision points
            
            # Just test the API call directly to see responses
            payload = {
                "transactionReference": f"TEST_{card_name}",
                "instruction": {
                    "narrative": {
                        "line1": f"Order {recent_order.number}"
                    },
                    "value": {
                        "currency": "GBP",
                        "amount": int(recent_order.total_incl_tax * 100)
                    },
                    "paymentInstrument": {
                        "type": "card/plain",
                        "card": {
                            "cardNumber": card_data['card_number'].replace(' ', ''),
                            "expiryDate": {
                                "month": int(card_data['expiry_month']),
                                "year": int(card_data['expiry_year'])
                            },
                            "cardHolderName": card_data['cardholder_name'],
                            "cardSecurityCode": card_data['cvc']
                        }
                    }
                }
            }
            
            # Test the API response directly
            auth_header = facade._get_auth_header()
            headers = {
                'Authorization': auth_header,
                'Content-Type': 'application/vnd.worldpay.payments-v6+json',
                'Accept': 'application/vnd.worldpay.payments-v6+json'
            }
            
            print(f"   🌐 Making direct API call...")
            response = requests.post(facade.api_url, json=payload, headers=headers, timeout=30)
            
            print(f"   📊 Status Code: {response.status_code}")
            print(f"   ✅ Success condition (status == 201): {response.status_code == 201}")
            
            if response.status_code == 201:
                response_data = response.json()
                payment_id = response_data.get('paymentId')
                auth_code = response_data.get('issuer', {}).get('authorizationCode')
                print(f"   💳 Payment ID: {payment_id}")
                print(f"   🔢 Auth Code: {auth_code}")
                print(f"   ✅ SHOULD show thank-you page")
            else:
                print(f"   ❌ Error response: {response.text[:200]}")
                print(f"   ❌ SHOULD show payment form with error")
                
        except Exception as e:
            print(f"   💥 Exception: {str(e)}")
            print(f"   💥 SHOULD show payment form with error")

    print(f"\n🎯 SUMMARY:")
    print(f"   If both cards return status 201: both should show thank-you page") 
    print(f"   If both cards return different status: explains different behavior")
    print(f"   If responses are identical: there's a session/timing issue")
            
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
