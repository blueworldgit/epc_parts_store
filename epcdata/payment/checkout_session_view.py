"""
Django view to process Access Checkout session payments
This handles the server-to-server API call to avoid CORS issues
"""
import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .gateway_facade import WorldpayGatewayFacade

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def process_checkout_session_payment(request):
    """
    Process a payment using an Access Checkout session
    
    Expected POST data:
    {
        "sessionHref": "https://access.worldpay.com/sessions/xxx",
        "amount": 52,
        "currency": "GBP",
        "transactionReference": "ORDER-123",
        "billingAddress": {
            "address1": "...",
            "city": "...",
            "postcode": "...",
            "countryCode": "GB"
        }
    }
    """
    try:
        data = json.loads(request.body)
        
        session_href = data.get('sessionHref')
        amount = data.get('amount')
        currency = data.get('currency', 'GBP')
        transaction_ref = data.get('transactionReference')
        billing_address = data.get('billingAddress', {})
        
        if not session_href:
            return JsonResponse({
                'success': False,
                'error': 'Missing sessionHref'
            }, status=400)
        
        if not amount:
            return JsonResponse({
                'success': False,
                'error': 'Missing amount'
            }, status=400)
        
        logger.info(f"Processing checkout session payment: {transaction_ref}, £{amount/100:.2f}")
        logger.info(f"Session: {session_href}")
        
        # Initialize facade
        facade = WorldpayGatewayFacade()
        
        # Build payment payload for Gateway API v6
        payload = {
            "transactionReference": transaction_ref,
            "merchant": {
                "entity": facade.entity_id
            },
            "instruction": {
                "narrative": {
                    "line1": "EPC Parts Store"
                },
                "value": {
                    "currency": currency,
                    "amount": amount
                },
                "paymentInstrument": {
                    "type": "card/checkout+session",
                    "sessionHref": session_href
                }
            }
        }
        
        # Add billing address if provided
        if billing_address:
            payload["instruction"]["paymentInstrument"]["billingAddress"] = {
                "address1": billing_address.get('address1', ''),
                "address2": billing_address.get('address2', ''),
                "address3": billing_address.get('address3', ''),
                "postalCode": billing_address.get('postcode', ''),
                "city": billing_address.get('city', ''),
                "state": billing_address.get('state', ''),
                "countryCode": billing_address.get('countryCode', 'GB')
            }
        
        # Make API request
        headers = {
            "Authorization": facade._get_auth_header(),
            "Content-Type": "application/vnd.worldpay.payments-v6+json",
            "Accept": "application/vnd.worldpay.payments-v6+json"
        }
        
        import requests
        response = requests.post(
            f"{facade.base_url}/payments/authorizations",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        result = response.json()
        logger.info(f"Payment response: {response.status_code}")
        logger.info(f"Payment outcome: {result.get('outcome')}")
        
        # Return result
        return JsonResponse({
            'success': response.status_code in [200, 201],
            'httpStatus': response.status_code,
            'outcome': result.get('outcome'),
            'paymentId': result.get('_links', {}).get('payments:authorize', {}).get('href', ''),
            'data': result
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON'
        }, status=400)
    except Exception as e:
        logger.exception("Error processing checkout session payment")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
