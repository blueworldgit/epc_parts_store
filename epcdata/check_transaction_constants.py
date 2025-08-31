#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from oscar.apps.payment.models import Transaction

print("🔍 CHECKING TRANSACTION MODEL CONSTANTS")
print("=" * 50)

# Get all uppercase attributes (constants)
constants = [attr for attr in dir(Transaction) if attr.isupper()]
print("Available Transaction constants:")
for const in constants:
    value = getattr(Transaction, const)
    print(f"   {const} = {value}")

# Also check common transaction types
print("\nLooking for common transaction type patterns:")
all_attrs = [attr for attr in dir(Transaction) if not attr.startswith('_')]
for attr in all_attrs:
    if 'auth' in attr.lower() or 'purchase' in attr.lower() or 'sale' in attr.lower():
        value = getattr(Transaction, attr)
        print(f"   {attr} = {value}")

# Check if there are choices defined
if hasattr(Transaction, '_meta'):
    for field in Transaction._meta.fields:
        if field.name in ['txn_type', 'status'] and hasattr(field, 'choices'):
            print(f"\n{field.name} choices:")
            for choice in field.choices:
                print(f"   {choice[0]} = {choice[1]}")
