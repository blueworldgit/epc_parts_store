"""
Worldpay Hosted Payment Pages Facade
Handles API communication with Worldpay for hosted payment sessions
"""
import json
import uuid
import requests
import logging
import base64
from decimal import Decimal
from django.conf import settings
from django.urls import reverse
from oscar.core.loading import get_model

logger = logging.getLogger(__name__)

Order = get_model('order', 'Order')
Source = get_model('payment', 'Source')
SourceType = get_model('payment', 'SourceType')
Transaction = get_model('payment', 'Transaction')


class WorldpayHostedFacade:
    """
    Facade for Worldpay Hosted Payment Pages API integration
    """
    
    def __init__(self):
        self.api_url = getattr(settings, 'WORLDPAY_API_URL', 'https://try.access.worldpay.com/payment-pages/v1/sessions')
        self.username = getattr(settings, 'WORLDPAY_USERNAME', '')
        self.password = getattr(settings, 'WORLDPAY_PASSWORD', '')
        self.entity_id = getattr(settings, 'WORLDPAY_ENTITY_ID', '')
        
    def _get_auth_header(self):
        """
        Generate Basic Auth header for Worldpay API
        """
        if not self.username or not self.password:
            logger.error("Worldpay username or password not configured")
            return None
            
        # Create base64 encoded Basic Auth
        credentials = f"{self.username}:{self.password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded_credentials}"
        
    def create_payment_session(self, order, request):
        """
        Create a hosted payment session with Worldpay
        Returns the payment session URL or None if failed
        """
        try:
            # Generate unique transaction reference
            transaction_ref = f"ORDER-{order.number}-{uuid.uuid4().hex[:8]}"
            
            # Build absolute URLs for callbacks
            base_url = request.build_absolute_uri('/')[:-1]  # Remove trailing slash
            success_url = f"{base_url}{reverse('payment:worldpay-success')}"
            failure_url = f"{base_url}{reverse('payment:worldpay-failure')}"
            cancel_url = f"{base_url}{reverse('payment:worldpay-cancel')}"
            
            # Prepare payment request payload
            payload = {
                "amount": int(order.total_incl_tax * 100),  # Convert to pence/cents
                "currency": str(order.currency),
                "description": f"Order {order.number}",
                "customer": {
                    "email": order.email if order.email else "guest@example.com"
                },
                "success_url": success_url,
                "failure_url": failure_url,
                "cancel_url": cancel_url
            }
            
            # Add customer name if available
            if order.billing_address:
                payload["customer"]["first_name"] = order.billing_address.first_name
                payload["customer"]["last_name"] = order.billing_address.last_name
            
            # Prepare headers according to Worldpay API specification
            auth_header = self._get_auth_header()
            if not auth_header:
                logger.error("Failed to generate authentication header")
                return None
                
            headers = {
                'Authorization': auth_header,
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            logger.info(f"Creating Worldpay payment session for order {order.number}")
            logger.debug(f"Payment payload: {json.dumps(payload, indent=2)}")
            
            # Make API request
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            logger.info(f"Worldpay API response status: {response.status_code}")
            
            if response.status_code == 201:
                response_data = response.json()
                logger.info("Payment session created successfully")
                logger.debug(f"Response data: {json.dumps(response_data, indent=2)}")
                
                # Store transaction reference in session for callback handling
                request.session['worldpay_transaction_ref'] = transaction_ref
                request.session['worldpay_order_number'] = order.number
                
                # Return the payment page URL - check different possible field names
                payment_url = (
                    response_data.get('url') or 
                    response_data.get('payment_url') or
                    response_data.get('_links', {}).get('payment', {}).get('href') or
                    response_data.get('_links', {}).get('redirect', {}).get('href')
                )
                
                if payment_url:
                    logger.info(f"Payment URL: {payment_url}")
                    return payment_url
                else:
                    logger.error("No payment URL found in response")
                    logger.error(f"Response data: {response_data}")
                    return None
            else:
                logger.error(f"Failed to create payment session: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Network error creating payment session: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error creating payment session: {str(e)}")
            return None
    
    def handle_payment_callback(self, request, status='success'):
        """
        Handle payment callback from Worldpay
        """
        try:
            transaction_ref = request.session.get('worldpay_transaction_ref')
            order_number = request.session.get('worldpay_order_number')
            
            if not transaction_ref or not order_number:
                logger.error("Missing transaction reference or order number in session")
                return None
            
            # Get the order
            try:
                order = Order.objects.get(number=order_number)
            except Order.DoesNotExist:
                logger.error(f"Order {order_number} not found")
                return None
            
            # Get or create payment source
            source_type, created = SourceType.objects.get_or_create(
                name='Worldpay Hosted',
                code='worldpay-hosted'
            )
            
            source = Source(
                source_type=source_type,
                currency=order.currency,
                amount_allocated=order.total_incl_tax,
                amount_debited=order.total_incl_tax if status == 'success' else Decimal('0.00'),
                reference=transaction_ref
            )
            source.save()
            
            # Create transaction record
            transaction = Transaction(
                source=source,
                txn_type=Transaction.PURCHASE if status == 'success' else Transaction.REFUND,
                amount=order.total_incl_tax,
                reference=transaction_ref,
                status=Transaction.COMPLETE if status == 'success' else Transaction.FAILED
            )
            transaction.save()
            
            # Clear session data
            request.session.pop('worldpay_transaction_ref', None)
            request.session.pop('worldpay_order_number', None)
            
            logger.info(f"Payment {status} processed for order {order.number}")
            
            return order
            
        except Exception as e:
            logger.error(f"Error handling payment callback: {str(e)}")
            return None
