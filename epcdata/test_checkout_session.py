"""
Test Access Checkout Session Creation
Then use the session with Payments API
"""
import requests
import json
from base64 import b64encode

# Worldpay credentials
CHECKOUT_ID = "fef2d93b-6d26-4e58-be09-cb9c6477494e"
ENTITY_ID = "PO4080334630"
USERNAME = "2UfzfFhGOus54k5G"
PASSWORD = "FGx4t8u73n6G"

# Create Basic Auth header
credentials = f"{USERNAME}:{PASSWORD}"
encoded_credentials = b64encode(credentials.encode()).decode()

print("=" * 80)
print("ACCESS CHECKOUT SESSION TEST")
print("=" * 80)
print(f"\nCheckout ID: {CHECKOUT_ID}")

# Step 1: Create a session (simulating what the JS SDK does)
# Note: In production, the JS SDK on the client does this
session_url = "https://access.worldpay.com/sessions"

session_headers = {
    "Authorization": f"Basic {encoded_credentials}",
    "Content-Type": "application/vnd.worldpay.sessions-v1.hal+json",
    "Accept": "application/vnd.worldpay.sessions-v1.hal+json"
}

# Jason Pink's card details
card_data = {
    "cardNumber": "4745590025636822",
    "cardExpiryDate": {
        "month": 12,
        "year": 2028
    },
    "cvc": "123",
    "identity": CHECKOUT_ID
}

print("\n" + "-" * 80)
print("STEP 1: Creating session from card details...")
print("-" * 80)
print(f"Card: {card_data['cardNumber'][:4]}...{card_data['cardNumber'][-4:]}")

try:
    session_response = requests.post(session_url, headers=session_headers, json=card_data)
    print(f"HTTP Status: {session_response.status_code}")
    
    if session_response.status_code in [200, 201]:
        session_result = session_response.json()
        print("✅ Session created successfully!")
        
        # Extract session href
        if '_links' in session_result and 'sessions:session' in session_result['_links']:
            session_href = session_result['_links']['sessions:session']['href']
            print(f"\n🔗 Session URL: {session_href}")
            
            # Step 2: Use session with Payments API
            print("\n" + "-" * 80)
            print("STEP 2: Using session with Payments API...")
            print("-" * 80)
            
            payment_url = "https://access.worldpay.com/payments/authorizations"
            payment_headers = {
                "Authorization": f"Basic {encoded_credentials}",
                "Content-Type": "application/vnd.worldpay.payments-v6+json",
                "Accept": "application/vnd.worldpay.payments-v6+json"
            }
            
            # Payment request using session
            payment_payload = {
                "transactionReference": "TEST-SESSION-52P",
                "merchant": {
                    "entity": ENTITY_ID
                },
                "instruction": {
                    "narrative": {
                        "line1": "EPC Parts Store"
                    },
                    "value": {
                        "currency": "GBP",
                        "amount": 52
                    },
                    "paymentInstrument": {
                        "type": "card/checkout",
                        "session": {
                            "href": session_href
                        },
                        "billingAddress": {
                            "address1": "28-29 Bertie Ward Way",
                            "address2": "Rashes Green Ind. Est.",
                            "postalCode": "NR19 1TE",
                            "city": "Dereham",
                            "state": "Norfolk",
                            "countryCode": "GB"
                        }
                    }
                }
            }
            
            print("Payment Amount: £0.52")
            print("Billing Address: Dereham, Norfolk")
            
            payment_response = requests.post(payment_url, headers=payment_headers, json=payment_payload)
            print(f"\nHTTP Status: {payment_response.status_code}")
            
            if payment_response.status_code in [200, 201]:
                payment_result = payment_response.json()
                
                outcome = payment_result.get('outcome')
                print(f"\n{'=' * 80}")
                
                if outcome == 'authorized':
                    print("✅ PAYMENT AUTHORIZED!")
                elif outcome == 'refused':
                    print("❌ PAYMENT REFUSED")
                else:
                    print(f"⚠️  PAYMENT OUTCOME: {outcome}")
                
                print(f"{'=' * 80}")
                
                # Show detailed response
                print("\nFull Payment Response:")
                print(json.dumps(payment_result, indent=2))
                
            else:
                print("\n❌ Payment request failed")
                try:
                    error = payment_response.json()
                    print(json.dumps(error, indent=2))
                except:
                    print(payment_response.text)
        
        print("\n" + "-" * 80)
        print("Session Response:")
        print(json.dumps(session_result, indent=2))
        
    else:
        print("\n❌ Failed to create session")
        try:
            error = session_response.json()
            print(json.dumps(error, indent=2))
        except:
            print(session_response.text)

except Exception as e:
    print("\n" + "=" * 80)
    print("❌ ERROR")
    print("=" * 80)
    print(f"\n{type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
