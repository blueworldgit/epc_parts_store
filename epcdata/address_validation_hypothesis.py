#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

print("🔍 HYPOTHESIS: Address validation affects payment response handling")
print("=" * 70)

# The key differences I noticed:
print("📍 ADDRESS COMPARISON:")
print("   WORKING (Your card):")
print("   - Durban, South Africa (but country shows UK)")
print("   - Postcode: NR161PH (appears to be UK format but for SA address)")
print("   - Name: SHANE PILLAY")
print("")
print("   PROBLEMATIC (JASON PINK):")
print("   - Norwich, UK (legitimate UK address)")
print("   - Postcode: NR152WH / NR15 2WH (legitimate UK postcode)")
print("   - Name: Jason Pink")

print("\n🤔 SUSPICIOUS PATTERN:")
print("   Your 'working' address is actually a SA address with UK postcode")
print("   JASON PINK has a legitimate UK address with proper UK postcode")
print("   Worldpay might handle these validation scenarios differently")

print("\n💡 POSSIBLE EXPLANATIONS:")
print("   1. Worldpay address validation is more strict for proper UK addresses")
print("   2. Invalid address combinations (SA address + UK postcode) skip validation")
print("   3. Address validation warnings vs errors are handled differently")
print("   4. Different response structures for address validation issues")

print("\n🔧 SOLUTION APPROACHES:")
print("   1. Check if removing billing address from API call fixes JASON PINK")
print("   2. Add comprehensive address validation error handling")
print("   3. Test with standardized addresses for both cards")
print("   4. Log the exact Worldpay responses for both address types")

print("\n🎯 IMMEDIATE TEST:")
print("   Try JASON PINK card with your address details to see if it works")
print("   Or try your card with JASON PINK's address to see if it breaks")
