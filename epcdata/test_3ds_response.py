"""
Simple test to see raw 3DS API response
"""
import os
import sys
import django
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from payment.gateway_facade import WorldpayGatewayFacade
from oscar.apps.address.models import Country

class MockBillingAddress:
    def __init__(self):
        self.line1 = "61 Jacaranda Crescent"
        self.line2 = "Isipingo Hills"
        self.line3 = ""
        self.line4 = "Isipingo"
        self.postcode = "4133"
        self.state = ""
        self.country = Country.objects.get(iso_3166_1_a2='GB')

class MockOrder:
    def __init__(self):
        self.number = "TEST-RESPONSE-CHECK"
        self.total_incl_tax = 0.20
        self.currency = "GBP"
        self.billing_address = MockBillingAddress()

# Initialize
facade = WorldpayGatewayFacade()
card_data = {
    'card_number': '5284973561659800',
    'expiry_month': '03',
    'expiry_year': '2030',
    'cvc': '347',
    'cardholder_name': 'S PILLAY'
}

order = MockOrder()

print("Testing 3DS authentication...")
print("="*60)

result = facade.authenticate_3ds(order, card_data, None)

print("\nRESULT:")
print(json.dumps(result, indent=2, default=str))

print("\n" + "="*60)
if 'response_data' in result:
    print("\nFULL API RESPONSE:")
    print(json.dumps(result['response_data'], indent=2))
