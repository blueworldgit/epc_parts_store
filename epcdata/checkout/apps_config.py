from django.apps import AppConfig
from oscar.apps.checkout.apps import CheckoutConfig as CoreCheckoutConfig


class CheckoutConfig(CoreCheckoutConfig):
    name = 'checkout'
    verbose_name = 'Checkout'
