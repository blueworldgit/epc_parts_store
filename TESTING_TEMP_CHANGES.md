# Temporary Changes for Testing

## Free Shipping Option (REMOVE LATER)

**Files Modified**: 
1. `epcdata/epcdata/shipping_methods.py`
2. `epcdata/shipping/repository.py` (MAIN FILE USED)

**Changes Made**:
1. Updated `FreeShippingMethod` name to "Free Shipping (Testing)" in both files
2. Modified `get_available_shipping_methods()` in both files to offer free shipping to ALL users
3. Added free shipping option to the main Repository class in `shipping/repository.py`

**Lines Changed**:
- `shipping_methods.py`: Lines ~81 and ~95
- `shipping/repository.py`: Lines ~90-94 (class definition) and ~140-143 (method list)

**Reason**: To avoid card charges during testing of VAT calculations and payment flow

**⚠️ IMPORTANT**: These changes MUST be reverted before production deployment to prevent customers from getting free shipping inappropriately.

## How to Remove Later:
1. In `FreeShippingMethod` class:
   - Change name back to 'Free Shipping' 
   - Remove '(Testing)' and 'Testing purposes only' text
2. In `get_available_shipping_methods()`:
   - Add back the staff user check: `if user and user.is_staff:`
   - Remove the TODO comment about testing

---
**Created**: September 10, 2025
**Purpose**: Testing VAT calculations without card charges
**Status**: TEMPORARY - REMOVE BEFORE PRODUCTION
