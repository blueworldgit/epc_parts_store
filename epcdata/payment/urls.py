from django.urls import path
from . import views
from .debug_views import PaymentDebugView
from .gateway_views import (
    WorldpayGatewayRedirectView, 
    WorldpayGatewayCardFormView,
    WorldpayGatewaySuccessView,
    WorldpayGatewayFailureView,
    WorldpayDebugConfigView
)
from .debug_gateway import PaymentSessionDebugView, PaymentTestOrderCreationView
from .debug_checkout import CheckoutDebugView, PaymentMethodTestView
from .simple_test import SimpleGatewayTestView
from .checkout_session_view import process_checkout_session_payment
from django.views.generic import TemplateView

app_name = 'payment'

urlpatterns = [
    # Original hosted payment URLs (for backwards compatibility)
    path('worldpay/redirect/', views.WorldpayRedirectView.as_view(), name='worldpay-redirect'),
    path('worldpay/callback/', views.WorldpayCallbackView.as_view(), name='worldpay-callback'),
    path('worldpay/success/', views.WorldpaySuccessView.as_view(), name='worldpay-success'),
    path('worldpay/failure/', views.WorldpayFailureView.as_view(), name='worldpay-failure'),
    path('worldpay/cancel/', views.WorldpayCancelView.as_view(), name='worldpay-cancel'),
    
    # New Gateway API URLs (direct payment processing)
    path('gateway/redirect/', WorldpayGatewayRedirectView.as_view(), name='worldpay-gateway-redirect'),
    path('gateway/card-form/', WorldpayGatewayCardFormView.as_view(), name='worldpay-gateway-card-form'),
    path('gateway/success/', WorldpayGatewaySuccessView.as_view(), name='worldpay-gateway-success'),
    path('gateway/failure/', WorldpayGatewayFailureView.as_view(), name='worldpay-gateway-failure'),
    
    # Access Checkout Session payment endpoint
    path('checkout-session/', process_checkout_session_payment, name='checkout-session-payment'),
    path('test-checkout/', TemplateView.as_view(template_name='payment/test_checkout.html'), name='test-checkout'),
    path('test-checkout-debug/', TemplateView.as_view(template_name='payment/test_checkout_debug.html'), name='test-checkout-debug'),
    
    # Debug URLs
    path('debug/', PaymentDebugView.as_view(), name='debug'),
    path('debug/session/', PaymentSessionDebugView.as_view(), name='debug-session'),
    path('debug/test-order/', PaymentTestOrderCreationView.as_view(), name='debug-test-order'),
    path('debug/checkout/', CheckoutDebugView.as_view(), name='debug-checkout'),
    path('debug/payment-form/', PaymentMethodTestView.as_view(), name='debug-payment-form'),
    path('debug/config/', WorldpayDebugConfigView.as_view(), name='debug-config'),
    path('test/', SimpleGatewayTestView.as_view(), name='simple-test'),
]
