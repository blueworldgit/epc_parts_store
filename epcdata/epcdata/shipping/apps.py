from django.apps import AppConfig


class ShippingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'epcdata.shipping'
    verbose_name = 'Weight-Based Shipping'
