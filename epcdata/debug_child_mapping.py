import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from motorpartsdata.models import SerialNumber, ParentTitle, ChildTitle, Part
from oscar.apps.catalogue.models import Category

print('🔍 Debugging child_title.id mapping for LSFAL11A4PA157987...')

serial = SerialNumber.objects.filter(serial='LSFAL11A4PA157987').first()
if not serial:
    print('❌ Serial not found!')
else:
    print(f'✅ Found serial: {serial.serial}')
    
    # Get parent 12 (Charging & Energystorage)
    parent_12 = ParentTitle.objects.filter(serial_number=serial, title='Charging & Energystorage').first()
    if parent_12:
        print(f'\n📁 Parent 12: {parent_12.title} (ID: {parent_12.id})')
        
        # Get all child titles for this parent
        child_titles = ChildTitle.objects.filter(parent=parent_12).order_by('id')
        print(f'   Child titles found: {child_titles.count()}')
        
        for i, child_title in enumerate(child_titles, 1):
            print(f'   Child {i}: ID={child_title.id}, Title="{child_title.title}"')
            
            # Check if Oscar category exists for this child
            oscar_cat = Category.objects.filter(slug=f'serial-LSFAL11A4PA157987-parent-12-child-{i}').first()
            if oscar_cat:
                print(f'      ✅ Oscar category: {oscar_cat.slug}')
                products = oscar_cat.get_num_children()  # This counts child categories, not products
                # Let's count actual products
                from oscar.apps.catalogue.models import Product
                actual_products = Product.objects.filter(categories=oscar_cat).count()
                print(f'      📦 Products: {actual_products}')
            else:
                print(f'      ❌ No Oscar category found')
            
            # Check what parts exist for this child_title
            parts = Part.objects.filter(child_title=child_title, oscar_imported=True)
            print(f'      🔧 Parts in database: {parts.count()}')
            
            if parts.exists():
                sample_part = parts.first()
                print(f'         Sample: {sample_part.part_number} - {sample_part.usage_name}')
    
    print('\n🔍 Checking what the category mapping expects...')
    print('The import logic looks for:')
    for child_title in child_titles:
        lookup_key = f"child_{child_title.id}"
        print(f'   category_map["{lookup_key}"] for child_title.id={child_title.id}')
        
        # The import creates categories with these slugs
        expected_slug = f'serial-LSFAL11A4PA157987-parent-12-child-{child_titles.filter(id__lte=child_title.id).count()}'
        print(f'      Should map to slug: {expected_slug}')