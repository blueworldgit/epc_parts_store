#!/usr/bin/env python
"""
Test script for VAT calculation template filters using precise_money
"""
import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'epcdata'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')

django.setup()

# Import our template filters
from epcdata.templatetags.money_filters import vat_from_total, subtotal_from_total

def test_vat_calculations():
    """Test our VAT calculation filters"""
    print("🧮 Testing VAT calculation filters with precise_money")
    
    # Test case 1: £330.07 total (from user's example)
    total_inc_vat = "330.07"
    
    vat_amount = vat_from_total(total_inc_vat)
    subtotal_amount = subtotal_from_total(total_inc_vat)
    
    print(f"\n💰 Test Case 1: £{total_inc_vat} (VAT-inclusive)")
    print(f"  - Subtotal ex VAT: £{subtotal_amount}")
    print(f"  - VAT amount: £{vat_amount}")
    print(f"  - Check: £{subtotal_amount} + £{vat_amount} = £{float(subtotal_amount) + float(vat_amount):.2f}")
    
    # Test case 2: Verify math
    # If total inc VAT is £330.07, then:
    # Subtotal ex VAT = £330.07 / 1.20 = £275.058... ≈ £275.06
    # VAT = £330.07 - £275.06 = £55.01
    expected_subtotal = 330.07 / 1.20
    expected_vat = 330.07 - expected_subtotal
    
    print(f"\n🔍 Mathematical verification:")
    print(f"  - Expected subtotal: £{expected_subtotal:.2f}")
    print(f"  - Expected VAT: £{expected_vat:.2f}")
    print(f"  - Our subtotal: £{subtotal_amount}")
    print(f"  - Our VAT: £{vat_amount}")
    
    # Check if they match
    subtotal_match = abs(float(subtotal_amount) - expected_subtotal) < 0.01
    vat_match = abs(float(vat_amount) - expected_vat) < 0.01
    
    print(f"\n✅ Results:")
    print(f"  - Subtotal accuracy: {'✅ PASS' if subtotal_match else '❌ FAIL'}")
    print(f"  - VAT accuracy: {'✅ PASS' if vat_match else '❌ FAIL'}")
    
    if subtotal_match and vat_match:
        print(f"\n🎉 All tests passed! Template filters are working correctly with precise_money.")
    else:
        print(f"\n⚠️ Some tests failed. Check the calculations.")

if __name__ == "__main__":
    test_vat_calculations()
