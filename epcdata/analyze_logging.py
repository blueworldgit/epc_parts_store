#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

import logging

# Create a simple test to see what's in the Django logs
logger = logging.getLogger(__name__)

print("🔍 CHECKING DJANGO LOGS FOR PAYMENT PROCESSING")
print("=" * 60)

# Check if there are any log files
log_files = []
for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith('.log'):
            log_files.append(os.path.join(root, file))

print(f"📄 Found log files: {len(log_files)}")
for log_file in log_files:
    print(f"   - {log_file}")

# Since we know both your card and JASON PINK card have the same outcome
# (no payment sources), but different redirect behavior, let's investigate
# what could cause this difference

print(f"\n💡 THEORY ABOUT DIFFERENT REDIRECT BEHAVIOR:")
print(f"   1. Your card: Payment processing fails, but session/redirect works")  
print(f"   2. JASON PINK: Payment processing fails, AND redirect fails")
print(f"   3. The difference is NOT in the payment success/failure")
print(f"   4. The difference is in the ERROR HANDLING paths")

print(f"\n🔍 NEXT STEPS TO FIND THE REAL DIFFERENCE:")
print(f"   1. Add temporary logging to capture the exact flow")
print(f"   2. Check what happens in the 'else' clause when payment fails")
print(f"   3. Look for different exception handling paths")
print(f"   4. Test both cards with detailed logging")

print(f"\n🎯 KEY INSIGHT:")
print(f"   Both cards are failing payment processing (no payment sources created)")
print(f"   But the failure handling is different between the two cards")
print(f"   Need to check the error path logic in gateway_views.py")
