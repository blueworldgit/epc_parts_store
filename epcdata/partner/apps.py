import oscar.apps.partner.apps as apps


class PartnerConfig(apps.PartnerConfig):
    name = 'partner'
    label = 'partner'  # Use the same label as Oscar's partner
    
    def ready(self):
        super().ready()
        # Import any signal handlers or additional setup here
        pass
