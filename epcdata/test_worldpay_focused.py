#!/usr/bin/env python3
"""
Focused Worldpay Gateway API Test - Direct Card Payment Authorization
Tests the actual Gateway API endpoint used by your payment system
"""
import os
import sys
import django
import requests
import json
import base64
import uuid
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')

try:
    django.setup()
    from django.conf import settings
    
    print("=== WORLDPAY GATEWAY API TEST (Direct Card Payment) ===\n")
    
    # Get credentials
    username = getattr(settings, 'WORLDPAY_USERNAME')
    password = getattr(settings, 'WORLDPAY_PASSWORD')
    entity_id = getattr(settings, 'WORLDPAY_ENTITY_ID')
    test_mode = getattr(settings, 'WORLDPAY_TEST_MODE', True)
    
    print(f"✅ Credentials loaded:")
    print(f"   Username: {username}")
    print(f"   Entity ID: {entity_id}")
    print(f"   Test Mode: {test_mode}\n")
    
    # Create auth header
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    auth_header = f"Basic {encoded_credentials}"
    
    # Use correct Gateway API endpoint (the one that actually works!)
    base_url = "https://try.access.worldpay.com" if test_mode else "https://access.worldpay.com"
    payment_url = f"{base_url}/payments/authorizations"
    
    print(f"🎯 Testing Gateway API endpoint: {payment_url}")
    print(f"   (This is the endpoint your payment system uses)\n")
    
    # Generate unique transaction reference
    transaction_ref = f"TEST-{uuid.uuid4().hex[:8]}"
    
    # Create test payment payload using working Gateway API v6 schema
    # Note: Gateway API v6 doesn't support 'channel' field - use 3DS API instead
    test_payload = {
        "transactionReference": transaction_ref,
        "merchant": {
            "entity": entity_id
        },
        "instruction": {
            "value": {
                "currency": "GBP",
                "amount": 50  # £0.50 in pence (50p test)
            },
            "narrative": {
                "line1": "Test payment"
            },
            "paymentInstrument": {
                "type": "card/plain",
                "cardNumber": "4745590025636822",  # Jason Pink - Live card
                "cardExpiryDate": {
                    "month": 4,
                    "year": 2028
                },
                "cardHolderName": "JASON PINK",
                "cardSecurityCode": "751"
            }
        }
    }
    
    headers = {
        'Authorization': auth_header,
        'Content-Type': 'application/vnd.worldpay.payments-v6+json',
        'Accept': 'application/vnd.worldpay.payments-v6+json'
    }
    
    print(f"📦 Live Card Payload (50p Test):")
    print(f"   Transaction Ref: {transaction_ref}")
    print(f"   Amount: £0.50")
    print(f"   Card: 4745 5900 2563 6822 (Jason Pink - LIVE)")
    print(f"   Expiry: 04/2028")
    print(f"   CVC: 751\n")
    print(f"📋 Headers: {json.dumps({k: v if k != 'Authorization' else f'{v[:20]}...' for k, v in headers.items()}, indent=2)}\n")
    
    # Make the API call
    print("🚀 Making API call to Gateway API...")
    print("   (This tests the exact endpoint and schema your payment system uses)\n")
    try:
        response = requests.post(
            payment_url,
            headers=headers,
            json=test_payload,
            timeout=30,
            verify=False  # Match your gateway_facade.py settings
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📄 Response Headers:")
        for key in ['WP-CorrelationId', 'Content-Type', 'Date']:
            if key in response.headers:
                print(f"   {key}: {response.headers[key]}")
        
        print(f"\n📝 Response Body:")
        try:
            response_data = response.json()
            print(json.dumps(response_data, indent=2))
        except:
            print(response.text)
        print()
        
        if response.status_code == 201:
            try:
                data = response.json()
                outcome = data.get('outcome')
                
                if outcome == 'authorized':
                    print("✅ SUCCESS: Payment AUTHORIZED!")
                    print(f"   Payment ID: {data.get('paymentId')}")
                    print(f"   Authorization Code: {data.get('issuer', {}).get('authorizationCode')}")
                    
                    # Show payment instrument details
                    instrument = data.get('paymentInstrument', {})
                    if instrument:
                        print(f"   Card Brand: {instrument.get('cardBrand')}")
                        print(f"   Last 4 Digits: {instrument.get('lastFour')}")
                        print(f"   Card Type: {instrument.get('fundingType')}")
                    
                    # Show available actions
                    links = data.get('_links', {})
                    if links:
                        print(f"\n   Available actions:")
                        if 'cardPayments:settle' in links:
                            print(f"      - Settle payment")
                        if 'cardPayments:cancel' in links:
                            print(f"      - Cancel payment")
                    
                    print(f"\n🎉 This is the same successful response your payment system gets!")
                    
                elif outcome == 'refused':
                    print("❌ PAYMENT REFUSED")
                    refusal = data.get('refusal', {})
                    print(f"   Refusal Code: {refusal.get('refusalCode')}")
                    print(f"   Description: {refusal.get('refusalDescription')}")
                    
                else:
                    print(f"⚠️ UNEXPECTED OUTCOME: {outcome}")
                    
            except Exception as e:
                print(f"⚠️ Could not parse response details: {e}")
                
        elif response.status_code == 401:
            print("❌ AUTHENTICATION ERROR")
            print("   - Check your username/password")
            print("   - Verify credentials in Worldpay dashboard")
            print("   - Ensure credentials have Gateway API access")
        elif response.status_code == 403:
            print("❌ FORBIDDEN ERROR")
            print("   - Check entity ID is correct")
            print("   - Verify Gateway API is enabled for your entity")
            print("   - Check permissions in Worldpay dashboard")
        elif response.status_code == 400:
            print("❌ BAD REQUEST ERROR")
            print("   - Check payload format matches API v6 schema")
            print("   - Verify all required fields are present")
        elif response.status_code == 404:
            print("❌ ENDPOINT NOT FOUND")
            print("   - This means the Gateway API endpoint doesn't exist")
            print("   - Check if your account has Gateway API access enabled")
        else:
            print(f"❌ UNEXPECTED ERROR: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT ERROR: Request timed out after 30 seconds")
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR: Could not connect to Worldpay")
        print("   - Check your internet connection")
        print("   - Verify Worldpay API is not down")
    except Exception as e:
        print(f"❌ REQUEST ERROR: {e}")
        import traceback
        traceback.print_exc()

    # ============================================================
    # TEST 2: 3D SECURE IMPLEMENTATION TEST (Proper 3DS API)
    # ============================================================
    print("\n" + "="*60)
    print("TEST 2: 3D SECURE (3DS) AUTHENTICATION")
    print("="*60 + "\n")
    
    print("🔒 Testing Proper 3DS Authentication Endpoint (API v3)")
    print("   Endpoint: /verifications/customers/3ds/authentication")
    print("   This is the CORRECT way to do 3DS with Worldpay\n")
    
    # Use proper 3DS authentication endpoint (v3 API)
    threeDS_url = f"{base_url}/verifications/customers/3ds/authentication"
    threeDS_ref = f"3DS-{uuid.uuid4().hex[:8]}"
    
    print(f"📍 Endpoint: {threeDS_url}")
    print(f"📋 Reference: {threeDS_ref}\n")
    
    # Build proper 3DS authentication payload (v3 API format)
    # Using Jason Pink's real card (commercial card that requires 3DS)
    threeDS_payload = {
        "transactionReference": threeDS_ref,
        "merchant": {
            "entity": entity_id
        },
        "instruction": {
            "paymentInstrument": {
                "type": "card/front",
                "cardHolderName": "JASON PINK",
                "cardNumber": "4745590025636822",  # Jason Pink's live commercial card
                "cardExpiryDate": {
                    "month": 4,
                    "year": 2028
                },
                "billingAddress": {
                    "address1": "123 Test Street",
                    "postalCode": "SW1A 1AA",
                    "city": "London",
                    "countryCode": "GB"
                }
            },
            "value": {
                "currency": "GBP",
                "amount": 50  # £0.50
            }
        },
        "deviceData": {
            "acceptHeader": "text/html",
            "userAgentHeader": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "browserLanguage": "en-GB",
            "browserJavaEnabled": False,
            "browserColorDepth": "24",
            "browserScreenHeight": 1080,
            "browserScreenWidth": 1920,
            "timeZone": "0",
            "browserJavascriptEnabled": True,
            "ipAddress": "192.168.1.1"
        },
        "challenge": {
            "windowSize": "600x400",
            "preference": "noPreference",
            "returnUrl": "http://localhost:8000/payment/success"
        }
    }
    
    # Update headers for 3DS API v3
    threeDS_headers = {
        'Authorization': auth_header,
        'Content-Type': 'application/vnd.worldpay.verifications.customers-v3.hal+json',
        'Accept': 'application/vnd.worldpay.verifications.customers-v3.hal+json'
    }
    
    print("📦 3DS Authentication Payload:")
    print(json.dumps(threeDS_payload, indent=2))
    print()
    
    print("📋 3DS API Headers:")
    print(f"   Content-Type: {threeDS_headers['Content-Type']}")
    print(f"   Accept: {threeDS_headers['Accept']}\n")
    
    try:
        print("🚀 Making 3DS authentication request...\n")
        threeDS_response = requests.post(
            threeDS_url,
            headers=threeDS_headers,
            json=threeDS_payload,
            timeout=30,
            verify=False
        )
        
        print(f"📊 Response Status: {threeDS_response.status_code}")
        print(f"📄 Response Headers:")
        for key in ['WP-CorrelationId', 'Content-Type', 'Date']:
            if key in threeDS_response.headers:
                print(f"   {key}: {threeDS_response.headers[key]}")
        print()
        
        if threeDS_response.status_code in [200, 201]:
            threeDS_data = threeDS_response.json()
            print("📝 3DS Authentication Response:")
            print(json.dumps(threeDS_data, indent=2))
            print()
            
            outcome = threeDS_data.get('outcome')
            
            if outcome == 'authenticated':
                print("✅ 3DS AUTHENTICATION SUCCESSFUL (Frictionless)")
                print("   No challenge required - card authenticated!")
                
                # Extract 3DS data for payment authorization
                auth_data = threeDS_data.get('authentication', {})
                eci = auth_data.get('eci')
                auth_value = auth_data.get('authenticationValue')
                trans_id = auth_data.get('transactionId')
                version = auth_data.get('version')
                
                print(f"\n🔐 3DS Authentication Data (for payment authorization):")
                print(f"   ECI: {eci}")
                print(f"   Authentication Value: {auth_value}")
                print(f"   Transaction ID: {trans_id}")
                print(f"   3DS Version: {version}")
                print("\n   💡 Use this data in your payment authorization request!")
                print("   💡 This provides liability shift protection!")
                    
            elif outcome == 'challenged':
                print("⚠️ 3DS CHALLENGE REQUIRED")
                print("   User must complete step-up authentication")
                challenge_url = threeDS_data.get('_links', {}).get('3ds:challenge', {}).get('href')
                if challenge_url:
                    print(f"   Challenge URL: {challenge_url}")
                print("   After challenge, call verification endpoint to get auth data")
                
            elif outcome == 'authenticationFailed':
                print("❌ 3DS AUTHENTICATION FAILED")
                print("   Card authentication was rejected by issuer")
                
            elif outcome == 'unavailable':
                print("⚠️ 3DS AUTHENTICATION UNAVAILABLE")
                print("   3DS not available for this card/issuer")
                
            else:
                print(f"❓ OUTCOME: {outcome}")
                
        elif threeDS_response.status_code == 400:
            print("❌ BAD REQUEST - Schema Error")
            print("   The payload doesn't match 3DS API v3 schema")
            try:
                error_data = threeDS_response.json()
                print(f"\n📝 Error Response:")
                print(json.dumps(error_data, indent=2))
            except:
                print(f"   Raw response: {threeDS_response.text}")
                
        elif threeDS_response.status_code == 401:
            print("❌ AUTHENTICATION ERROR")
            print("   Check credentials have access to 3DS API")
            print("   You may need to enable 3DS in your Worldpay account")
            
        elif threeDS_response.status_code == 403:
            print("❌ FORBIDDEN - 3DS API Access Denied")
            print("   Your account may not have 3DS API enabled")
            print("   Contact Worldpay to enable 3DS product")
            
        else:
            print(f"❌ UNEXPECTED STATUS: {threeDS_response.status_code}")
            try:
                error_data = threeDS_response.json()
                print(f"   Response: {json.dumps(error_data, indent=2)}")
            except:
                print(f"   Response: {threeDS_response.text}")
            
    except Exception as e:
        print(f"❌ 3DS REQUEST ERROR: {e}")
        import traceback
        traceback.print_exc()

except Exception as e:
    print(f"❌ Django setup error: {e}")
    import traceback
    traceback.print_exc()
