"""
Order confirmation email signals for Django Oscar
Sends email confirmations when orders are successfully placed and paid
"""

from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from oscar.apps.order.signals import order_placed
# Note: payment_successful signal might not exist in all Oscar versions
# We'll use order status changes instead
from oscar.apps.order.abstract_models import AbstractOrder
from oscar.core.loading import get_model
import logging

# Get Oscar models
Order = get_model('order', 'Order')
PaymentEvent = get_model('order', 'PaymentEvent')

logger = logging.getLogger(__name__)

@receiver(order_placed)
def send_order_confirmation_email(sender, order, user, **kwargs):
    """
    Send order confirmation email when an order is placed
    This will be triggered when an order is successfully placed and paid
    """
    try:
        # Get customer email
        customer_email = order.email
        if not customer_email and user and user.email:
            customer_email = user.email
            
        if not customer_email:
            logger.warning(f"No email found for order {order.number}")
            return
            
        # Prepare email context
        context = {
            'order': order,
            'user': user,
            'lines': order.lines.all(),
            'billing_address': order.billing_address,
            'shipping_address': order.shipping_address,
            'site_name': getattr(settings, 'OSCAR_SHOP_NAME', 'EPC Parts Store'),
            'shop_tagline': getattr(settings, 'OSCAR_SHOP_TAGLINE', 'Your trusted motor parts supplier'),
        }
        
        # Render email templates
        subject = render_to_string('oscar/emails/order_confirmation_subject.txt', context).strip()
        body_text = render_to_string('oscar/emails/order_confirmation_body.txt', context)
        body_html = render_to_string('oscar/emails/order_confirmation_body.html', context)
        
        # Create and send email
        from_email = getattr(settings, 'OSCAR_FROM_EMAIL', settings.DEFAULT_FROM_EMAIL)
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=body_text,
            from_email=from_email,
            to=[customer_email]
        )
        email.attach_alternative(body_html, "text/html")
        email.send()
        
        logger.info(f"Order confirmation email sent for order {order.number} to {customer_email}")
        
    except Exception as e:
        logger.error(f"Failed to send order confirmation email for order {order.number}: {e}")

def send_custom_order_email(order, template_prefix, extra_context=None):
    """
    Generic function to send custom order emails
    """
    try:
        # Get customer email
        customer_email = order.email
        if not customer_email and order.user and order.user.email:
            customer_email = order.user.email
            
        if not customer_email:
            logger.warning(f"No email found for order {order.number}")
            return False
            
        # Prepare base context
        context = {
            'order': order,
            'user': order.user,
            'lines': order.lines.all(),
            'billing_address': order.billing_address,
            'shipping_address': order.shipping_address,
            'site_name': getattr(settings, 'OSCAR_SHOP_NAME', 'EPC Parts Store'),
            'shop_tagline': getattr(settings, 'OSCAR_SHOP_TAGLINE', 'Your trusted motor parts supplier'),
        }
        
        # Add extra context if provided
        if extra_context:
            context.update(extra_context)
        
        # Render email templates
        subject = render_to_string(f'oscar/emails/{template_prefix}_subject.txt', context).strip()
        body_text = render_to_string(f'oscar/emails/{template_prefix}_body.txt', context)
        body_html = render_to_string(f'oscar/emails/{template_prefix}_body.html', context)
        
        # Create and send email
        from_email = getattr(settings, 'OSCAR_FROM_EMAIL', settings.DEFAULT_FROM_EMAIL)
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=body_text,
            from_email=from_email,
            to=[customer_email]
        )
        email.attach_alternative(body_html, "text/html")
        email.send()
        
        logger.info(f"Custom email ({template_prefix}) sent for order {order.number} to {customer_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send custom email ({template_prefix}) for order {order.number}: {e}")
        return False
