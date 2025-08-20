"""
Debug view to check Worldpay configuration on server
Access this at: /debug/worldpay-config/
"""
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["GET"])
def worldpay_config_debug(request):
    """Debug endpoint to check Worldpay configuration"""
    
    # Get all Worldpay-related settings
    config = {}
    
    # Check for both old and new variable names
    worldpay_vars = [
        'WORLDPAY_TEST_MODE',
        'WORLDPAY_GATEWAY_URL',
        'WORLDPAY_GATEWAY_USERNAME', 
        'WORLDPAY_GATEWAY_PASSWORD',
        'WORLDPAY_GATEWAY_ENTITY_ID',
        'WORLDPAY_USERNAME',  # Old variable
        'WORLDPAY_PASSWORD',  # Old variable
        'WORLDPAY_ENTITY_ID', # Old variable
        'WORLDPAY_URL',       # Old variable
    ]
    
    for var in worldpay_vars:
        value = getattr(settings, var, 'NOT_SET')
        if 'PASSWORD' in var and value != 'NOT_SET':
            # Mask password but show last 4 characters
            config[var] = '*' * (len(str(value)) - 4) + str(value)[-4:] if len(str(value)) > 4 else '*' * len(str(value))
        else:
            config[var] = value
    
    # Check which credentials are actually being used
    from payment.gateway_facade import WorldpayGatewayFacade
    facade = WorldpayGatewayFacade()
    
    actual_config = {
        'api_url': facade.api_url,
        'username': facade.username,
        'password': '*' * (len(facade.password) - 4) + facade.password[-4:] if len(facade.password) > 4 else '*' * len(facade.password),
        'entity_id': facade.entity_id,
    }
    
    # Environment info
    env_info = {
        'DEBUG': getattr(settings, 'DEBUG', 'NOT_SET'),
        'ALLOWED_HOSTS': getattr(settings, 'ALLOWED_HOSTS', 'NOT_SET'),
    }
    
    response_data = {
        'timestamp': '2025-08-20',
        'status': 'success',
        'environment_variables': config,
        'actual_facade_config': actual_config,
        'environment_info': env_info,
        'missing_variables': [],
        'recommendations': []
    }
    
    # Check for missing critical variables
    critical_vars = ['WORLDPAY_GATEWAY_USERNAME', 'WORLDPAY_GATEWAY_PASSWORD', 'WORLDPAY_GATEWAY_ENTITY_ID']
    for var in critical_vars:
        if config.get(var) == 'NOT_SET':
            response_data['missing_variables'].append(var)
    
    # Add recommendations
    if response_data['missing_variables']:
        response_data['recommendations'].append('Add missing environment variables to .env.production')
    
    if actual_config['username'] == '':
        response_data['recommendations'].append('WORLDPAY_GATEWAY_USERNAME is empty - check .env.production file')
        
    if actual_config['password'] == '':
        response_data['recommendations'].append('WORLDPAY_GATEWAY_PASSWORD is empty - check .env.production file')
    
    logger.info(f"🔍 Worldpay config debug accessed: {actual_config}")
    
    return JsonResponse(response_data, json_dumps_params={'indent': 2})
