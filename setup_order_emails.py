#!/usr/bin/env python3
"""
Create Django Oscar communication event types for order emails
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

def create_order_communication_events():
    print("🔧 Creating Django Oscar communication event types for order emails...")
    
    try:
        CommunicationEventType = get_model('communication', 'CommunicationEventType')
        
        # Order confirmation email (most important)
        order_placed, created = CommunicationEventType.objects.get_or_create(
            code='ORDER_PLACED',
            defaults={
                'name': 'Order Confirmation',
                'category': CommunicationEventType.ORDER_RELATED,
                'email_subject_template': 'Order Confirmation - Order #{{ order.number }}',
                'email_body_template': '''
Dear {{ order.user.first_name|default:"Customer" }},

Thank you for your order! We're pleased to confirm that we have received your order.

Order Details:
--------------
Order Number: {{ order.number }}
Order Date: {{ order.date_placed|date:"F j, Y" }}
Total: £{{ order.total_incl_tax }}

Items Ordered:
{% for line in order.lines.all %}
- {{ line.title }} (Qty: {{ line.quantity }}) - £{{ line.line_price_incl_tax }}
{% endfor %}

{% if order.shipping_address %}
Shipping Address:
{{ order.shipping_address.line1 }}
{% if order.shipping_address.line2 %}{{ order.shipping_address.line2 }}{% endif %}
{{ order.shipping_address.line4 }}, {{ order.shipping_address.state }} {{ order.shipping_address.postcode }}
{{ order.shipping_address.country }}
{% endif %}

We will send you another email when your order ships.

If you have any questions about your order, please contact us:
Email: sales@vanpartsdirect4u.co.uk  
Phone: 01953 665421

Thank you for shopping with us!

Van Parts Direct Team
''',
                'email_body_html_template': '''
<html>
<body>
<h2>Thank you for your order!</h2>

<p>Dear {{ order.user.first_name|default:"Customer" }},</p>

<p>Thank you for your order! We're pleased to confirm that we have received your order.</p>

<h3>Order Details</h3>
<table border="1" cellpadding="5" cellspacing="0">
    <tr><td><strong>Order Number:</strong></td><td>{{ order.number }}</td></tr>
    <tr><td><strong>Order Date:</strong></td><td>{{ order.date_placed|date:"F j, Y" }}</td></tr>
    <tr><td><strong>Total:</strong></td><td>£{{ order.total_incl_tax }}</td></tr>
</table>

<h3>Items Ordered</h3>
<table border="1" cellpadding="5" cellspacing="0">
    <tr><th>Product</th><th>Quantity</th><th>Price</th></tr>
    {% for line in order.lines.all %}
    <tr><td>{{ line.title }}</td><td>{{ line.quantity }}</td><td>£{{ line.line_price_incl_tax }}</td></tr>
    {% endfor %}
</table>

{% if order.shipping_address %}
<h3>Shipping Address</h3>
<p>
{{ order.shipping_address.line1 }}<br>
{% if order.shipping_address.line2 %}{{ order.shipping_address.line2 }}<br>{% endif %}
{{ order.shipping_address.line4 }}, {{ order.shipping_address.state }} {{ order.shipping_address.postcode }}<br>
{{ order.shipping_address.country }}
</p>
{% endif %}

<p>We will send you another email when your order ships.</p>

<p>If you have any questions about your order, please contact us:</p>
<p>
<strong>Email:</strong> sales@vanpartsdirect4u.co.uk<br>
<strong>Phone:</strong> 01953 665421
</p>

<p>Thank you for shopping with us!</p>
<p><strong>Van Parts Direct Team</strong></p>

</body>
</html>
''',
            }
        )
        
        if created:
            print("✅ Created ORDER_PLACED communication event type")
        else:
            print("ℹ️ ORDER_PLACED communication event type already exists")
        
        # Order shipped email
        order_shipped, created = CommunicationEventType.objects.get_or_create(
            code='ORDER_SHIPPED',
            defaults={
                'name': 'Order Shipped',
                'category': CommunicationEventType.ORDER_RELATED,
                'email_subject_template': 'Your Order #{{ order.number }} Has Shipped',
                'email_body_template': '''
Dear {{ order.user.first_name|default:"Customer" }},

Great news! Your order #{{ order.number }} has been shipped and is on its way to you.

Your order should arrive within 3-5 business days.

If you have any questions, please contact us:
Email: sales@vanpartsdirect4u.co.uk
Phone: 01953 665421

Thank you for shopping with us!

Van Parts Direct Team
''',
            }
        )
        
        if created:
            print("✅ Created ORDER_SHIPPED communication event type")
        else:
            print("ℹ️ ORDER_SHIPPED communication event type already exists")
        
        print("\n📧 Communication event types configured successfully!")
        print("✉️ Order confirmation emails will now be sent automatically when orders are placed.")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    create_order_communication_events()
