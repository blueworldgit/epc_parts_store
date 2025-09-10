#!/usr/bin/env python3
"""
Check email records for order #100003-4608
"""
import os
import sys
from pathlib import Path

# Add the project directory to the Python path
project_dir = Path(__file__).parent / "epcdata"
sys.path.insert(0, str(project_dir))

# Load environment
import dotenv
dotenv.load_dotenv()

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')

# Initialize Django
import django
django.setup()

from oscar.apps.order.models import Order
from oscar.core.loading import get_model

# Try to get the communication models
try:
    CommunicationEventType = get_model('communication', 'CommunicationEventType')
    Email = get_model('communication', 'Email')
    COMMUNICATION_AVAILABLE = True
except:
    COMMUNICATION_AVAILABLE = False

def check_order_emails():
    print("🔍 Checking emails for order #100003-4608...")
    
    if not COMMUNICATION_AVAILABLE:
        print("❌ Communication models not available")
        return
    
    try:
        order = Order.objects.get(number='100003-4608')
        print(f"📦 Order found: {order.number}")
        print(f"👤 Customer email: {order.email}")
        print(f"📅 Order date: {order.date_placed}")
        print("")
        
        # Check if any emails exist for this user
        user_emails = Email.objects.filter(user=order.user).order_by('-date_sent')
        print(f"📧 Total emails for user: {user_emails.count()}")
        
        if user_emails.exists():
            print("\n📬 Recent emails sent to user:")
            for email in user_emails[:5]:
                print(f"  - {email.subject} ({email.date_sent})")
        else:
            print("❌ No emails found for this user")
            
        # Check all recent emails in system
        all_recent_emails = Email.objects.all().order_by('-date_sent')[:10]
        print(f"\n📫 Recent emails in system ({all_recent_emails.count()} total):")
        for email in all_recent_emails:
            print(f"  - To: {email.user.email if email.user else 'Unknown'}")
            print(f"    Subject: {email.subject}")
            print(f"    Date: {email.date_sent}")
            print("")
            
    except Order.DoesNotExist:
        print("❌ Order #100003-4608 not found")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_order_emails()
