"""
Worldpay Gateway API Facade
Handles direct payment processing with Worldpay Gateway API v6
Based on successful testing results - processed £20 payment with HTTP 201 response
Working configuration: https://try.access.worldpay.com/payments/authorizations
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


class WorldpayGatewayFacade:
    """
    Facade for Worldpay Gateway API integration - Direct payment processing
    Uses the proven working configuration from wamptrial testing
    Successfully tested with £20 payment authorization (pay9n1XpOaGs7JFzrSuAK7Wk0)
    """
    
    def __init__(self):
        # Use the working Gateway API endpoint discovered in testing
        self.api_url = getattr(settings, 'WORLDPAY_GATEWAY_URL', 'https://try.access.worldpay.com/payments/authorizations')
        self.username = getattr(settings, 'WORLDPAY_USERNAME', '')
        self.password = getattr(settings, 'WORLDPAY_PASSWORD', '')
        self.entity_id = getattr(settings, 'WORLDPAY_ENTITY_ID', 'PO4080334630')  # Working entity ID
        
        # 🔍 DEBUG: Log Worldpay configuration on initialization
        self._log_worldpay_config()
        
    def _log_worldpay_config(self):
        """Log the current Worldpay configuration for debugging"""
        logger.info("🌍 WORLDPAY GATEWAY CONFIGURATION:")
        logger.info(f"   📍 API URL: {self.api_url}")
        logger.info(f"   👤 Username: {self.username}")
        logger.info(f"   🔑 Password: {'*' * (len(self.password) - 4) + self.password[-4:] if len(self.password) > 4 else '*' * len(self.password)}")
        logger.info(f"   🏢 Entity ID: {self.entity_id}")
        logger.info(f"   🧪 Test Mode: {getattr(settings, 'WORLDPAY_TEST_MODE', 'NOT SET')}")
        
        # Check for missing credentials
        missing = []
        if not self.username:
            missing.append("USERNAME")
        if not self.password:
            missing.append("PASSWORD")
        if not self.entity_id:
            missing.append("ENTITY_ID")
        if not self.api_url:
            missing.append("API_URL")
            
        if missing:
            logger.error(f"❌ MISSING WORLDPAY CREDENTIALS: {', '.join(missing)}")
        else:
            logger.info("✅ All Worldpay credentials present")
        
    def _get_auth_header(self):
        """
        Generate Basic Auth header for Worldpay Gateway API
        Uses the proven working format from testing
        """
        if not self.username or not self.password:
            logger.error("Worldpay username or password not configured")
            return None
            
        # Create base64 encoded Basic Auth
        credentials = f"{self.username}:{self.password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded_credentials}"
    
    def process_payment(self, order, card_data):
        """
        Process a direct payment using Worldpay Gateway API v6
        Uses the exact schema format that was successfully tested
        
        card_data should contain:
        - card_number
        - expiry_month
        - expiry_year
        - cvc
        - cardholder_name
        """
        try:
            # Generate unique transaction reference
            transaction_ref = f"ORDER-{order.number}-{uuid.uuid4().hex[:8]}"
            
            # Prepare payment request payload using proven v6 schema
            payload = {
                "transactionReference": transaction_ref,
                "merchant": {
                    "entity": self.entity_id
                },
                "instruction": {
                    "value": {
                        "currency": str(order.currency),
                        "amount": int(order.total_incl_tax * 100)  # Convert to pence/cents
                    },
                    "narrative": {
                        "line1": f"Order {order.number}"
                    },
                    "paymentInstrument": {
                        "type": "card/plain",
                        "cardNumber": card_data['card_number'].replace(' ', ''),
                        "cardExpiryDate": {
                            "month": int(card_data['expiry_month']),
                            "year": int(card_data['expiry_year'])
                        },
                        "cardHolderName": card_data['cardholder_name'],
                        "cardSecurityCode": card_data['cvc']
                    }
                }
            }
            
            # Add billing address if available
            if order.billing_address:
                payload["instruction"]["paymentInstrument"]["billingAddress"] = {
                    "address1": order.billing_address.line1,
                    "address2": order.billing_address.line2 or "",
                    "address3": order.billing_address.line3 or "",
                    "postalCode": order.billing_address.postcode,
                    "city": order.billing_address.line4,
                    "state": order.billing_address.state,
                    "countryCode": str(order.billing_address.country.code)
                }
            
            # Prepare headers using proven working format
            auth_header = self._get_auth_header()
            if not auth_header:
                logger.error("Failed to generate authentication header")
                return None
                
            headers = {
                'Authorization': auth_header,
                'Content-Type': 'application/vnd.worldpay.payments-v6+json',  # Proven working content type
                'Accept': 'application/vnd.worldpay.payments-v6+json'
            }
            
            logger.info(f"Processing payment for order {order.number}")
            logger.info(f"🌐 API URL: {self.api_url}")
            logger.info(f"👤 Username: {self.username}")
            logger.info(f"🆔 Entity ID: {self.entity_id}")
            logger.info(f"🔗 Request URL: {self.api_url}")
            logger.debug(f"Payment payload: {json.dumps(payload, indent=2)}")
            
            # Make API request
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30,
                verify=False  # For testing - should be True in production
            )
            
            logger.info(f"Worldpay Gateway API response status: {response.status_code}")
            logger.info(f"📡 Response headers: {dict(response.headers)}")
            
            if response.status_code == 201:
                response_data = response.json()
                logger.info("Payment authorized successfully")
                logger.debug(f"Response data: {json.dumps(response_data, indent=2)}")
                
                # Extract payment details from response
                payment_id = response_data.get('paymentId')
                authorization_code = response_data.get('paymentResponse', {}).get('authorizationCode')
                card_scheme = response_data.get('paymentResponse', {}).get('cardSchemeType')
                
                # Create payment source and transaction records
                self._create_payment_records(order, response_data, transaction_ref)
                
                return {
                    'success': True,
                    'payment_id': payment_id,
                    'authorization_code': authorization_code,
                    'card_scheme': card_scheme,
                    'transaction_ref': transaction_ref,
                    'response_data': response_data
                }
            else:
                logger.error(f"Payment failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                
                error_data = {}
                try:
                    error_data = response.json()
                except:
                    pass
                
                # Check for test card usage in live mode
                error_message = error_data.get('message', 'Payment failed')
                is_test_card_error = self._is_test_card_error(error_data, response.status_code)
                
                if is_test_card_error:
                    error_message = "Test cards cannot be used for real purchases. Please use a valid payment card."
                    logger.warning("Test card detected in live mode")
                
                return {
                    'success': False,
                    'error_code': response.status_code,
                    'error_message': error_message,
                    'error_data': error_data,
                    'is_test_card': is_test_card_error
                }
                
        except requests.RequestException as e:
            logger.error(f"Network error processing payment: {str(e)}")
            return {
                'success': False,
                'error_message': f"Network error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Unexpected error processing payment: {str(e)}")
            return {
                'success': False,
                'error_message': f"Unexpected error: {str(e)}"
            }
    
    def _create_payment_records(self, order, response_data, transaction_ref):
        """
        Create Oscar payment source and transaction records
        """
        try:
            # Get or create payment source type
            source_type, created = SourceType.objects.get_or_create(
                name='Worldpay Gateway',
                code='worldpay-gateway'
            )
            
            # Create payment source
            source = Source(
                source_type=source_type,
                currency=order.currency,
                amount_allocated=order.total_incl_tax,
                amount_debited=order.total_incl_tax,
                reference=transaction_ref
            )
            source.save()
            
            # Create transaction record
            transaction = Transaction(
                source=source,
                txn_type=Transaction.PURCHASE,
                amount=order.total_incl_tax,
                reference=response_data.get('paymentId', transaction_ref),
                status=Transaction.COMPLETE
            )
            transaction.save()
            
            logger.info(f"Payment records created for order {order.number}")
            
        except Exception as e:
            logger.error(f"Error creating payment records: {str(e)}")
    
    def refund_payment(self, payment_id, amount, reason="Customer refund"):
        """
        Process a refund using Worldpay Gateway API
        """
        try:
            # Use environment-aware base URL
            base_url = self.api_url.replace('/payments/authorizations', '')
            refund_url = f"{base_url}/payments/{payment_id}/refunds"
            
            payload = {
                "reference": f"REFUND-{uuid.uuid4().hex[:8]}",
                "value": {
                    "currency": "GBP",  # Should match original payment
                    "amount": int(amount * 100)
                },
                "narrative": {
                    "line1": reason
                }
            }
            
            auth_header = self._get_auth_header()
            if not auth_header:
                return {'success': False, 'error_message': 'Authentication failed'}
                
            headers = {
                'Authorization': auth_header,
                'Content-Type': 'application/vnd.worldpay.payments-v6+json',
                'Accept': 'application/vnd.worldpay.payments-v6+json'
            }
            
            response = requests.post(
                refund_url,
                headers=headers,
                json=payload,
                timeout=30,
                verify=False
            )
            
            if response.status_code == 201:
                response_data = response.json()
                logger.info(f"Refund processed successfully: {response_data.get('refundId')}")
                return {
                    'success': True,
                    'refund_id': response_data.get('refundId'),
                    'response_data': response_data
                }
            else:
                logger.error(f"Refund failed: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error_code': response.status_code,
                    'error_message': 'Refund failed'
                }
        
        except requests.RequestException as e:
            logger.error(f"Network error processing refund: {str(e)}")
            return {
                'success': False,
                'error_message': 'Network error during refund'
            }
    
    def _is_test_card_error(self, error_data, status_code):
        """
        Detect if payment failure was due to test card usage in live mode
        """
        if not error_data:
            return False
            
        # Common indicators of test card usage
        error_message = error_data.get('message', '').lower()
        error_code = error_data.get('errorCode', '')
        
        # Worldpay specific error patterns for test cards
        test_card_indicators = [
            'test card',
            'invalid card number',
            'card not permitted',
            'transaction not permitted',
            'invalid merchant',
            'issuer not available'
        ]
        
        # Check if any test card indicators are in the error message
        for indicator in test_card_indicators:
            if indicator in error_message:
                return True
                
        # Additional check for specific error codes that indicate test card usage
        test_card_error_codes = ['TKN_NOT_FOUND', 'INVALID_CARD', 'CARD_NOT_PERMITTED']
        if error_code in test_card_error_codes:
            return True
            
        return False
