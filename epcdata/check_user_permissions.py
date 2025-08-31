#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

print("🔍 CHECKING USER PERMISSIONS AND ADMIN STATUS")
print("=" * 60)

# Check the different users
user_ids = [1, 3]  # Your admin user vs JASON PINK

for user_id in user_ids:
    try:
        user = User.objects.get(id=user_id)
        print(f"\n👤 User ID {user_id}:")
        print(f"   Email: {user.email}")
        print(f"   Username: {getattr(user, 'username', 'N/A')}")
        print(f"   Is Staff: {user.is_staff}")
        print(f"   Is Superuser: {user.is_superuser}")
        print(f"   Is Active: {user.is_active}")
        print(f"   Date Joined: {user.date_joined}")
        
    except User.DoesNotExist:
        print(f"\n❌ User ID {user_id} not found")

print(f"\n💡 THEORY:")
print(f"   Admin/staff users might bypass certain checkout validations")
print(f"   ThankYouView might have different logic for staff vs regular users")
print(f"   Staff users might not need complete checkout session data")

print(f"\n🎯 THIS EXPLAINS:")
print(f"   - Why your admin account showed thank-you (bypassed validation)")
print(f"   - Why JASON PINK (regular user) gets redirected (failed validation)")
print(f"   - Why payment sources don't matter for admin users")

print(f"\n🔧 NEXT STEP:")
print(f"   Check Oscar's ThankYouView source code for staff user exceptions")
print(f"   Look for checkout session validation differences")
print(f"   Test with admin user vs regular user on same card")
