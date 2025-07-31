from django.core.management.base import BaseCommand
from oscar.apps.address.models import Country


class Command(BaseCommand):
    help = 'Populate countries for Oscar'

    def handle(self, *args, **options):
        countries_data = [
            ('US', 'United States'),
            ('GB', 'United Kingdom'), 
            ('CA', 'Canada'),
            ('AU', 'Australia'),
            ('DE', 'Germany'),
            ('FR', 'France'),
            ('IT', 'Italy'),
            ('ES', 'Spain'),
            ('NL', 'Netherlands'),
            ('BE', 'Belgium'),
            ('IE', 'Ireland'),
            ('CH', 'Switzerland'),
            ('AT', 'Austria'),
            ('SE', 'Sweden'),
            ('NO', 'Norway'),
            ('DK', 'Denmark'),
            ('FI', 'Finland'),
        ]

        self.stdout.write(f'Current countries: {Country.objects.count()}')
        
        for code, name in countries_data:
            country, created = Country.objects.get_or_create(
                iso_3166_1_a2=code,
                defaults={'name': name, 'printable_name': name}
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created country: {code} - {name}')
                )
            else:
                self.stdout.write(f'Country already exists: {code} - {name}')

        self.stdout.write(f'Final countries count: {Country.objects.count()}')
