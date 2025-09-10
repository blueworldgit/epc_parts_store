"""
Signal handlers for order-related emails
"""
from django.dispatch import receiver
from oscar.apps.order.signals import order_placed
from oscar.core.loading import get_class
import logging

logger = logging.getLogger(__name__)

# Get Oscar's communication classes
CommunicationEventType = get_class('communication.models', 'CommunicationEventType')
Dispatcher = get_class('communication.utils', 'Dispatcher')

@receiver(order_placed)
def send_order_confirmation_email(sender, order, user, **kwargs):
    """
    Send order confirmation email when an order is placed.
    """
    try:
        logger.info(f"Order placed signal received for order {order.number}")
        
        # Get the ORDER_PLACED communication event type
        try:
            event_type = CommunicationEventType.objects.get(code='ORDER_PLACED')
            logger.info(f"Found ORDER_PLACED communication event type: {event_type.name}")
        except CommunicationEventType.DoesNotExist:
            logger.error("ORDER_PLACED communication event type not found")
            return
        
        # Create the context for email templates
        context = {
            'order': order,
            'user': user or order.user,
        }
        
        logger.info(f"Sending order confirmation email to {order.email}")
        
        # Generate the email messages from templates
        messages = event_type.get_messages(context)
        
        if messages['subject'] and (messages['body'] or messages['html']):
            # Send email using Oscar's communication dispatcher
            dispatcher = Dispatcher()
            result = dispatcher.dispatch_user_messages(order.user, messages)
            
            if result:
                logger.info(f"Order confirmation email sent successfully to {order.email}")
            else:
                logger.warning(f"Failed to send order confirmation email to {order.email}")
        else:
            logger.warning(f"No valid email content generated for order {order.number}")
            
    except Exception as e:
        logger.error(f"Error sending order confirmation email for order {order.number}: {e}")
        # Don't raise the exception to avoid breaking the checkout process
