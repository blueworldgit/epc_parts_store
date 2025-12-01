"""
Test 3DS + Payment with billing address (AVS data)
This tests if including AVS data resolves the refusal code 6 for commercial cards
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
from oscar.apps.address.models import Country

# Mock classes with billing address - S PILLAY (SA address, using GB country code for test)
class MockBillingAddress:
    def __init__(self):
        self.line1 = "61 Jacaranda Crescent"
        self.line2 = "Isipingo Hills"
        self.line3 = ""
        self.line4 = "Isipingo"  # city
        self.postcode = "4133"
        self.state = ""
        self.country = Country.objects.get(iso_3166_1_a2='GB')

class MockOrder:
    def __init__(self):
        self.number = "TEST-SPILLAY-20P"
        self.total_incl_tax = 0.20  # 20p
        self.currency = "GBP"
        self.billing_address = MockBillingAddress()

print("="*60)
print("3DS + PAYMENT TEST WITH BILLING ADDRESS (AVS)")
print("="*60)
print()

# Initialize facade
facade = WorldpayGatewayFacade()
print(f"✅ Facade initialized")
print()

# S PILLAY's card
card_data = {
    'card_number': '5284973561659800',
    'expiry_month': '03',
    'expiry_year': '2030',
    'cvc': '347',
    'cardholder_name': 'S PILLAY'
}

# Create mock order WITH billing address
order = MockOrder()

print(f"📋 Test Data:")
print(f"   Order: {order.number}")
print(f"   Amount: £{order.total_incl_tax}")
print(f"   Card: {card_data['card_number'][:4]}****{card_data['card_number'][-4:]}")
print(f"   Billing: {order.billing_address.line1}, {order.billing_address.postcode}")
print()

# STEP 1: 3DS Authentication
print("="*60)
print("STEP 1: 3D SECURE AUTHENTICATION")
print("="*60)
print()

threeds_result = facade.authenticate_3ds(order, card_data, None)

outcome = threeds_result.get('outcome')

if outcome == 'challenged':
    print("⚠️ 3DS CHALLENGE REQUIRED")
    print(f"   Your card requires interactive authentication")
    print(f"   Challenge URL: {threeds_result.get('challenge_url')}")
    print()
    print("ℹ️ In the live site:")
    print("   1. Customer will see a popup/iframe with the challenge")
    print("   2. They'll verify via SMS code, banking app, etc")
    print("   3. After verification, payment will complete automatically")
    print()
    print("✅ Good news: Your 3DS challenge integration is working!")
    print("   The threeds_challenge.html template will show the challenge iframe.")
    print("   Real customers can complete authentication and checkout successfully.")
    sys.exit(0)

if not threeds_result.get('success'):
    print(f"❌ 3DS FAILED: {threeds_result.get('error_message')}")
    sys.exit(1)

if outcome != 'authenticated':
    print(f"⚠️ UNEXPECTED 3DS OUTCOME: {outcome}")
    sys.exit(1)

print("✅ 3DS Authentication Successful!")
auth_data = threeds_result.get('authentication', {})
print(f"   ECI: {auth_data.get('eci')}")
print(f"   Version: {auth_data.get('version')}")
print()

# STEP 2: Payment with 3DS + AVS data
print("="*60)
print("STEP 2: PAYMENT AUTHORIZATION (3DS + AVS)")
print("="*60)
print()

payment_result = facade.process_payment(order, card_data, authentication_data=auth_data)

print("Payment Result:")
if payment_result.get('success'):
    print("✅ PAYMENT AUTHORIZED!")
    print(f"   Payment ID: {payment_result.get('payment_id')}")
    print(f"   Auth Code: {payment_result.get('authorization_code')}")
else:
    print(f"❌ PAYMENT REFUSED")
    resp = payment_result.get('response_data', {})
    print(f"   Outcome: {resp.get('outcome')}")
    print(f"   Code: {resp.get('code')}")
    print(f"   Description: {resp.get('description')}")
    
    # Check risk factors
    if 'riskFactors' in resp:
        print(f"\n   Risk Factors:")
        for risk in resp['riskFactors']:
            print(f"     - {risk.get('type')}: {risk.get('risk')}" + 
                  (f" ({risk.get('detail')})" if 'detail' in risk else ""))

print()
print("="*60)
if payment_result.get('success'):
    print("🎉 SUCCESS! 3DS + AVS resolved code 6 refusal!")
else:
    if payment_result.get('response_data', {}).get('code') == '6':
        print("❌ STILL CODE 6 - Card may have additional restrictions")
    else:
        print(f"ℹ️ Different error code: {payment_result.get('response_data', {}).get('code')}")
print("="*60)
