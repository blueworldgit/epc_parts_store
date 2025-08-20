#!/usr/bin/env python3
"""
Quick Worldpay API endpoint test
"""
import requests
import json
import base64

# Your credentials
username = "evQNpTg2ScurKUxK"
password = "uIQbwozYFFlClnbfJl3vc3Zn0G5HBvg6KTtZeuXn4DqPa9m67R15Ebrq0uZhUGxm"
entity_id = "PO4080334630"

# Create auth header
credentials = f"{username}:{password}"
encoded_credentials = base64.b64encode(credentials.encode()).decode()
auth_header = f"Basic {encoded_credentials}"

print("=== WORLDPAY ENDPOINT TEST ===\n")

# Test different endpoints
endpoints = [
    "https://try.access.worldpay.com/payment-pages",  # Current facade URL (wrong)
    "https://try.access.worldpay.com/payment-pages/v1/sessions",  # Likely correct
    "https://try.access.worldpay.com/payments/hosted/sessions",  # Alternative
]

simple_payload = {
    "amount": 1000,
    "currency": "GBP",
    "description": "Test payment"
}

for endpoint in endpoints:
    print(f"Testing: {endpoint}")
    
    headers = {
        'Authorization': auth_header,
        'Content-Type': 'application/vnd.worldpay.payment_pages-v1.hal+json',
        'Accept': 'application/vnd.worldpay.payment_pages-v1.hal+json'
    }
    
    try:
        response = requests.post(
            endpoint,
            headers=headers,
            json=simple_payload,
            timeout=10
        )
        
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.text[:200]}...")
        
        if response.status_code == 201:
            print("  ✅ SUCCESS!")
        elif response.status_code == 404:
            print("  ❌ NOT FOUND - Wrong endpoint")
        elif response.status_code == 401:
            print("  ❌ UNAUTHORIZED - Auth issue")
        elif response.status_code == 400:
            print("  ❌ BAD REQUEST - Payload issue")
        
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
    
    print()
