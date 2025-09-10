#!/usr/bin/env python3
"""
Test sending order confirmation email for existing order
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
from oscar.core.loading import get_class
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_order_email():
    print("🧪 Testing order confirmation email for order #100003-4608...")
    
    try:
        # Get the order
        order = Order.objects.get(number='100003-4608')
        print(f"📦 Found order: {order.number}")
        print(f"👤 Customer: {order.email}")
        print("📧 Sending test to: bluefieldmediasa@gmail.com")
        
        # Get communication classes
        CommunicationEventType = get_class('communication.models', 'CommunicationEventType')
        Dispatcher = get_class('communication.utils', 'Dispatcher')
        
        # Get the ORDER_PLACED event type
        event_type = CommunicationEventType.objects.get(code='ORDER_PLACED')
        print(f"📧 Found communication event: {event_type.name}")
        
        # Create dispatcher and send email
        dispatcher = Dispatcher()
        
        context = {
            'order': order,
            'user': order.user,
        }
        
        print(f"📤 Sending order confirmation email to {order.email}...")
        
        # Generate the messages first, then dispatch
        messages = event_type.get_messages(context)
        
        if messages['subject'] and (messages['body'] or messages['html']):
            dispatcher_result = dispatcher.dispatch_user_messages(
                order.user, messages
            )
            messages = [dispatcher_result] if dispatcher_result else []
        else:
            print("❌ No valid messages generated from template")
            messages = []
        
        if messages:
            print(f"✅ Order confirmation email sent successfully!")
            print(f"📧 {len(messages)} message(s) sent")
        else:
            print("❌ No messages were generated")
            
    except Order.DoesNotExist:
        print("❌ Order #100003-4608 not found")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_order_email()
