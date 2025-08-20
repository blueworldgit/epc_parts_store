#!/usr/bin/env python3
"""
Check Worldpay Payment Status and Settlement
"""

import os
import sys
import django
import requests
import base64
import json

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from django.conf import settings

def check_payment_status():
    print("🔍 Checking Payment Status and Settlement Options")
    print("=" * 60)
    
    # Get current configuration
    username = getattr(settings, 'WORLDPAY_USERNAME', '')
    password = getattr(settings, 'WORLDPAY_PASSWORD', '')
    
    # Create Basic Auth
    auth_string = f"{username}:{password}"
    auth_bytes = auth_string.encode('ascii')
    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
    
    headers = {
        'Authorization': f'Basic {auth_b64}',
        'Content-Type': 'application/vnd.worldpay.payments-v6+json',
        'Accept': 'application/vnd.worldpay.payments-v6+json'
    }
    
    # Payment ID from the previous test
    payment_id = "payllXw50h4_a5x2uUG2dtzT0"
    
    print(f"💳 Payment ID: {payment_id}")
    print(f"💰 Amount: £0.75")
    
    # Check payment events/status
    events_url = f"https://access.worldpay.com/payments/events/{payment_id}"
    
    try:
        print(f"\n🔍 Checking payment events...")
        response = requests.get(events_url, headers=headers, timeout=30)
        
        print(f"📊 Events Response Status: {response.status_code}")
        
        if response.content:
            try:
                events_data = response.json()
                print(f"📝 Events Response: {json.dumps(events_data, indent=2)}")
                
                # Check if payment has been settled
                if 'events' in events_data:
                    events = events_data['events']
                    settled = any(event.get('type') == 'payment.settled' for event in events)
                    
                    if settled:
                        print("✅ Payment has been SETTLED - money should appear in bank")
                    else:
                        print("⏳ Payment is AUTHORIZED but not yet SETTLED")
                        print("   This is why it's not showing in your bank account")
                        
            except json.JSONDecodeError:
                print(f"📝 Events Response (raw): {response.text}")
                
    except Exception as e:
        print(f"❌ Failed to check events: {e}")
    
    # Try to settle the payment manually
    settle_url = f"https://access.worldpay.com/payments/settlements/full"
    settle_payload = {
        "transactionReference": "SETTLE-REAL-CARD-001",
        "paymentId": payment_id
    }
    
    print(f"\n💰 Attempting to settle payment manually...")
    
    try:
        settle_response = requests.post(
            settle_url,
            headers=headers,
            json=settle_payload,
            timeout=30
        )
        
        print(f"📊 Settlement Response Status: {settle_response.status_code}")
        
        if settle_response.content:
            try:
                settle_data = settle_response.json()
                print(f"📝 Settlement Response: {json.dumps(settle_data, indent=2)}")
                
                if settle_response.status_code == 201:
                    print("✅ Payment SETTLED successfully!")
                    print("   Money should now be charged to your card")
                    print("   Check your bank account in 1-3 business days")
                else:
                    print("⚠️  Settlement may have failed or already been processed")
                    
            except json.JSONDecodeError:
                print(f"📝 Settlement Response (raw): {settle_response.text}")
                
    except Exception as e:
        print(f"❌ Failed to settle payment: {e}")
    
    print(f"\n📋 Summary:")
    print("🔹 AUTHORIZATION: Reserves funds (immediate)")
    print("🔹 SETTLEMENT: Actually charges the card (can take time)")
    print("🔹 BANK POSTING: When it appears in your account (1-3 days)")
    print("\n💡 If still not showing:")
    print("1. Wait 24-48 hours for automatic settlement")
    print("2. Check your Worldpay merchant dashboard")
    print("3. Contact Worldpay support about settlement settings")

if __name__ == "__main__":
    check_payment_status()
