import oscar.apps.checkout.apps as apps


class CheckoutConfig(apps.CheckoutConfig):
    name = 'checkout'
    label = 'checkout'  # Use the same label as Oscar's checkout
    
    def ready(self):
        super().ready()
        # Import any signal handlers or additional setup here
        pass
