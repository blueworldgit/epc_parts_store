"""
Test 3DS + Payment with Worldpay's official 3DS test card
Card: 4000000000001000 (3DS frictionless success)
"""
import os
import sys
import django
import json

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from payment.gateway_facade import WorldpayGatewayFacade

# Mock order class
class MockOrder:
    def __init__(self):
        self.number = "TEST-100002"
        self.total_incl_tax = 0.50  # 50p
        self.currency = "GBP"
        self.billing_address = None

print("="*60)
print("3DS + PAYMENT FLOW TEST - WORLDPAY TEST CARD")
print("="*60)
print()

# Initialize facade
facade = WorldpayGatewayFacade()
print(f"✅ Facade initialized")
print(f"   Payment API: {facade.api_url}")
print(f"   3DS API: {facade.threeds_url}")
print()

# Test card data - Worldpay's official 3DS test card
card_data = {
    'card_number': '4000000000001000',  # 3DS frictionless success
    'expiry_month': '12',
    'expiry_year': '2028',
    'cvc': '123',
    'cardholder_name': 'TEST CUSTOMER'
}

# Create mock order
order = MockOrder()

print(f"📋 Test Data:")
print(f"   Order: {order.number}")
print(f"   Amount: £{order.total_incl_tax}")
print(f"   Card: {card_data['card_number'][:4]}****{card_data['card_number'][-4:]}")
print(f"   Cardholder: {card_data['cardholder_name']}")
print()

# STEP 1: 3DS Authentication
print("="*60)
print("STEP 1: 3D SECURE AUTHENTICATION")
print("="*60)
print()

threeds_result = facade.authenticate_3ds(order, card_data, None)
print("3DS Result:")
print(json.dumps(threeds_result, indent=2))
print()

if not threeds_result.get('success'):
    print(f"❌ 3DS AUTHENTICATION FAILED: {threeds_result.get('error_message')}")
    sys.exit(1)

if threeds_result.get('outcome') != 'authenticated':
    print(f"⚠️ 3DS OUTCOME: {threeds_result.get('outcome')}")
    print("Cannot proceed with payment without authenticated status")
    sys.exit(1)

print("✅ 3DS Authentication Successful!")
auth_data = threeds_result.get('authentication', {})
print(f"   ECI: {auth_data.get('eci')}")
print(f"   Version: {auth_data.get('version')}")
print(f"   Auth Value: {auth_data.get('authenticationValue')}")
print(f"   Transaction ID: {auth_data.get('transactionId')}")
print()

# STEP 2: Payment Authorization with 3DS data
print("="*60)
print("STEP 2: PAYMENT AUTHORIZATION (with 3DS data)")
print("="*60)
print()

payment_result = facade.process_payment(order, card_data, authentication_data=auth_data)
print("Payment Result:")
print(json.dumps(payment_result, indent=2))
print()

if payment_result.get('success'):
    print("✅ PAYMENT SUCCESSFUL!")
    print(f"   Payment ID: {payment_result.get('payment_id')}")
    print(f"   Authorization Code: {payment_result.get('authorization_code')}")
else:
    print(f"❌ PAYMENT FAILED: {payment_result.get('error_message')}")
    print(f"   Error Code: {payment_result.get('error_code')}")
    if 'response_data' in payment_result:
        resp = payment_result['response_data']
        if 'outcome' in resp:
            print(f"   Outcome: {resp['outcome']}")
        if 'code' in resp:
            print(f"   Refusal Code: {resp['code']}")
        if 'description' in resp:
            print(f"   Description: {resp['description']}")

print()
print("="*60)

# Check if test card worked
if payment_result.get('success'):
    print("🎉 TEST CARD SUCCESS - 3DS Integration Working!")
    print("   Issue is specific to Jason Pink's real card")
else:
    if payment_result.get('response_data', {}).get('code') == '6':
        print("⚠️ TEST CARD ALSO GETTING CODE 6!")
        print("   This means the 3DS authentication data is NOT being recognized")
        print("   by the Gateway API v6 payment endpoint")
    else:
        print("ℹ️ Different error with test card - check details above")
print("="*60)
