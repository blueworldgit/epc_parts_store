#!/usr/bin/env python3
"""
Enhanced Test Script for Debugging Card-Specific Issues
This will capture detailed response data to diagnose redirect problems
"""

import os
import sys
import django
import requests
import base64
import json
from decimal import Decimal
from datetime import datetime

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from django.conf import settings

def test_problematic_card(card_number, expiry_month, expiry_year, cardholder_name, cvc):
    print("🔍 ENHANCED CARD TESTING - DEBUGGING REDIRECT ISSUE")
    print("=" * 60)
    print(f"🕐 Test Time: {datetime.now()}")
    
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
    
    # Generate unique transaction reference
    transaction_ref = f"DEBUG-CARD-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    # Test payment payload
    payload = {
        "transactionReference": transaction_ref,
        "merchant": {
            "entity": entity_id
        },
        "instruction": {
            "narrative": {
                "line1": "Redirect debug test"
            },
            "value": {
                "currency": "GBP",
                "amount": 21  # 21 pence as requested
            },
            "paymentInstrument": {
                "type": "card/plain",
                "cardNumber": card_number,
                "cardExpiryDate": {
                    "month": int(expiry_month),
                    "year": int(expiry_year)
                },
                "cardHolderName": cardholder_name,
                "cvc": cvc
            }
        }
    }
    
    print(f"\n🧪 Testing Card Details:")
    print(f"💳 Card Number: {card_number[:4]}-****-****-{card_number[-4:]}")
    print(f"📅 Expiry: {int(expiry_month):02d}/{expiry_year}")
    print(f"👤 Cardholder: {cardholder_name}")
    print(f"💰 Amount: £0.21 (21 pence)")
    print(f"🔖 Transaction Ref: {transaction_ref}")
    
    print(f"\n📨 Request Details:")
    print(f"🎯 Endpoint: {api_url}")
    print(f"📋 Headers: {json.dumps(dict(headers), indent=2)}")
    print(f"📦 Payload: {json.dumps(payload, indent=2)}")
    
    try:
        print(f"\n⏳ Processing payment...")
        response = requests.post(
            api_url,
            headers=headers,
            json=payload,
            timeout=10  # Shorter timeout
        )
        
        print(f"\n📊 RESPONSE ANALYSIS:")
        print(f"🔢 Status Code: {response.status_code}")
        print(f"📏 Content Length: {len(response.content) if response.content else 0} bytes")
        
        # Capture ALL response headers
        print(f"\n📋 Response Headers:")
        for header_name, header_value in response.headers.items():
            print(f"   {header_name}: {header_value}")
        
        # Capture response content
        if response.content:
            try:
                response_data = response.json()
                print(f"\n📝 Response JSON:")
                print(json.dumps(response_data, indent=2))
                
                # Detailed analysis
                print(f"\n🔍 DETAILED ANALYSIS:")
                if response.status_code == 201:
                    outcome = response_data.get('outcome', 'unknown')
                    payment_id = response_data.get('paymentId', 'N/A')
                    
                    print(f"✅ HTTP 201 Created - Payment processed")
                    print(f"🎯 Payment ID: {payment_id}")
                    print(f"📊 Outcome: {outcome}")
                    
                    if outcome == 'authorized':
                        print(f"💚 AUTHORIZED: Payment successful")
                        
                        # Check for any redirect-related fields
                        print(f"\n🔍 Checking for redirect indicators:")
                        
                        # Look for common redirect fields
                        redirect_fields = ['redirectUrl', 'redirect_url', 'nextAction', 'action', 'threeDSecure']
                        for field in redirect_fields:
                            if field in response_data:
                                print(f"   🔗 {field}: {response_data[field]}")
                        
                        # Check for 3D Secure or additional authentication
                        if 'paymentResponse' in response_data:
                            payment_response = response_data['paymentResponse']
                            print(f"   💳 Payment Response: {json.dumps(payment_response, indent=4)}")
                            
                            if 'threeDSecure' in payment_response:
                                print(f"   🔐 3D Secure detected: {payment_response['threeDSecure']}")
                            
                            if 'riskScore' in payment_response:
                                print(f"   ⚠️ Risk Score: {payment_response['riskScore']}")
                        
                        # Check for any additional processing requirements
                        if 'links' in response_data:
                            print(f"   🔗 Links: {response_data['links']}")
                            
                    elif outcome == 'refused':
                        code = response_data.get('code', 'unknown')
                        description = response_data.get('description', 'No description')
                        print(f"❌ REFUSED: {code} - {description}")
                        
                    elif outcome == 'sentForAuthorization':
                        print(f"⏳ PENDING: Sent for authorization (3D Secure or additional checks)")
                        # This might be causing the redirect!
                        if 'redirectUrl' in response_data:
                            print(f"   🔗 Redirect URL: {response_data['redirectUrl']}")
                        
                    else:
                        print(f"❓ UNKNOWN OUTCOME: {outcome}")
                        
                elif response.status_code == 202:
                    print(f"⏳ HTTP 202 Accepted - Payment pending additional authentication")
                    # This could be 3D Secure
                    
                elif response.status_code == 400:
                    print(f"❌ HTTP 400 Bad Request")
                    error_code = response_data.get('code', 'unknown')
                    error_desc = response_data.get('description', 'No description')
                    print(f"   Error: {error_code} - {error_desc}")
                    
                elif response.status_code == 401:
                    print(f"❌ HTTP 401 Unauthorized: Invalid credentials")
                    
                elif response.status_code == 403:
                    print(f"❌ HTTP 403 Forbidden: Account restrictions")
                    
                else:
                    print(f"❓ Unexpected HTTP {response.status_code}")
                
            except json.JSONDecodeError:
                print(f"\n📝 Response Body (Raw Text):")
                print(response.text)
                print(f"\n⚠️ Could not parse JSON response")
        else:
            print(f"\n📭 No response content")
            
    except requests.exceptions.Timeout:
        print(f"❌ Request timed out after 30 seconds")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    
    print(f"\n📋 SUMMARY:")
    print(f"🎯 This test shows exactly what Worldpay returns for this card")
    print(f"🔍 Look for 'sentForAuthorization' or '3D Secure' indicators")
    print(f"🔗 Any redirect URLs or additional authentication requirements")
    print(f"⚠️ Cards requiring 3D Secure may cause redirect behavior")
    print(f"\n" + "=" * 60)

def main():
    """
    Main function to test a specific card
    """
    print("📋 Please provide the card details that are causing redirect issues:")
    
    # You can either provide the details here or I can add them when you give them to me
    # For now, using placeholder that you can replace
    
    card_number = input("💳 Card Number (16 digits): ").replace(" ", "").replace("-", "")
    expiry_month = input("📅 Expiry Month (MM): ")
    expiry_year = input("📅 Expiry Year (YYYY): ")
    cardholder_name = input("👤 Cardholder Name: ")
    cvc = input("🔐 CVC: ")
    
    test_problematic_card(card_number, expiry_month, expiry_year, cardholder_name, cvc)

if __name__ == "__main__":
    # Testing the specific card causing redirect issues
    # Card: 4745 5900 2563 6822, Exp: 04/28, Name: JASON PINK, CVC: 751
    # Amount: 21 pence
    test_problematic_card("4745590025636822", "4", "2028", "JASON PINK", "751")
