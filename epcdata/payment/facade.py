import hashlib
import hmac
from decimal import Decimal
from django.conf import settings
from django.urls import reverse
from oscar.core.loading import get_model

Source = get_model('payment', 'Source')
SourceType = get_model('payment', 'SourceType')


class Facade:
    """
    Facade for interacting with Worldpay Hosted Payment Page
    """
    
    @staticmethod
    def get_redirect_url():
        """
        Get the Worldpay redirect URL
        """
        if getattr(settings, 'WORLDPAY_TEST_MODE', True):
            return 'https://secure-test.worldpay.com/wcc/purchase'
        else:
            return 'https://secure.worldpay.com/wcc/purchase'
    
    @staticmethod
    def get_form_data(order_number, amount, currency, user, request):
        """
        Generate form data for Worldpay redirect
        """
        # Basic required fields
        data = {
            'instId': settings.WORLDPAY_INSTALLATION_ID,
            'cartId': order_number,
            'amount': str(amount),
            'currency': currency,
            'desc': f'Order {order_number}',
            'testMode': '100' if getattr(settings, 'WORLDPAY_TEST_MODE', True) else '0',
        }
        
        # Add callback URLs
        data.update({
            'MC_callback': request.build_absolute_uri(reverse('worldpay-callback')),
            'successURL': request.build_absolute_uri(reverse('checkout:thank-you')),
            'cancelURL': request.build_absolute_uri(reverse('checkout:payment-details')),
            'failureURL': request.build_absolute_uri(reverse('checkout:payment-details')),
        })
        
        # Add customer information if available
        if user and user.is_authenticated:
            data['email'] = user.email
            if hasattr(user, 'first_name') and user.first_name:
                data['name'] = f"{user.first_name} {user.last_name}".strip()
        
        # Add signature if secret key is configured
        if hasattr(settings, 'WORLDPAY_SECRET_KEY'):
            signature_string = f"{data['instId']}:{data['cartId']}:{data['amount']}:{data['currency']}"
            signature = hmac.new(
                settings.WORLDPAY_SECRET_KEY.encode('utf-8'),
                signature_string.encode('utf-8'),
                hashlib.md5
            ).hexdigest()
            data['signature'] = signature
        
        return data
    
    @staticmethod
    def create_payment_source(order, payment_ref, amount):
        """
        Create a payment source for the successful payment
        """
        source_type, _ = SourceType.objects.get_or_create(
            name='Worldpay',
            code='worldpay'
        )
        
        source = Source(
            source_type=source_type,
            currency=order.currency,
            amount_allocated=Decimal(str(amount)),
            amount_debited=Decimal(str(amount)),
            reference=payment_ref,
            label=f'Worldpay payment ({payment_ref})'
        )
        source.save()
        return source
    
    @staticmethod
    def verify_callback_signature(params):
        """
        Verify the signature from Worldpay callback
        """
        if not hasattr(settings, 'WORLDPAY_SECRET_KEY'):
            return True  # Skip verification if no secret key
        
        received_signature = params.get('signature', '')
        callback_pw = params.get('callbackPW', '')
        
        # Create signature string
        signature_string = f"{callback_pw}:{params.get('instId')}:{params.get('cartId')}:{params.get('amount')}:{params.get('currency')}"
        
        expected_signature = hmac.new(
            settings.WORLDPAY_SECRET_KEY.encode('utf-8'),
            signature_string.encode('utf-8'),
            hashlib.md5
        ).hexdigest()
        
        return hmac.compare_digest(received_signature, expected_signature)
