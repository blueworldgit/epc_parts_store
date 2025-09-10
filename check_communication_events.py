#!/usr/bin/env python3
"""
Check Django Oscar communication event types
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

from oscar.core.loading import get_model

def check_communication_events():
    print("🔍 Checking Django Oscar communication event types...")
    
    try:
        CommunicationEventType = get_model('communication', 'CommunicationEventType')
        
        all_events = CommunicationEventType.objects.all()
        print(f"📧 Total communication event types: {all_events.count()}")
        
        if all_events.exists():
            print("\n📬 Available communication event types:")
            for event in all_events:
                print(f"  - Code: {event.code}")
                print(f"    Name: {event.name}")
                print(f"    Category: {event.category}")
                print(f"    Email subject template: {event.email_subject_template}")
                print("")
        else:
            print("❌ No communication event types configured!")
            print("💡 This means order confirmation emails won't be sent.")
            print("📝 You need to create communication event types for order emails.")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_communication_events()
