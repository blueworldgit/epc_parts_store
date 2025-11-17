#!/usr/bin/env python
"""
Test script to send order confirmation email
Usage: python manage.py shell < test_order_confirmation_email.py
"""

import os
import django
from datetime import datetime
from decimal import Decimal
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from oscar.core.loading import get_model

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

User = get_user_model()
Product = get_model('catalogue', 'Product')
Order = get_model('order', 'Order')
Line = get_model('order', 'Line')

def create_test_email():
    """Create and send a test order confirmation email"""
    
    # Create a mock user
    class MockUser:
        first_name = "Test"
        last_name = "Customer"
        email = "bluefieldmediasa@gmail.com"
    
    # Create mock address
    class MockAddress:
        first_name = "Test"
        last_name = "Customer"
        line1 = "123 Test Street"
        line2 = "Apt 4B"
        line4 = "London"
        postcode = "SW1A 1AA"
    
    # Create mock product and line - Simulating part #C00098945
    class MockProduct:
        title = "SENSOR—TIRE PRESSURE MOTOR"
        upc = "C00098945"
        
        def get_product_class(self):
            class MockProductClass:
                slug = "motor-part"
            return MockProductClass()
        
        # Simulate weight attribute for shipping calculation
        class MockAttr:
            weight = 15.5  # 15.5kg - falls in first weight band (0-24.9kg = £11.95)
        
        attr = MockAttr()
    
    class MockLine:
        def __init__(self):
            self.product = MockProduct()
            self.quantity = 2  # 2 units of 15.5kg each = 31kg total
            self.line_price_incl_tax = Decimal('89.98')  # £44.99 each × 2
    
    # Create mock order with realistic weight-based shipping
    # 31kg total weight falls in 25-49.9kg bracket = £23.90 shipping
    class MockOrder:
        number = "VAN-20251113-001"
        date_placed = datetime.now()
        total_incl_tax = Decimal('113.88')  # Products £89.98 + Shipping £23.90
        shipping_incl_tax = Decimal('23.90')  # Weight-based shipping for 31kg
    
    # Create test data
    user = MockUser()
    order = MockOrder()
    lines = [MockLine()]
    billing_address = MockAddress()
    shipping_address = MockAddress()
    
    # Prepare email context
    context = {
        'user': user,
        'order': order,
        'lines': lines,
        'billing_address': billing_address,
        'shipping_address': shipping_address,
    }
    
    # Render email templates
    html_content = render_to_string('oscar/emails/order_confirmation_body.html', context)
    text_content = render_to_string('oscar/emails/order_confirmation_body.txt', context)
    
    # Create email
    subject = f'Order Confirmation - {order.number}'
    from_email = 'noreply@vanparts-direct.co.uk'  # Update with your actual from email
    to_email = ['bluefieldmediasa@gmail.com']
    
    # Create the email message
    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=from_email,
        to=to_email
    )
    
    # Attach HTML content
    msg.attach_alternative(html_content, "text/html")
    
    try:
        # Send the email
        msg.send()
        print(f"✅ Test email sent successfully to {to_email[0]}")
        print(f"📧 Subject: {subject}")
        print(f"📦 Order Number: {order.number}")
        print(f"💰 Total: £{order.total_incl_tax}")
        print("🔍 Check your email inbox for the test order confirmation!")
        
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        print("Please check your email settings in Django settings.py")

if __name__ == "__main__":
    create_test_email()