from django.core.management.base import BaseCommand
from motorpartsdata.models import ShippingMethod
from django_countries import countries


class Command(BaseCommand):
    help = 'Create initial shipping methods for common countries'

    def handle(self, *args, **options):
        self.stdout.write('Creating initial shipping methods...')

        # UK Domestic Shipping
        uk_standard, created = ShippingMethod.objects.get_or_create(
            name='UK Standard Delivery',
            defaults={
                'description': 'Standard delivery within the UK',
                'countries': ['GB'],
                'price': 4.99,
                'estimated_days_min': 2,
                'estimated_days_max': 3,
                'is_active': True
            }
        )
        if created:
            self.stdout.write(f'✓ Created: {uk_standard.name}')

        # UK Express Shipping
        uk_express, created = ShippingMethod.objects.get_or_create(
            name='UK Express Delivery',
            defaults={
                'description': 'Next day delivery within the UK',
                'countries': ['GB'],
                'price': 9.99,
                'estimated_days_min': 1,
                'estimated_days_max': 1,
                'is_active': True
            }
        )
        if created:
            self.stdout.write(f'✓ Created: {uk_express.name}')

        # European Union Standard
        eu_countries = ['AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR', 
                       'DE', 'GR', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL', 
                       'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE']
        
        eu_standard, created = ShippingMethod.objects.get_or_create(
            name='EU Standard Delivery',
            defaults={
                'description': 'Standard delivery to European Union countries',
                'countries': eu_countries,
                'price': 12.99,
                'estimated_days_min': 5,
                'estimated_days_max': 10,
                'is_active': True
            }
        )
        if created:
            self.stdout.write(f'✓ Created: {eu_standard.name}')

        # International Standard
        international_countries = ['US', 'CA', 'AU', 'NZ', 'JP', 'NO', 'CH']
        
        international_standard, created = ShippingMethod.objects.get_or_create(
            name='International Standard',
            defaults={
                'description': 'Standard international delivery',
                'countries': international_countries,
                'price': 19.99,
                'estimated_days_min': 7,
                'estimated_days_max': 14,
                'is_active': True
            }
        )
        if created:
            self.stdout.write(f'✓ Created: {international_standard.name}')

        self.stdout.write(
            self.style.SUCCESS('Successfully created initial shipping methods!')
        )
        self.stdout.write('You can now manage these in the Django admin panel.')
