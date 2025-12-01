"""
Test to determine which Gateway API version the account supports
"""
import os
import sys
import django
import json
import requests
import base64

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from django.conf import settings

# Test both v6 and v7
username = settings.WORLDPAY_USERNAME
password = settings.WORLDPAY_PASSWORD
entity_id = settings.WORLDPAY_ENTITY_ID
api_url = "https://access.worldpay.com/payments/authorizations"

# Create auth header
credentials = f"{username}:{password}"
encoded_credentials = base64.b64encode(credentials.encode()).decode()
auth_header = f"Basic {encoded_credentials}"

# Simple test payload
payload = {
    "transactionReference": "API-VERSION-TEST-001",
    "channel": "ecom",
    "merchant": {
        "entity": entity_id
    },
    "instruction": {
        "requestAutoSettlement": {
            "enabled": False
        },
        "narrative": {
            "line1": "API Version Test"
        },
        "value": {
            "currency": "GBP",
            "amount": 10  # 10p
        },
        "paymentInstrument": {
            "type": "card/plain",
            "cardNumber": "4444333322221111",
            "expiryDate": {
                "month": 12,
                "year": 2028
            }
        }
    }
}

print("="*60)
print("GATEWAY API VERSION DETECTION")
print("="*60)
print()

# Test v7
print("Testing Gateway API v7...")
headers_v7 = {
    'Authorization': auth_header,
    'Content-Type': 'application/vnd.worldpay.payments-v7+json',
    'Accept': 'application/vnd.worldpay.payments-v7+json'
}

try:
    response = requests.post(api_url, headers=headers_v7, json=payload, timeout=30, verify=False)
    print(f"v7 Response Status: {response.status_code}")
    if response.status_code == 415:
        print("❌ v7 NOT SUPPORTED (415 Bad content type)")
    elif response.status_code in [200, 201]:
        print("✅ v7 SUPPORTED")
        print(f"Response: {response.json()}")
    else:
        print(f"⚠️ v7 Response: {response.text[:200]}")
except Exception as e:
    print(f"❌ v7 Error: {e}")

print()

# Test v6
print("Testing Gateway API v6...")
headers_v6 = {
    'Authorization': auth_header,
    'Content-Type': 'application/vnd.worldpay.payments-v6+json',
    'Accept': 'application/vnd.worldpay.payments-v6+json'
}

# Adjust payload for v6 field names
payload_v6 = payload.copy()
del payload_v6['channel']  # v6 doesn't have channel
payload_v6['instruction']['paymentInstrument']['cardExpiryDate'] = payload_v6['instruction']['paymentInstrument'].pop('expiryDate')
payload_v6['instruction']['paymentInstrument']['cardSecurityCode'] = '123'

try:
    response = requests.post(api_url, headers=headers_v6, json=payload_v6, timeout=30, verify=False)
    print(f"v6 Response Status: {response.status_code}")
    if response.status_code == 415:
        print("❌ v6 NOT SUPPORTED (415 Bad content type)")
    elif response.status_code in [200, 201]:
        print("✅ v6 SUPPORTED")
        resp_data = response.json()
        print(f"Outcome: {resp_data.get('outcome')}")
        if resp_data.get('outcome') == 'refused':
            print(f"Refusal Code: {resp_data.get('code')} - {resp_data.get('description')}")
    else:
        print(f"⚠️ v6 Response: {response.text[:200]}")
except Exception as e:
    print(f"❌ v6 Error: {e}")

print()
print("="*60)
print("CONCLUSION:")
print("="*60)
