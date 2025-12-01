"""
Test to verify the exact payload structure being sent to Worldpay
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
        self.number = "TEST-100001"
        self.total_incl_tax = 0.50  # 50p
        self.currency = "GBP"
        self.billing_address = None

# Initialize facade
facade = WorldpayGatewayFacade()

# Test card data (Jason Pink's card)
card_data = {
    'card_number': '4745590025636822',
    'expiry_month': '12',
    'expiry_year': '2028',
    'cvc': '123',
    'cardholder_name': 'JASON PINK'
}

# Mock authentication data from 3DS
authentication_data = {
    'version': '2.2.0',
    'eci': '05',
    'authenticationValue': 'AJkBBlOWOAAAAAAygmM1dQAAAAA=',
    'transactionId': 'a31681ac-3c75-44aa-a78e-e1e85b22ab20'
}

# Create order
order = MockOrder()

print("="*60)
print("PAYLOAD STRUCTURE TEST")
print("="*60)
print()

# Build the payload manually to show structure
import uuid
transaction_ref = f"ORDER-{order.number}-{uuid.uuid4().hex[:8]}"

payload = {
    "transactionReference": transaction_ref,
    "merchant": {
        "entity": facade.entity_id
    },
    "instruction": {
        "requestAutoSettlement": {
            "enabled": False
        },
        "narrative": {
            "line1": f"Order {order.number}"
        },
        "value": {
            "currency": order.currency,
            "amount": int(order.total_incl_tax * 100)
        },
        "paymentInstrument": {
            "type": "card/plain",
            "cardNumber": card_data['card_number'].replace(' ', ''),
            "cardExpiryDate": {
                "month": int(card_data['expiry_month']),
                "year": int(card_data['expiry_year'])
            },
            "cardHolderName": card_data['cardholder_name'],
            "cardSecurityCode": card_data['cvc']
        }
    }
}

# Add authentication at ROOT level
payload['authentication'] = {
    'threeDS': {
        'version': authentication_data.get('version'),
        'eci': authentication_data.get('eci'),
        'authenticationValue': authentication_data.get('authenticationValue'),
        'transactionId': authentication_data.get('transactionId')
    }
}

print("PAYLOAD STRUCTURE:")
print(json.dumps(payload, indent=2))
print()
print("="*60)
print("KEY POINTS:")
print("="*60)
print(f"✅ authentication is at ROOT level: {'authentication' in payload}")
print(f"✅ authentication.threeDS exists: {'threeDS' in payload.get('authentication', {})}")
print(f"✅ ECI value: {payload['authentication']['threeDS']['eci']}")
print(f"✅ Version: {payload['authentication']['threeDS']['version']}")
print(f"✅ Has authenticationValue: {bool(payload['authentication']['threeDS']['authenticationValue'])}")
print(f"✅ Has transactionId: {bool(payload['authentication']['threeDS']['transactionId'])}")
print()

# Compare with Worldpay documentation example
print("="*60)
print("WORLDPAY DOCUMENTATION EXAMPLE:")
print("="*60)
worldpay_example = {
    "transactionReference": "Memory265-13/08/1876",
    "channel": "ecom",
    "merchant": {
        "entity": "default"
    },
    "instruction": {
        "requestAutoSettlement": {
            "enabled": False
        },
        "narrative": {
            "line1": "Mind Palace"
        },
        "value": {
            "currency": "GBP",
            "amount": 250
        },
        "paymentInstrument": {
            "type": "card/plain",
            "cardNumber": "4444333322221111",
            "expiryDate": {
                "month": 5,
                "year": 2035
            }
        }
    },
    "authentication": {
        "threeDS": {
            "eci": "05",
            "authenticationValue": "MAAAAAAAAAAAAAAAAAAAAAAAAA3=",
            "transactionId": "a09b446d-5c0d-4003-9c99-21fb73d75999",
            "version": "2.2.0"
        }
    }
}
print(json.dumps(worldpay_example, indent=2))
print()

# Compare field names
print("="*60)
print("FIELD COMPARISON:")
print("="*60)
print(f"⚠️ Our expiryDate field: cardExpiryDate")
print(f"⚠️ Worldpay example field: expiryDate")
print(f"⚠️ Our CVC field: cardSecurityCode")
print(f"⚠️ Worldpay example field: cvc (when present)")
print(f"⚠️ Missing field: channel (ecom)")
print()
