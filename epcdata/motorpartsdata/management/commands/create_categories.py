from django.core.management.base import BaseCommand
from oscar.apps.catalogue.models import Category
from motorpartsdata.models import SerialNumber, ParentTitle, ChildTitle

class Command(BaseCommand):
    help = 'Create Oscar categories from your model structure'

    def handle(self, *args, **options):
        self.stdout.write("🏗️ Creating Oscar Categories from Motor Parts Data")
        self.stdout.write("=" * 50)
        
        created_count = 0
        
        # Check current data
        serial_count = SerialNumber.objects.count()
        parent_count = ParentTitle.objects.count()
        child_count = ChildTitle.objects.count()
        current_categories = Category.objects.count()
        
        self.stdout.write(f"📊 Data Summary:")
        self.stdout.write(f"   Serial Numbers: {serial_count}")
        self.stdout.write(f"   Parent Titles: {parent_count}")
        self.stdout.write(f"   Child Titles: {child_count}")
        self.stdout.write(f"   Current Categories: {current_categories}")
        self.stdout.write("")
        
        if serial_count == 0:
            self.stdout.write(self.style.WARNING("No data found to create categories from!"))
            return
        
        # Create categories as root categories (no tree structure for now)
        
        # Create categories for SerialNumbers
        for serial in SerialNumber.objects.all()[:3]:  # Limit to first 3 for testing
            category_name = f"Serial: {serial.serial}"
            if not Category.objects.filter(name=category_name).exists():
                serial_category = Category.add_root(
                    name=category_name,
                    description=f'Parts for serial number {serial.serial}',
                    slug=f'serial-{serial.serial}',
                )
                self.stdout.write(f"📁 Created Serial Category: {serial_category.name}")
                created_count += 1
        
        # Create categories for ParentTitles
        for parent in ParentTitle.objects.all()[:10]:  # Limit to first 10
            category_name = f"Parent: {parent.title}"
            if not Category.objects.filter(name=category_name).exists():
                parent_category = Category.add_root(
                    name=category_name,
                    description=f'Parent category: {parent.title}',
                    slug=f'parent-{parent.id}',
                )
                self.stdout.write(f"📂 Created Parent Category: {parent_category.name}")
                created_count += 1
        
        # Create categories for ChildTitles
        for child in ChildTitle.objects.all()[:15]:  # Limit to first 15
            category_name = f"Child: {child.title}"
            if not Category.objects.filter(name=category_name).exists():
                child_category = Category.add_root(
                    name=category_name,
                    description=f'Child category: {child.title}',
                    slug=f'child-{child.id}',
                )
                self.stdout.write(f"📄 Created Child Category: {child_category.name}")
                created_count += 1
        
        self.stdout.write("=" * 50)
        self.stdout.write(self.style.SUCCESS(f"✅ Created {created_count} new categories"))
        self.stdout.write(f"📊 Total categories: {Category.objects.count()}")
        
        # Show category tree structure
        self.stdout.write("\n🌳 Category Tree Structure:")
        for root_cat in Category.objects.filter(depth=1)[:10]:  # Show first 10
            self.stdout.write(f"└── {root_cat.name}")
            for child_cat in root_cat.get_children()[:3]:  # Show first 3 children
                self.stdout.write(f"    └── {child_cat.name}")
                for grandchild_cat in child_cat.get_children()[:2]:  # Show first 2 grandchildren
                    self.stdout.write(f"        └── {grandchild_cat.name}")
        
        self.stdout.write(f"\n🎉 You can now view categories at: http://127.0.0.1:8000/dashboard/catalogue/categories/")
