import oscar.apps.shipping.apps as apps


class ShippingConfig(apps.ShippingConfig):
    name = 'shipping'
    label = 'shipping'  # Use the same label as Oscar's shipping
    
    def ready(self):
        super().ready()
        # Import any signal handlers or additional setup here
        pass
