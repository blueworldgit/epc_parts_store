from django.apps import AppConfig

class EpcdataConfig(AppConfig):
    name = 'epcdata'
    default_auto_field = 'django.db.models.BigAutoField'
    
    def ready(self):
        """
        Import signals when Django starts up
        """
        try:
            import epcdata.order_emails  # Import the signals module
        except ImportError:
            pass
