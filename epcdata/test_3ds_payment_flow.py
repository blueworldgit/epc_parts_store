#!/usr/bin/env python3
"""
Test complete 3DS + Payment flow with Jason Pink's card
This tests the exact flow that will happen in production
"""
import os
import sys
import django
import json
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')

try:
    django.setup()
    from django.conf import settings
    from payment.gateway_facade import WorldpayGatewayFacade
    
    print("="*60)
    print("3DS + PAYMENT FLOW TEST")
    print("="*60)
    print()
    
    # Create facade
    facade = WorldpayGatewayFacade()
    
    print(f"✅ Facade initialized")
    print(f"   Payment API: {facade.api_url}")
    print(f"   3DS API: {facade.threeds_url}")
    print()
    
    # Mock order data (you would have a real Order object)
    class MockOrder:
        number = "TEST-100001"
        currency = "GBP"
        total_incl_tax = 0.50  # £0.50
        
        class BillingAddress:
            line1 = "123 Test Street"
            line2 = ""
            line3 = ""
            line4 = "London"
            postcode = "SW1A 1AA"
            state = ""
            
            class Country:
                code = "GB"
            country = Country()
            
        billing_address = BillingAddress()
    
    order = MockOrder()
    
    # Jason Pink's card data
    card_data = {
        'card_number': '4745590025636822',
        'expiry_month': '4',
        'expiry_year': '2028',
        'cvc': '751',
        'cardholder_name': 'JASON PINK'
    }
    
    print("📋 Test Data:")
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
    
    threeds_result = facade.authenticate_3ds(order, card_data, request=None)
    
    print(f"3DS Result:")
    print(json.dumps(threeds_result, indent=2, default=str))
    print()
    
    if not threeds_result.get('success'):
        print(f"❌ 3DS Authentication Failed: {threeds_result.get('error_message')}")
        print(f"   Outcome: {threeds_result.get('outcome')}")
        sys.exit(1)
    
    print(f"✅ 3DS Authentication Successful!")
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
    
    payment_result = facade.process_payment(order, card_data, auth_data)
    
    print(f"Payment Result:")
    print(json.dumps(payment_result, indent=2, default=str))
    print()
    
    if payment_result and payment_result.get('success'):
        print(f"✅ PAYMENT SUCCESSFUL!")
        print(f"   Payment ID: {payment_result.get('payment_id')}")
        print(f"   Authorization Code: {payment_result.get('authorization_code')}")
        print()
        print("="*60)
        print("🎉 COMPLETE SUCCESS - 3DS + PAYMENT WORKING!")
        print("="*60)
    else:
        print(f"❌ PAYMENT FAILED: {payment_result.get('error_message') if payment_result else 'No result'}")
        sys.exit(1)

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
