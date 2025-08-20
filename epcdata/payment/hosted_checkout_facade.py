import logging
import hashlib
import hmac
from decimal import Decimal
from datetime import datetime
from django.conf import settings
from django.urls import reverse
from oscar.core.loading import get_model

Source = get_model('payment', 'Source')
SourceType = get_model('payment', 'SourceType')

logger = logging.getLogger(__name__)


class WorldpayHostedCheckoutFacade:
    """
    Facade for interacting with Worldpay Hosted Payment Pages (HPP)
    This is much simpler than Access Checkout and doesn't require HTTPS for development.
    """
    
    @staticmethod
    def get_hosted_payment_url():
        """Get the URL for Worldpay Hosted Payment Pages"""
        if getattr(settings, 'WORLDPAY_TEST_MODE', True):
            return 'https://secure-test.worldpay.com/wcc/purchase'
        else:
            return 'https://secure.worldpay.com/wcc/purchase'
    
    @staticmethod
    def get_installation_id():
        """Get the Worldpay installation ID"""
        return getattr(settings, 'WORLDPAY_INSTALLATION_ID', '')
    
    @staticmethod
    def get_md5_secret():
        """Get the MD5 secret for signature generation"""
        return getattr(settings, 'WORLDPAY_MD5_SECRET', '')
    
    @staticmethod
    def generate_signature(order_data):
        """
        Generate MD5 signature for Worldpay hosted checkout
        """
        secret = WorldpayHostedCheckoutFacade.get_md5_secret()
        if not secret:
            return None
            
        # Create signature string based on Worldpay requirements
        signature_string = (
            f"{secret}:"
            f"{order_data['instId']}:"
            f"{order_data['amount']}:"
            f"{order_data['currency']}:"
            f"{order_data['cartId']}"
        )
        
        return hashlib.md5(signature_string.encode('utf-8')).hexdigest()
    
    @staticmethod
    def create_hosted_payment_data(order_total, order_number, request):
        """
        Create the data required for Worldpay hosted checkout
        """
        installation_id = WorldpayHostedCheckoutFacade.get_installation_id()
        
        # Convert order total to pence (Worldpay expects amount in smallest currency unit)
        amount_in_pence = int(order_total * 100)
        
        # Create the payment data
        payment_data = {
            'instId': installation_id,
            'cartId': order_number,
            'amount': str(amount_in_pence),
            'currency': 'GBP',
            'desc': f'Order {order_number}',
            'MC_callback': request.build_absolute_uri(reverse('worldpay-hosted-callback')),
            'MC_success_url': request.build_absolute_uri(reverse('worldpay-hosted-success')),
            'MC_failure_url': request.build_absolute_uri(reverse('worldpay-hosted-failure')),
            'testMode': '100' if getattr(settings, 'WORLDPAY_TEST_MODE', True) else '0',
        }
        
        # Add signature if MD5 secret is configured
        signature = WorldpayHostedCheckoutFacade.generate_signature(payment_data)
        if signature:
            payment_data['signature'] = signature
        
        return payment_data
    
    @staticmethod
    def verify_callback_signature(post_data):
        """
        Verify the signature in the callback from Worldpay
        """
        secret = WorldpayHostedCheckoutFacade.get_md5_secret()
        if not secret:
            return True  # Skip verification if no secret configured
            
        received_signature = post_data.get('signature', '')
        
        # Create signature string for verification
        signature_string = (
            f"{secret}:"
            f"{post_data.get('callbackPW', '')}:"
            f"{post_data.get('instId', '')}:"
            f"{post_data.get('compName', '')}:"
            f"{post_data.get('cartId', '')}:"
            f"{post_data.get('amount', '')}:"
            f"{post_data.get('currency', '')}:"
            f"{post_data.get('transId', '')}:"
            f"{post_data.get('transStatus', '')}:"
            f"{post_data.get('transTime', '')}:"
            f"{post_data.get('authAmount', '')}:"
            f"{post_data.get('authCurrency', '')}:"
            f"{post_data.get('authAmountString', '')}:"
            f"{post_data.get('rawAuthMessage', '')}:"
            f"{post_data.get('rawAuthCode', '')}"
        )
        
        calculated_signature = hashlib.md5(signature_string.encode('utf-8')).hexdigest()
        
        return calculated_signature.lower() == received_signature.lower()
    
    @staticmethod
    def process_callback_data(post_data):
        """
        Process the callback data from Worldpay
        """
        try:
            transaction_status = post_data.get('transStatus', '')
            transaction_id = post_data.get('transId', '')
            order_number = post_data.get('cartId', '')
            amount = post_data.get('amount', '')
            currency = post_data.get('currency', '')
            
            # Verify signature
            if not WorldpayHostedCheckoutFacade.verify_callback_signature(post_data):
                logger.error(f"Invalid signature for order {order_number}")
                return False, "Invalid signature"
            
            # Check transaction status
            if transaction_status == 'Y':
                # Payment successful
                logger.info(f"Payment successful for order {order_number}, transaction ID: {transaction_id}")
                return True, {
                    'transaction_id': transaction_id,
                    'order_number': order_number,
                    'amount': amount,
                    'currency': currency,
                    'status': 'success'
                }
            else:
                # Payment failed
                logger.warning(f"Payment failed for order {order_number}, status: {transaction_status}")
                return False, f"Payment failed with status: {transaction_status}"
                
        except Exception as e:
            logger.error(f"Error processing callback data: {str(e)}")
            return False, f"Error processing payment: {str(e)}"
