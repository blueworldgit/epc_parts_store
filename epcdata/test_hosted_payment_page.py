"""
Test Worldpay Hosted Payment Pages API
Creates a payment session and gets the redirect URL
"""
import requests
import json
from base64 import b64encode

# Worldpay credentials
ENTITY_ID = "PO4080334630"
USERNAME = "2UfzfFhGOus54k5G"
PASSWORD = "FGx4t8u73n6G"

# Create Basic Auth header
credentials = f"{USERNAME}:{PASSWORD}"
encoded_credentials = b64encode(credentials.encode()).decode()

# API endpoint
url = "https://access.worldpay.com/payment_pages"

# Headers
headers = {
    "Authorization": f"Basic {encoded_credentials}",
    "Content-Type": "application/vnd.worldpay.payment_pages-v1.hal+json",
    "Accept": "application/vnd.worldpay.payment_pages-v1.hal+json"
}

# Payment request for 52p (£0.52)
payload = {
    "transactionReference": f"TEST-JASONPINK-52P",
    "merchant": {
        "entity": ENTITY_ID
    },
    "narrative": {
        "line1": "EPC Parts Store"
    },
    "value": {
        "currency": "GBP",
        "amount": 52  # 52 pence
    },
    "description": "Test payment - Jason Pink card 52p",
    "billingAddress": {
        "firstName": "Jason",
        "lastName": "Pink",
        "address1": "28-29 Bertie Ward Way",
        "address2": "Rashes Green Ind. Est.",
        "city": "Dereham",
        "state": "Norfolk",
        "postalCode": "NR19 1TE",
        "countryCode": "GB"
    },
    "resultURLs": {
        "successURL": "https://yoursite.com/payment/success",
        "pendingURL": "https://yoursite.com/payment/pending",
        "failureURL": "https://yoursite.com/payment/failure",
        "errorURL": "https://yoursite.com/payment/error",
        "cancelURL": "https://yoursite.com/payment/cancel",
        "expiryURL": "https://yoursite.com/payment/expiry"
    },
    "expiry": "1800"  # 30 minutes
}

print("=" * 80)
print("WORLDPAY HOSTED PAYMENT PAGES TEST")
print("=" * 80)
print(f"\nTransaction Reference: {payload['transactionReference']}")
print(f"Amount: £{payload['value']['amount'] / 100:.2f}")
print(f"Billing Address: {payload['billingAddress']['address1']}, {payload['billingAddress']['city']}")
print(f"Customer: {payload['billingAddress']['firstName']} {payload['billingAddress']['lastName']}")

print("\n" + "-" * 80)
print("CREATING PAYMENT SESSION...")
print("-" * 80)

try:
    response = requests.post(url, headers=headers, json=payload)
    
    print(f"\nHTTP Status: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    
    if response.status_code == 201:
        result = response.json()
        print("\n" + "=" * 80)
        print("✅ PAYMENT SESSION CREATED SUCCESSFULLY!")
        print("=" * 80)
        
        # Extract the redirect URL
        if '_links' in result and 'payment_pages:redirect' in result['_links']:
            redirect_url = result['_links']['payment_pages:redirect']['href']
            print(f"\n🔗 REDIRECT URL:")
            print(redirect_url)
            print("\n📋 Instructions:")
            print("1. Copy the URL above")
            print("2. Open it in your browser")
            print("3. Enter Jason Pink's card details:")
            print("   Card Number: 4745590025636822")
            print("   Expiry: 12/28")
            print("   CVC: 123")
            print("4. Complete the payment")
            print("\nWorldpay will handle 3DS authentication automatically!")
        
        # Show query link for checking status
        if '_links' in result and 'self' in result['_links']:
            query_url = result['_links']['self']['href']
            print(f"\n🔍 Status Query URL:")
            print(query_url)
        
        print("\n" + "-" * 80)
        print("Full Response:")
        print(json.dumps(result, indent=2))
        
    else:
        print("\n" + "=" * 80)
        print("❌ FAILED TO CREATE PAYMENT SESSION")
        print("=" * 80)
        print(f"\nResponse Body:")
        try:
            error = response.json()
            print(json.dumps(error, indent=2))
        except:
            print(response.text)

except Exception as e:
    print("\n" + "=" * 80)
    print("❌ ERROR")
    print("=" * 80)
    print(f"\n{type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
