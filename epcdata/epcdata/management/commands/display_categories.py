from django.core.management.base import BaseCommand
from oscar.apps.catalogue.models import Category
from django.db import transaction


class Command(BaseCommand):
    help = 'Display current category structure and optionally sync with vanparts-direct'

    def add_arguments(self, parser):
        parser.add_argument(
            '--display-only',
            action='store_true',
            help='Only display current categories without making changes',
        )

    def handle(self, *args, **options):
        self.stdout.write('Current category structure:')
        self.stdout.write('=' * 50)
        
        # Display current categories
        root_categories = Category.objects.filter(depth=1)
        
        if not root_categories.exists():
            self.stdout.write(self.style.WARNING('No categories found in database'))
            return
            
        for category in root_categories:
            self.display_category_tree(category, indent=0)
            
        self.stdout.write(f'\nTotal categories: {Category.objects.count()}')
        
        if options['display_only']:
            return
            
        # If you want to add specific categories that match vanparts-direct structure
        self.stdout.write('\nTo sync with vanparts-direct categories, you would need to:')
        self.stdout.write('1. Export categories from vanparts-direct database')
        self.stdout.write('2. Import them here with proper hierarchy')
        self.stdout.write('3. Use Category.add_child() for nested structure')

    def display_category_tree(self, category, indent=0):
        """Display category and its children recursively"""
        prefix = '  ' * indent
        product_count = category.get_num_products()
        
        self.stdout.write(f'{prefix}- {category.name} ({product_count} products)')
        
        # Display children
        for child in category.get_children():
            self.display_category_tree(child, indent + 1)
