#!/usr/bin/env python3
"""
Update Django Oscar communication event templates to fix currency filter issue
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

def update_email_templates():
    print("🔧 Updating Django Oscar communication event templates...")
    
    try:
        CommunicationEventType = get_model('communication', 'CommunicationEventType')
        
        # Update ORDER_PLACED template
        order_placed = CommunicationEventType.objects.get(code='ORDER_PLACED')
        
        order_placed.email_body_template = '''
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
'''

        order_placed.email_body_html_template = '''
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
'''
        
        order_placed.save()
        print("✅ Updated ORDER_PLACED email templates")
        
        print("\n📧 Email templates updated successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    update_email_templates()
