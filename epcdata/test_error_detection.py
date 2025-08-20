#!/usr/bin/env python
"""
Test script to verify enhanced test card error handling
"""

import os
import sys
import django
from django.conf import settings

# Add the project directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from payment.gateway_facade import WorldpayGatewayFacade

def test_error_detection():
    """Test the test card error detection logic"""
    facade = WorldpayGatewayFacade()
    
    # Test various error scenarios
    test_cases = [
        {
            'error_data': {'message': 'Test card not permitted in live mode'},
            'status_code': 400,
            'expected': True,
            'name': 'Direct test card message'
        },
        {
            'error_data': {'message': 'Invalid card number provided'},
            'status_code': 400,
            'expected': True,
            'name': 'Invalid card number'
        },
        {
            'error_data': {'message': 'Transaction not permitted for this card'},
            'status_code': 400,
            'expected': True,
            'name': 'Transaction not permitted'
        },
        {
            'error_data': {'errorCode': 'INVALID_CARD', 'message': 'Card rejected'},
            'status_code': 400,
            'expected': True,
            'name': 'Invalid card error code'
        },
        {
            'error_data': {'message': 'Insufficient funds'},
            'status_code': 400,
            'expected': False,
            'name': 'Regular payment error'
        },
        {
            'error_data': {'message': 'Network timeout'},
            'status_code': 500,
            'expected': False,
            'name': 'Network error'
        }
    ]
    
    print("🧪 Testing Test Card Error Detection")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        result = facade._is_test_card_error(
            test_case['error_data'], 
            test_case['status_code']
        )
        
        status = "✅ PASS" if result == test_case['expected'] else "❌ FAIL"
        print(f"{i}. {test_case['name']}: {status}")
        print(f"   Error: {test_case['error_data']}")
        print(f"   Expected: {test_case['expected']}, Got: {result}")
        print()

if __name__ == "__main__":
    test_error_detection()
